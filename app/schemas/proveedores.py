from pydantic import BaseModel

from app.schemas.comun import SalidaBase


class ProveedorCrear(BaseModel):
    razon_social: str
    nit: str | None = None
    nombre_contacto: str | None = None
    telefono: str | None = None
    correo: str | None = None
    direccion: str | None = None
    ciudad: str | None = None


class ProveedorActualizar(BaseModel):
    razon_social: str | None = None
    nit: str | None = None
    nombre_contacto: str | None = None
    telefono: str | None = None
    correo: str | None = None
    direccion: str | None = None
    ciudad: str | None = None


class ProveedorSalida(SalidaBase):
    razon_social: str
    nit: str | None
    nombre_contacto: str | None
    telefono: str | None
    correo: str | None
    direccion: str | None
    ciudad: str | None