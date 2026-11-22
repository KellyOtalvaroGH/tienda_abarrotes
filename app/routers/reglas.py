from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.reglas_cliente_frecuente import obtener_regla_activa, reglas
from app.dependencias import get_session
from app.routers.base import crear_router
from app.schemas.reglas import ReglaActualizar, ReglaCrear, ReglaSalida


def _extras(router):
    @router.get("/activa", response_model=ReglaSalida)
    def activa(session: Session = Depends(get_session)):
        regla = obtener_regla_activa(session)
        if regla is None:
            raise HTTPException(status_code=404, detail="No hay una regla activa")
        return regla


router = crear_router(
    "/reglas-cliente-frecuente", "Regla de cliente frecuente", reglas,
    ReglaCrear, ReglaActualizar, ReglaSalida, extras=_extras,
)