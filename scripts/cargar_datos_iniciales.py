from sqlalchemy import select

from app.database import SessionLocal
from app.models import ReglaClienteFrecuente

with SessionLocal() as session:
    existe = session.scalars(select(ReglaClienteFrecuente)).first()
    if not existe:
        session.add(ReglaClienteFrecuente(min_compras=6, dias_ventana=180))
        session.commit()
        print("Regla creada")
    else:
        print("La regla ya existía")