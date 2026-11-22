from pydantic import BaseModel

from app.schemas.comun import SalidaBase


class ClienteCrear(BaseModel):
    tipo_documento: str | None = None
    numero_documento: str | None = None
    nombre: str
    apellido: str | None = None
    telefono: str | None = None
    correo: str | None = None
    direccion: str | None = None
    ciudad: str | None = None


class ClienteActualizar(BaseModel):
    tipo_documento: str | None = None
    numero_documento: str | None = None
    nombre: str | None = None
    apellido: str | None = None
    telefono: str | None = None
    correo: str | None = None
    direccion: str | None = None
    ciudad: str | None = None


class ClienteSalida(SalidaBase):
    tipo_documento: str | None
    numero_documento: str | None
    nombre: str
    apellido: str | None
    telefono: str | None
    correo: str | None
    direccion: str | None
    ciudad: str | None