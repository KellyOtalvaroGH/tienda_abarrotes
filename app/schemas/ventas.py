from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ItemVenta(BaseModel):
    producto_id: int
    cantidad: Decimal = Field(gt=0)
    promocion_id: int | None = None


class VentaCrear(BaseModel):
    vendedor_id: int
    cliente_id: int | None = None
    metodo_pago: Literal["efectivo", "tarjeta", "transferencia"]
    items: list[ItemVenta] = Field(min_length=1)


class DetalleSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: Decimal
    precio_unitario: Decimal
    costo_unitario: Decimal
    promocion_id: int | None
    descuento: Decimal
    subtotal: Decimal


class VentaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int | None
    vendedor_id: int
    fecha_venta: datetime
    subtotal: Decimal
    descuento_total: Decimal
    total: Decimal
    metodo_pago: str
    estado: str


class VentaCompletaSalida(VentaSalida):
    detalles: list[DetalleSalida]
    ganancia: Decimal