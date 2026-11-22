from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import ventas as v
from app.dependencias import get_session
from app.schemas.ventas import (
    DetalleSalida, VentaCompletaSalida, VentaCrear, VentaSalida,
)

router = APIRouter(prefix="/ventas", tags=["Ventas"])


def _completa(session: Session, venta) -> VentaCompletaSalida:
    return VentaCompletaSalida(
        **VentaSalida.model_validate(venta).model_dump(),
        detalles=[DetalleSalida.model_validate(d) for d in v.obtener_detalle(session, venta.id)],
        ganancia=v.ganancia_venta(session, venta.id),
    )


@router.post("", response_model=VentaCompletaSalida, status_code=201)
def crear(datos: VentaCrear, session: Session = Depends(get_session)):
    try:
        venta = v.crear_venta(
            session,
            vendedor_id=datos.vendedor_id,
            cliente_id=datos.cliente_id,
            metodo_pago=datos.metodo_pago,
            items=[item.model_dump() for item in datos.items],
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Vendedor o cliente inexistente")
    return _completa(session, venta)


@router.get("", response_model=list[VentaSalida])
def listar(
    desde: datetime | None = None,
    hasta: datetime | None = None,
    session: Session = Depends(get_session),
):
    return v.listar_ventas(session, desde, hasta)


@router.get("/{venta_id}", response_model=VentaCompletaSalida)
def obtener(venta_id: int, session: Session = Depends(get_session)):
    venta = v.obtener_venta(session, venta_id)
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return _completa(session, venta)


@router.post("/{venta_id}/anular", response_model=VentaSalida)
def anular(venta_id: int, session: Session = Depends(get_session)):
    try:
        venta = v.anular_venta(session, venta_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta