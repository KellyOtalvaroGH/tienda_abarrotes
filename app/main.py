from fastapi import FastAPI

from app.routers import (
    categorias, clientes, productos, promociones,
    proveedores, reglas, reportes, vendedores, ventas,
)

app = FastAPI(title="Tienda de abarrotes")

for modulo in (
    categorias, proveedores, productos, clientes,
    vendedores, promociones, reglas, reportes, ventas,
):
    app.include_router(modulo.router)


@app.get("/salud")
def salud():
    return {"estado": "ok"}