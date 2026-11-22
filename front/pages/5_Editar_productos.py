import streamlit as st

from front.api import ErrorAPI, pedir

st.set_page_config(page_title="Editar productos", layout="wide")
st.title("Editar productos")

try:
    productos = pedir("GET", "/productos", params={"solo_activos": "false"})
    categorias = pedir("GET", "/categorias")
    proveedores = pedir("GET", "/proveedores")
except ErrorAPI as error:
    st.error(error)
    st.stop()

if "mensaje_ok" in st.session_state:
    st.success(st.session_state.pop("mensaje_ok"))

if not productos:
    st.info("Todavía no hay productos.")
    st.stop()

producto = st.selectbox(
    "Producto a editar",
    productos,
    format_func=lambda p: f"{p['nombre']}" + ("" if p["activo"] else " (inactivo)"),
)


def indice(lista, campo, valor):
    for i, elemento in enumerate(lista):
        if elemento[campo] == valor:
            return i
    return 0


UNIDADES = ["unidad", "kilo", "libra", "litro", "gramo"]
if producto["unidad_medida"] not in UNIDADES:
    UNIDADES.append(producto["unidad_medida"])

with st.form(f"editar_{producto['id']}"):
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombre *", value=producto["nombre"])
    codigo = c2.text_input("Código de barras", value=producto["codigo_barras"] or "")
    categoria = c1.selectbox(
        "Categoría *",
        categorias,
        index=indice(categorias, "id", producto["categoria_id"]),
        format_func=lambda c: c["nombre"],
    )
    proveedor = c2.selectbox(
        "Proveedor *",
        proveedores,
        index=indice(proveedores, "id", producto["proveedor_id"]),
        format_func=lambda p: p["razon_social"],
    )
    unidad = c1.selectbox(
        "Unidad de medida", UNIDADES, index=UNIDADES.index(producto["unidad_medida"])
    )
    precio_compra = c2.number_input(
        "Precio de compra *", min_value=0.0, value=float(producto["precio_compra"]), step=100.0
    )
    precio_venta = c1.number_input(
        "Precio de venta *", min_value=0.0, value=float(producto["precio_venta"]), step=100.0
    )
    stock = c2.number_input(
        "Stock", min_value=0.0, value=float(producto["stock"]), step=1.0
    )
    stock_min = c1.number_input(
        "Stock mínimo", min_value=0.0, value=float(producto["stock_minimo"]), step=1.0
    )
    activo = c2.checkbox("Producto activo", value=producto["activo"])

    if st.form_submit_button("Guardar cambios", type="primary"):
        if not nombre.strip():
            st.error("El nombre es obligatorio")
        elif precio_venta < precio_compra:
            st.error("El precio de venta es menor al de compra: se vendería con pérdida")
        else:
            cambios = {
                "nombre": nombre.strip(),
                "codigo_barras": codigo.strip() or None,
                "categoria_id": categoria["id"],
                "proveedor_id": proveedor["id"],
                "unidad_medida": unidad,
                "precio_compra": precio_compra,
                "precio_venta": precio_venta,
                "stock": stock,
                "stock_minimo": stock_min,
                "activo": activo,
            }
            try:
                pedir("PATCH", f"/productos/{producto['id']}", json=cambios)
            except ErrorAPI as error:
                st.error(error)
            else:
                st.session_state.mensaje_ok = f"Producto '{nombre.strip()}' actualizado"
                st.rerun()