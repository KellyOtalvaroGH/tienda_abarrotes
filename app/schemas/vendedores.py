from datetime import date

from pydantic import BaseModel

from app.schemas.comun import SalidaBase


class VendedorCrear(BaseModel):
    tipo_documento: str
    numero_documento: str
    nombre: str
    apellido: str
    telefono: str | None = None
    correo: str | None = None
    fecha_ingreso: date | None = None


class VendedorActualizar(BaseModel):
    tipo_documento: str | None = None
    numero_documento: str | None = None
    nombre: str | None = None
    apellido: str | None = None
    telefono: str | None = None
    correo: str | None = None
    fecha_ingreso: date | None = None


class VendedorSalida(SalidaBase):
    tipo_documento: str
    numero_documento: str
    nombre: str
    apellido: str
    telefono: str | None
    correo: str | None
    fecha_ingreso: date | None