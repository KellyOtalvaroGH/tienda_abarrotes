from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.crud.reglas_cliente_frecuente import obtener_regla_activa
from app.models import Cliente, Venta

clientes = CRUDBase(Cliente)


def es_cliente_frecuente(session: Session, cliente_id: int) -> bool:
    regla = obtener_regla_activa(session)
    if regla is None:
        return False
    desde = datetime.now() - timedelta(days=regla.dias_ventana)
    compras = session.scalar(
        select(func.count(Venta.id)).where(
            Venta.cliente_id == cliente_id,
            Venta.estado == "completada",
            Venta.fecha_venta >= desde,
        )
    )
    return compras >= regla.min_compras