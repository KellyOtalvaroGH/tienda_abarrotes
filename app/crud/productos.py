from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Producto

productos = CRUDBase(Producto)


def buscar_por_codigo_barras(session: Session, codigo: str):
    consulta = select(Producto).where(Producto.codigo_barras == codigo)
    return session.scalars(consulta).first()


def listar_bajo_stock(session: Session):
    consulta = select(Producto).where(
        Producto.activo.is_(True),
        Producto.stock <= Producto.stock_minimo,
    )
    return list(session.scalars(consulta))