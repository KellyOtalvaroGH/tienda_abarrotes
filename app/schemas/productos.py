from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.comun import SalidaBase


class ProductoCrear(BaseModel):
    codigo_barras: str | None = None
    nombre: str
    categoria_id: int
    proveedor_id: int
    unidad_medida: str = "unidad"
    precio_compra: Decimal = Field(ge=0)
    precio_venta: Decimal = Field(ge=0)
    stock: Decimal = Field(default=0, ge=0)
    stock_minimo: Decimal = Field(default=0, ge=0)


class ProductoActualizar(BaseModel):
    codigo_barras: str | None = None
    nombre: str | None = None
    categoria_id: int | None = None
    proveedor_id: int | None = None
    unidad_medida: str | None = None
    precio_compra: Decimal | None = Field(default=None, ge=0)
    precio_venta: Decimal | None = Field(default=None, ge=0)
    stock: Decimal | None = Field(default=None, ge=0)
    stock_minimo: Decimal | None = Field(default=None, ge=0)


class ProductoSalida(SalidaBase):
    codigo_barras: str | None
    nombre: str
    categoria_id: int
    proveedor_id: int
    unidad_medida: str
    precio_compra: Decimal
    precio_venta: Decimal
    stock: Decimal
    stock_minimo: Decimal