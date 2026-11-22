from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.clientes import es_cliente_frecuente
from app.models import DetalleVenta, Producto, Promocion, PromocionProducto, Venta

CENTAVOS = Decimal("0.01")


def _dinero(valor) -> Decimal:
    return Decimal(valor).quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def _validar_promocion(session, promocion_id, producto_id, cliente_id):
    promocion = session.get(Promocion, promocion_id)
    if promocion is None or not promocion.activo:
        raise ValueError(f"La promoción {promocion_id} no existe o está inactiva")
    if not (promocion.fecha_inicio <= date.today() <= promocion.fecha_fin):
        raise ValueError(f"La promoción '{promocion.nombre}' no está vigente")
    vinculo = session.get(PromocionProducto, (promocion_id, producto_id))
    if vinculo is None or not vinculo.activo:
        raise ValueError(f"La promoción '{promocion.nombre}' no aplica a este producto")
    if promocion.solo_clientes_frecuentes:
        if cliente_id is None or not es_cliente_frecuente(session, cliente_id):
            raise ValueError(f"'{promocion.nombre}' es solo para clientes frecuentes")
    return promocion


def _descuento_promocion(promocion, precio, cantidad) -> Decimal:
    if promocion.tipo == "porcentaje":
        return _dinero(precio * cantidad * promocion.porcentaje_descuento / 100)
    if promocion.tipo == "precio_especial":
        return _dinero(max(precio - promocion.precio_especial, 0) * cantidad)
    # lleva_paga: por ejemplo 2x1 es lleva 2, paga 1
    grupos = int(cantidad // promocion.cantidad_lleva)
    gratis = grupos * (promocion.cantidad_lleva - promocion.cantidad_paga)
    return _dinero(precio * gratis)


def crear_venta(
    session: Session,
    vendedor_id: int,
    metodo_pago: str,
    items: list[dict],
    cliente_id: int | None = None,
) -> Venta:
    """items: [{"producto_id": 1, "cantidad": 2, "promocion_id": 3 (opcional)}, ...]"""
    if not items:
        raise ValueError("La venta no tiene productos")
    try:
        venta = Venta(
            cliente_id=cliente_id,
            vendedor_id=vendedor_id,
            metodo_pago=metodo_pago,
            subtotal=0,
            descuento_total=0,
            total=0,
        )
        session.add(venta)
        session.flush()

        subtotal = Decimal("0")
        descuento_total = Decimal("0")

        for item in items:
            producto = session.scalars(
                select(Producto).where(Producto.id == item["producto_id"]).with_for_update()
            ).first()
            if producto is None or not producto.activo:
                raise ValueError(f"El producto {item['producto_id']} no existe o está inactivo")

            cantidad = Decimal(str(item["cantidad"]))
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a cero")
            if producto.stock < cantidad:
                raise ValueError(f"Stock insuficiente de {producto.nombre}")

            precio = producto.precio_venta
            bruto = _dinero(precio * cantidad)
            descuento = Decimal("0.00")
            promocion_id = item.get("promocion_id")
            if promocion_id is not None:
                promocion = _validar_promocion(session, promocion_id, producto.id, cliente_id)
                descuento = _descuento_promocion(promocion, precio, cantidad)

            session.add(
                DetalleVenta(
                    venta_id=venta.id,
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    costo_unitario=producto.precio_compra,
                    promocion_id=promocion_id,
                    descuento=descuento,
                    subtotal=bruto - descuento,
                )
            )
            producto.stock -= cantidad
            subtotal += bruto
            descuento_total += descuento

        venta.subtotal = subtotal
        venta.descuento_total = descuento_total
        venta.total = subtotal - descuento_total
        session.commit()
        session.refresh(venta)
        return venta
    except Exception:
        session.rollback()
        raise


def anular_venta(session: Session, venta_id: int) -> Venta | None:
    venta = session.get(Venta, venta_id)
    if venta is None:
        return None
    if venta.estado == "anulada":
        raise ValueError("La venta ya está anulada")
    try:
        for detalle in obtener_detalle(session, venta_id):
            session.get(Producto, detalle.producto_id).stock += detalle.cantidad
        venta.estado = "anulada"
        session.commit()
        session.refresh(venta)
        return venta
    except Exception:
        session.rollback()
        raise


def obtener_venta(session: Session, venta_id: int):
    return session.get(Venta, venta_id)


def obtener_detalle(session: Session, venta_id: int):
    consulta = select(DetalleVenta).where(DetalleVenta.venta_id == venta_id)
    return list(session.scalars(consulta))


def listar_ventas(session: Session, desde: datetime | None = None, hasta: datetime | None = None):
    consulta = select(Venta).order_by(Venta.fecha_venta.desc())
    if desde:
        consulta = consulta.where(Venta.fecha_venta >= desde)
    if hasta:
        consulta = consulta.where(Venta.fecha_venta <= hasta)
    return list(session.scalars(consulta))


def ganancia_venta(session: Session, venta_id: int) -> Decimal:
    detalles = obtener_detalle(session, venta_id)
    return sum((d.subtotal - d.cantidad * d.costo_unitario for d in detalles), Decimal("0"))