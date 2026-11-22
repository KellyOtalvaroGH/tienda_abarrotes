from app.crud.vendedores import vendedores
from app.routers.base import crear_router
from app.schemas.vendedores import VendedorActualizar, VendedorCrear, VendedorSalida

router = crear_router(
    "/vendedores", "Vendedores", vendedores,
    VendedorCrear, VendedorActualizar, VendedorSalida,
)