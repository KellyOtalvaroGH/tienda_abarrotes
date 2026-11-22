from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.categorias import categorias
from app.dependencias import get_session
from app.schemas.categorias import CategoriaActualizar, CategoriaCrear, CategoriaSalida

router = APIRouter(prefix="/categorias", tags=["Categorías"])

ERROR_DATOS = "Nombre repetido o categoría padre inexistente"


@router.post("", response_model=CategoriaSalida, status_code=201)
def crear(datos: CategoriaCrear, session: Session = Depends(get_session)):
    try:
        return categorias.crear(session, **datos.model_dump())
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail=ERROR_DATOS)


@router.get("", response_model=list[CategoriaSalida])
def listar(solo_activos: bool = True, session: Session = Depends(get_session)):
    return categorias.listar(session, solo_activos)


@router.get("/{categoria_id}", response_model=CategoriaSalida)
def obtener(categoria_id: int, session: Session = Depends(get_session)):
    categoria = categorias.obtener(session, categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.patch("/{categoria_id}", response_model=CategoriaSalida)
def actualizar(
    categoria_id: int,
    datos: CategoriaActualizar,
    session: Session = Depends(get_session),
):
    try:
        categoria = categorias.actualizar(
            session, categoria_id, **datos.model_dump(exclude_unset=True)
        )
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail=ERROR_DATOS)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.delete("/{categoria_id}", response_model=CategoriaSalida)
def desactivar(categoria_id: int, session: Session = Depends(get_session)):
    categoria = categorias.desactivar(session, categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria