from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import ReglaClienteFrecuente

reglas = CRUDBase(ReglaClienteFrecuente)


def obtener_regla_activa(session: Session):
    consulta = (
        select(ReglaClienteFrecuente)
        .where(ReglaClienteFrecuente.activo.is_(True))
        .order_by(ReglaClienteFrecuente.id.desc())
    )
    return session.scalars(consulta).first()