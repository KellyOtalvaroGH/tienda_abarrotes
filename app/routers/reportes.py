from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.dependencias import get_session
from app.models import DetalleVenta, Producto, Venta

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/resumen")
def resumen(
    desde: date | None = None,
    hasta: date | None = None,
    session: Session = Depends(get_session),
):
    hoy = date.today()
    desde = desde or hoy
    hasta = hasta or hoy
    inicio = datetime.combine(desde, time.min)
    fin = datetime.combine(hasta + timedelta(days=1), time.min)
    filtro = (
        Venta.estado == "completada",
        Venta.fecha_venta >= inicio,
        Venta.fecha_venta < fin,
    )

    cantidad, subtotal, descuento, total = session.execute(
        select(
            func.count(Venta.id),
            func.coalesce(func.sum(Venta.subtotal), 0),
            func.coalesce(func.sum(Venta.descuento_total), 0),
            func.coalesce(func.sum(Venta.total), 0),
        ).where(*filtro)
    ).one()

    ganancia = session.scalar(
        select(
            func.coalesce(
                func.sum(
                    DetalleVenta.subtotal - DetalleVenta.cantidad * DetalleVenta.costo_unitario
                ),
                0,
            )
        )
        .join(Venta, Venta.id == DetalleVenta.venta_id)
        .where(*filtro)
    )

    top = session.execute(
        select(
            Producto.nombre,
            func.sum(DetalleVenta.cantidad),
            func.sum(DetalleVenta.subtotal),
        )
        .join(DetalleVenta, DetalleVenta.producto_id == Producto.id)
        .join(Venta, Venta.id == DetalleVenta.venta_id)
        .where(*filtro)
        .group_by(Producto.id, Producto.nombre)
        .order_by(func.sum(DetalleVenta.cantidad).desc())
        .limit(5)
    ).all()

    por_metodo = session.execute(
        select(Venta.metodo_pago, func.count(Venta.id), func.sum(Venta.total))
        .where(*filtro)
        .group_by(Venta.metodo_pago)
    ).all()

    return {
        "desde": desde,
        "hasta": hasta,
        "num_ventas": cantidad,
        "subtotal": subtotal,
        "descuento_total": descuento,
        "total_vendido": total,
        "ganancia": ganancia,
        "ticket_promedio": (total / cantidad) if cantidad else 0,
        "mas_vendidos": [
            {"producto": n, "unidades": u, "ingresos": i} for n, u, i in top
        ],
        "por_metodo_pago": [
            {"metodo": m, "ventas": c, "total": t} for m, c, t in por_metodo
        ],
    }