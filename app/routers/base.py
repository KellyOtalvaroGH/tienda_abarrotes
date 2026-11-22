from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencias import get_session

ERROR_DATOS = "Datos duplicados o referencias a registros que no existen"


def crear_router(prefijo, etiqueta, crud, Crear, Actualizar, Salida, extras=None):
    router = APIRouter(prefix=prefijo, tags=[etiqueta])

    if extras:
        extras(router)  # van primero para que no choquen con /{id}

    @router.post("", response_model=Salida, status_code=201)
    def crear(datos: Crear, session: Session = Depends(get_session)):
        try:
            return crud.crear(session, **datos.model_dump())
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail=ERROR_DATOS)

    @router.get("", response_model=list[Salida])
    def listar(solo_activos: bool = True, session: Session = Depends(get_session)):
        return crud.listar(session, solo_activos)

    @router.get("/{id}", response_model=Salida)
    def obtener(id: int, session: Session = Depends(get_session)):
        objeto = crud.obtener(session, id)
        if objeto is None:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        return objeto

    @router.patch("/{id}", response_model=Salida)
    def actualizar(id: int, datos: Actualizar, session: Session = Depends(get_session)):
        try:
            objeto = crud.actualizar(session, id, **datos.model_dump(exclude_unset=True))
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail=ERROR_DATOS)
        if objeto is None:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        return objeto

    @router.delete("/{id}", response_model=Salida)
    def desactivar(id: int, session: Session = Depends(get_session)):
        objeto = crud.desactivar(session, id)
        if objeto is None:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        return objeto

    return router