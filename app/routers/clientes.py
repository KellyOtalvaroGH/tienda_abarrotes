from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.clientes import clientes, es_cliente_frecuente
from app.dependencias import get_session
from app.routers.base import crear_router
from app.schemas.clientes import ClienteActualizar, ClienteCrear, ClienteSalida


def _extras(router):
    @router.get("/{cliente_id}/es-frecuente")
    def frecuente(cliente_id: int, session: Session = Depends(get_session)):
        if clientes.obtener(session, cliente_id) is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return {"cliente_id": cliente_id, "es_frecuente": es_cliente_frecuente(session, cliente_id)}


router = crear_router(
    "/clientes", "Clientes", clientes,
    ClienteCrear, ClienteActualizar, ClienteSalida, extras=_extras,
)