from pydantic import BaseModel, Field

from app.schemas.comun import SalidaBase


class ReglaCrear(BaseModel):
    min_compras: int = Field(ge=1)
    dias_ventana: int = Field(ge=1)


class ReglaActualizar(BaseModel):
    min_compras: int | None = Field(default=None, ge=1)
    dias_ventana: int | None = Field(default=None, ge=1)


class ReglaSalida(SalidaBase):
    min_compras: int
    dias_ventana: int