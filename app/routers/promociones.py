from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.promociones import (
    agregar_producto, listar_vigentes, promociones,
    promociones_de_producto, quitar_producto,
)
from app.dependencias import get_session
from app.routers.base import crear_router
from app.schemas.promociones import PromocionActualizar, PromocionCrear, PromocionSalida


def _extras(router):
    @router.get("/vigentes", response_model=list[PromocionSalida])
    def vigentes(session: Session = Depends(get_session)):
        return listar_vigentes(session)

    @router.get("/producto/{producto_id}", response_model=list[PromocionSalida])
    def de_producto(producto_id: int, session: Session = Depends(get_session)):
        return promociones_de_producto(session, producto_id)

    @router.post("/{promocion_id}/productos/{producto_id}", status_code=201)
    def vincular(promocion_id: int, producto_id: int, session: Session = Depends(get_session)):
        try:
            agregar_producto(session, promocion_id, producto_id)
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=404, detail="Promoción o producto inexistente")
        return {"promocion_id": promocion_id, "producto_id": producto_id, "activo": True}

    @router.delete("/{promocion_id}/productos/{producto_id}")
    def desvincular(promocion_id: int, producto_id: int, session: Session = Depends(get_session)):
        if quitar_producto(session, promocion_id, producto_id) is None:
            raise HTTPException(status_code=404, detail="Ese producto no está en la promoción")
        return {"promocion_id": promocion_id, "producto_id": producto_id, "activo": False}


router = crear_router(
    "/promociones", "Promociones", promociones,
    PromocionCrear, PromocionActualizar, PromocionSalida, extras=_extras,
)