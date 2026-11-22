from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoriaCrear(BaseModel):
    nombre: str
    descripcion: str | None = None
    categoria_padre_id: int | None = None


class CategoriaActualizar(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    categoria_padre_id: int | None = None


class CategoriaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    categoria_padre_id: int | None
    activo: bool
    fecha_creacion: datetime
    fecha_modificacion: datetime