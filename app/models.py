from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint, Date, ForeignKey, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ActivoMixin:
    activo: Mapped[bool] = mapped_column(default=True)


class AuditoriaMixin:
    fecha_creacion: Mapped[datetime] = mapped_column(server_default=func.now())
    fecha_modificacion: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class Categoria(ActivoMixin, AuditoriaMixin, Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria_padre_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"))


class Proveedor(ActivoMixin, AuditoriaMixin, Base):
    __tablename__ = "proveedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(150))
    nit: Mapped[str | None] = mapped_column(String(30), unique=True)
    nombre_contacto: Mapped[str | None] = mapped_column(String(100))
    telefono: Mapped[str | None] = mapped_column(String(30))
    correo: Mapped[str | None] = mapped_column(String(120))
    direccion: Mapped[str | None] = mapped_column(String(200))
    ciudad: Mapped[str | None] = mapped_column(String(80))


class Producto(ActivoMixin, AuditoriaMixin, Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo_barras: Mapped[str | None] = mapped_column(String(50), unique=True)
    nombre: Mapped[str] = mapped_column(String(150))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedores.id"))
    unidad_medida: Mapped[str] = mapped_column(String(20), default="unidad")
    precio_compra: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    stock_minimo: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)


class Cliente(ActivoMixin, AuditoriaMixin, Base):
    __tablename__ = "clientes"
    __table_args__ = (
        UniqueConstraint("tipo_documento", "numero_documento", name="uq_cliente_documento"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_documento: Mapped[str | None] = mapped_column(String(20))
    numero_documento: Mapped[str | None] = mapped_column(String(30))
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str | None] = mapped_column(String(100))
    telefono: Mapped[str | None] = mapped_column(String(30))
    correo: Mapped[str | None] = mapped_column(String(120))
    direccion: Mapped[str | None] = mapped_column(String(200))
    ciudad: Mapped[str | None] = mapped_column(String(80))


class Vendedor(ActivoMixin, AuditoriaMixin, Base):
    __tablename__ = "vendedores"
    __table_args__ = (
        UniqueConstraint("tipo_documento", "numero_documento", name="uq_vendedor_documento"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_documento: Mapped[str] = mapped_column(String(20))
    numero_documento: Mapped[str] = mapped_column(String(30))
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    telefono: Mapped[str | None] = mapped_column(String(30))
    correo: Mapped[str | None] = mapped_column(String(120))
    fecha_ingreso: Mapped[date | None] = mapped_column(Date)


class Promocion(ActivoMixin, AuditoriaMixin, Base):
    __tablename__ = "promociones"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('porcentaje', 'precio_especial', 'lleva_paga')",
            name="ck_promocion_tipo",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str | None] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(String(20))
    porcentaje_descuento: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    precio_especial: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    cantidad_lleva: Mapped[int | None] = mapped_column()
    cantidad_paga: Mapped[int | None] = mapped_column()
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)
    solo_clientes_frecuentes: Mapped[bool] = mapped_column(default=False)


class PromocionProducto(ActivoMixin, AuditoriaMixin, Base):
    __tablename__ = "promocion_productos"

    promocion_id: Mapped[int] = mapped_column(
        ForeignKey("promociones.id"), primary_key=True
    )
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id"), primary_key=True
    )


class ReglaClienteFrecuente(ActivoMixin, AuditoriaMixin, Base):
    __tablename__ = "reglas_cliente_frecuente"

    id: Mapped[int] = mapped_column(primary_key=True)
    min_compras: Mapped[int] = mapped_column()
    dias_ventana: Mapped[int] = mapped_column()


class Venta(AuditoriaMixin, Base):
    __tablename__ = "ventas"
    __table_args__ = (
        CheckConstraint(
            "metodo_pago IN ('efectivo', 'tarjeta', 'transferencia')",
            name="ck_venta_metodo_pago",
        ),
        CheckConstraint(
            "estado IN ('completada', 'anulada')",
            name="ck_venta_estado",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id"))
    vendedor_id: Mapped[int] = mapped_column(ForeignKey("vendedores.id"))
    fecha_venta: Mapped[datetime] = mapped_column(server_default=func.now())
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    descuento_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    metodo_pago: Mapped[str] = mapped_column(String(20))
    estado: Mapped[str] = mapped_column(String(20), default="completada")


class DetalleVenta(AuditoriaMixin, Base):
    __tablename__ = "detalle_ventas"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_detalle_cantidad"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("ventas.id"))
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    cantidad: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    costo_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    promocion_id: Mapped[int | None] = mapped_column(ForeignKey("promociones.id"))
    descuento: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))