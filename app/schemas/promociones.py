from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.comun import SalidaBase


class PromocionCrear(BaseModel):
    nombre: str
    descripcion: str | None = None
    tipo: Literal["porcentaje", "precio_especial", "lleva_paga"]
    porcentaje_descuento: Decimal | None = Field(default=None, gt=0, le=100)
    precio_especial: Decimal | None = Field(default=None, ge=0)
    cantidad_lleva: int | None = Field(default=None, ge=1)
    cantidad_paga: int | None = Field(default=None, ge=0)
    fecha_inicio: date
    fecha_fin: date
    solo_clientes_frecuentes: bool = False

    @model_validator(mode="after")
    def validar_coherencia(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin no puede ser anterior a fecha_inicio")
        if self.tipo == "porcentaje" and self.porcentaje_descuento is None:
            raise ValueError("El tipo porcentaje requiere porcentaje_descuento")
        if self.tipo == "precio_especial" and self.precio_especial is None:
            raise ValueError("El tipo precio_especial requiere precio_especial")
        if self.tipo == "lleva_paga":
            if self.cantidad_lleva is None or self.cantidad_paga is None:
                raise ValueError("El tipo lleva_paga requiere cantidad_lleva y cantidad_paga")
            if self.cantidad_paga >= self.cantidad_lleva:
                raise ValueError("cantidad_paga debe ser menor que cantidad_lleva")
        return self


class PromocionActualizar(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    porcentaje_descuento: Decimal | None = Field(default=None, gt=0, le=100)
    precio_especial: Decimal | None = Field(default=None, ge=0)
    cantidad_lleva: int | None = Field(default=None, ge=1)
    cantidad_paga: int | None = Field(default=None, ge=0)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    solo_clientes_frecuentes: bool | None = None


class PromocionSalida(SalidaBase):
    nombre: str
    descripcion: str | None
    tipo: str
    porcentaje_descuento: Decimal | None
    precio_especial: Decimal | None
    cantidad_lleva: int | None
    cantidad_paga: int | None
    fecha_inicio: date
    fecha_fin: date
    solo_clientes_frecuentes: bool