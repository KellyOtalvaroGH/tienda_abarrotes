import streamlit as st

from front.api import ErrorAPI, pedir

st.set_page_config(page_title="Tienda de abarrotes", layout="wide")
st.title("Tienda de abarrotes")

st.subheader("Productos")

try:
    productos = pedir("GET", "/productos")
    bajo_stock = pedir("GET", "/productos/bajo-stock")
except ErrorAPI as error:
    st.error(error)
    st.stop()

col1, col2 = st.columns(2)
col1.metric("Productos activos", len(productos))
col2.metric("Con stock bajo", len(bajo_stock))

st.dataframe(
    [
        {
            "Código": p["codigo_barras"],
            "Nombre": p["nombre"],
            "Unidad": p["unidad_medida"],
            "Precio venta": float(p["precio_venta"]),
            "Stock": float(p["stock"]),
        }
        for p in productos
    ],
    use_container_width=True,
)