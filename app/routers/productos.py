from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.productos import buscar_por_codigo_barras, listar_bajo_stock, productos
from app.dependencias import get_session
from app.routers.base import crear_router
from app.schemas.productos import ProductoActualizar, ProductoCrear, ProductoSalida


def _extras(router):
    @router.get("/bajo-stock", response_model=list[ProductoSalida])
    def bajo_stock(session: Session = Depends(get_session)):
        return listar_bajo_stock(session)

    @router.get("/codigo/{codigo}", response_model=ProductoSalida)
    def por_codigo(codigo: str, session: Session = Depends(get_session)):
        producto = buscar_por_codigo_barras(session, codigo)
        if producto is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return producto


router = crear_router(
    "/productos", "Productos", productos,
    ProductoCrear, ProductoActualizar, ProductoSalida, extras=_extras,
)