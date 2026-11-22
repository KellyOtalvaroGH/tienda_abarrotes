from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Promocion, PromocionProducto

promociones = CRUDBase(Promocion)


def agregar_producto(session: Session, promocion_id: int, producto_id: int):
    vinculo = session.get(PromocionProducto, (promocion_id, producto_id))
    if vinculo is None:
        vinculo = PromocionProducto(promocion_id=promocion_id, producto_id=producto_id)
        session.add(vinculo)
    else:
        vinculo.activo = True
    session.commit()
    return vinculo


def quitar_producto(session: Session, promocion_id: int, producto_id: int):
    vinculo = session.get(PromocionProducto, (promocion_id, producto_id))
    if vinculo is None:
        return None
    vinculo.activo = False
    session.commit()
    return vinculo


def listar_vigentes(session: Session, fecha: date | None = None):
    fecha = fecha or date.today()
    consulta = select(Promocion).where(
        Promocion.activo.is_(True),
        Promocion.fecha_inicio <= fecha,
        Promocion.fecha_fin >= fecha,
    )
    return list(session.scalars(consulta))


def promociones_de_producto(session: Session, producto_id: int, fecha: date | None = None):
    fecha = fecha or date.today()
    consulta = (
        select(Promocion)
        .join(PromocionProducto, PromocionProducto.promocion_id == Promocion.id)
        .where(
            PromocionProducto.producto_id == producto_id,
            PromocionProducto.activo.is_(True),
            Promocion.activo.is_(True),
            Promocion.fecha_inicio <= fecha,
            Promocion.fecha_fin >= fecha,
        )
    )
    return list(session.scalars(consulta))