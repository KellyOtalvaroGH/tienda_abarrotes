from app.crud.proveedores import proveedores
from app.routers.base import crear_router
from app.schemas.proveedores import ProveedorActualizar, ProveedorCrear, ProveedorSalida

router = crear_router(
    "/proveedores", "Proveedores", proveedores,
    ProveedorCrear, ProveedorActualizar, ProveedorSalida,
)