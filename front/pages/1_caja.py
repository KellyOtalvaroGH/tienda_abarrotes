import streamlit as st

from front.api import ErrorAPI, pedir

st.set_page_config(page_title="Caja", layout="wide")
st.title("Caja")

if "carrito" not in st.session_state:
    st.session_state.carrito = []

if "ultima_venta" in st.session_state:
    venta = st.session_state.pop("ultima_venta")
    st.success(
        f"Venta #{venta['id']} registrada. "
        f"Subtotal: {float(venta['subtotal']):,.0f} | "
        f"Descuento: {float(venta['descuento_total']):,.0f} | "
        f"Total: {float(venta['total']):,.0f}"
    )

try:
    productos = pedir("GET", "/productos")
    vendedores = pedir("GET", "/vendedores")
    clientes = pedir("GET", "/clientes")
except ErrorAPI as error:
    st.error(error)
    st.stop()

if not productos or not vendedores:
    st.warning("Se necesita al menos un producto y un vendedor registrados.")
    st.stop()

col_a, col_b, col_c = st.columns(3)
vendedor = col_a.selectbox(
    "Vendedor", vendedores, format_func=lambda v: f"{v['nombre']} {v['apellido']}"
)
cliente = col_b.selectbox(
    "Cliente (opcional)",
    [None] + clientes,
    format_func=lambda c: "Sin cliente" if c is None else f"{c['nombre']} {c['apellido'] or ''}".strip(),
)
metodo = col_c.selectbox("Método de pago", ["efectivo", "tarjeta", "transferencia"])

# Índice en memoria: código de barras -> producto (diccionario, búsqueda directa)
indice_codigos = {p["codigo_barras"]: p for p in productos if p["codigo_barras"]}

st.subheader("Agregar por código de barras")
c_cod, c_btn = st.columns([3, 1])
codigo = c_cod.text_input("Código de barras")
if c_btn.button("Agregar por código"):
    encontrado = indice_codigos.get(codigo.strip())
    if encontrado is None:
        st.error("No existe un producto con ese código")
    else:
        st.session_state.carrito.append(
            {
                "producto_id": encontrado["id"],
                "nombre": encontrado["nombre"],
                "cantidad": 1.0,
                "promocion_id": None,
                "promocion": "",
            }
        )
        st.rerun()
        
st.subheader("Agregar producto")
col1, col2, col3 = st.columns([3, 1, 3])
producto = col1.selectbox(
    "Producto",
    productos,
    format_func=lambda p: f"{p['nombre']} (stock {float(p['stock']):g})",
)
cantidad = col2.number_input("Cantidad", min_value=0.1, value=1.0, step=1.0)

try:
    promos = pedir("GET", f"/promociones/producto/{producto['id']}")
except ErrorAPI:
    promos = []
promo = col3.selectbox(
    "Promoción",
    [None] + promos,
    format_func=lambda p: "Sin promoción" if p is None else p["nombre"],
    key=f"promo_{producto['id']}",
)

if st.button("Agregar al carrito"):
    st.session_state.carrito.append(
        {
            "producto_id": producto["id"],
            "nombre": producto["nombre"],
            "cantidad": cantidad,
            "promocion_id": promo["id"] if promo else None,
            "promocion": promo["nombre"] if promo else "",
        }
    )
    st.rerun()

st.subheader("Carrito")
if not st.session_state.carrito:
    st.info("El carrito está vacío.")
else:
    st.dataframe(
        [
            {
                "Producto": i["nombre"],
                "Cantidad": i["cantidad"],
                "Promoción": i["promocion"] or "-",
            }
            for i in st.session_state.carrito
        ],
        use_container_width=True,
    )
    b1, b2 = st.columns(2)
    if b1.button("Vaciar carrito"):
        st.session_state.carrito = []
        st.rerun()
    if b2.button("Cobrar", type="primary"):
        datos = {
            "vendedor_id": vendedor["id"],
            "cliente_id": cliente["id"] if cliente else None,
            "metodo_pago": metodo,
            "items": [
                {
                    "producto_id": i["producto_id"],
                    "cantidad": i["cantidad"],
                    "promocion_id": i["promocion_id"],
                }
                for i in st.session_state.carrito
            ],
        }
        try:
            venta = pedir("POST", "/ventas", json=datos)
        except ErrorAPI as error:
            st.error(error)
        else:
            st.session_state.carrito = []
            st.session_state.ultima_venta = venta
            st.rerun()