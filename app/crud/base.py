from sqlalchemy import select
from sqlalchemy.orm import Session


class CRUDBase:
    def __init__(self, modelo):
        self.modelo = modelo

    def crear(self, session: Session, **datos):
        objeto = self.modelo(**datos)
        session.add(objeto)
        session.commit()
        session.refresh(objeto)
        return objeto

    def obtener(self, session: Session, id: int):
        return session.get(self.modelo, id)

    def listar(self, session: Session, solo_activos: bool = True):
        consulta = select(self.modelo).order_by(self.modelo.id)
        if solo_activos:
            consulta = consulta.where(self.modelo.activo.is_(True))
        return list(session.scalars(consulta))

    def actualizar(self, session: Session, id: int, **cambios):
        objeto = session.get(self.modelo, id)
        if objeto is None:
            return None
        for campo, valor in cambios.items():
            if not hasattr(self.modelo, campo):
                raise ValueError(f"Campo inexistente: {campo}")
            setattr(objeto, campo, valor)
        session.commit()
        session.refresh(objeto)
        return objeto

    def desactivar(self, session: Session, id: int):
        return self.actualizar(session, id, activo=False)