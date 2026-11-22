import streamlit as st

from front.api import ErrorAPI, pedir

st.set_page_config(page_title="Catálogos", layout="wide")
st.title("Catálogos")


def limpiar(datos):
    return {k: (v if v != "" else None) for k, v in datos.items()}


def crear(ruta, datos, nombre):
    try:
        pedir("POST", ruta, json=limpiar(datos))
    except ErrorAPI as error:
        st.error(error)
    else:
        st.success(f"{nombre} creado correctamente")


try:
    categorias = pedir("GET", "/categorias")
    proveedores = pedir("GET", "/proveedores")
except ErrorAPI as error:
    st.error(error)
    st.stop()

tab_cat, tab_prov, tab_prod, tab_cli, tab_vend = st.tabs(
    ["Categorías", "Proveedores", "Productos", "Clientes", "Vendedores"]
)

# ---------- Categorías ----------
with tab_cat:
    with st.form("form_categoria", clear_on_submit=True):
        nombre = st.text_input("Nombre *")
        descripcion = st.text_input("Descripción")
        padre = st.selectbox(
            "Categoría padre (opcional)",
            [None] + categorias,
            format_func=lambda c: "Ninguna (categoría principal)" if c is None else c["nombre"],
        )
        if st.form_submit_button("Guardar categoría"):
            if not nombre.strip():
                st.error("El nombre es obligatorio")
            else:
                crear(
                    "/categorias",
                    {
                        "nombre": nombre.strip(),
                        "descripcion": descripcion,
                        "categoria_padre_id": padre["id"] if padre else None,
                    },
                    "Categoría",
                )
    st.dataframe(
        [
            {"ID": c["id"], "Nombre": c["nombre"], "Descripción": c["descripcion"], "Padre (ID)": c["categoria_padre_id"]}
            for c in pedir("GET", "/categorias")
        ],
        use_container_width=True,
    )

# ---------- Proveedores ----------
with tab_prov:
    with st.form("form_proveedor", clear_on_submit=True):
        razon = st.text_input("Razón social *")
        c1, c2 = st.columns(2)
        nit = c1.text_input("NIT")
        contacto = c2.text_input("Nombre de contacto")
        telefono = c1.text_input("Teléfono")
        correo = c2.text_input("Correo")
        direccion = c1.text_input("Dirección")
        ciudad = c2.text_input("Ciudad")
        if st.form_submit_button("Guardar proveedor"):
            if not razon.strip():
                st.error("La razón social es obligatoria")
            else:
                crear(
                    "/proveedores",
                    {
                        "razon_social": razon.strip(),
                        "nit": nit,
                        "nombre_contacto": contacto,
                        "telefono": telefono,
                        "correo": correo,
                        "direccion": direccion,
                        "ciudad": ciudad,
                    },
                    "Proveedor",
                )
    st.dataframe(
        [
            {"ID": p["id"], "Razón social": p["razon_social"], "NIT": p["nit"], "Contacto": p["nombre_contacto"], "Teléfono": p["telefono"], "Ciudad": p["ciudad"]}
            for p in pedir("GET", "/proveedores")
        ],
        use_container_width=True,
    )

# ---------- Productos ----------
with tab_prod:
    if not categorias or not proveedores:
        st.warning("Primero crea al menos una categoría y un proveedor.")
    else:
        with st.form("form_producto", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nombre_p = c1.text_input("Nombre *")
            codigo = c2.text_input("Código de barras")
            categoria = c1.selectbox("Categoría *", categorias, format_func=lambda c: c["nombre"])
            proveedor = c2.selectbox("Proveedor *", proveedores, format_func=lambda p: p["razon_social"])
            unidad = c1.selectbox("Unidad de medida", ["unidad", "kilo", "libra", "litro", "gramo"])
            precio_compra = c2.number_input("Precio de compra *", min_value=0.0, step=100.0)
            precio_venta = c1.number_input("Precio de venta *", min_value=0.0, step=100.0)
            stock = c2.number_input("Stock inicial", min_value=0.0, step=1.0)
            stock_min = c1.number_input("Stock mínimo", min_value=0.0, step=1.0)
            if st.form_submit_button("Guardar producto"):
                if not nombre_p.strip():
                    st.error("El nombre es obligatorio")
                elif precio_venta < precio_compra:
                    st.error("El precio de venta es menor al de compra: se vendería con pérdida")
                else:
                    crear(
                        "/productos",
                        {
                            "nombre": nombre_p.strip(),
                            "codigo_barras": codigo,
                            "categoria_id": categoria["id"],
                            "proveedor_id": proveedor["id"],
                            "unidad_medida": unidad,
                            "precio_compra": precio_compra,
                            "precio_venta": precio_venta,
                            "stock": stock,
                            "stock_minimo": stock_min,
                        },
                        "Producto",
                    )
    st.dataframe(
        [
            {
                "ID": p["id"],
                "Código": p["codigo_barras"],
                "Nombre": p["nombre"],
                "Unidad": p["unidad_medida"],
                "Compra": float(p["precio_compra"]),
                "Venta": float(p["precio_venta"]),
                "Stock": float(p["stock"]),
                "Mínimo": float(p["stock_minimo"]),
            }
            for p in pedir("GET", "/productos")
        ],
        use_container_width=True,
    )

# ---------- Clientes ----------
with tab_cli:

    # Conjunto en memoria: documentos ya registrados (consulta de pertenencia directa)
    documentos_existentes = {
        (c["tipo_documento"], c["numero_documento"])
        for c in pedir("GET", "/clientes")
        if c["numero_documento"]
    }

    with st.form("form_cliente", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre_c = c1.text_input("Nombre *")
        apellido_c = c2.text_input("Apellido")
        tipo_doc = c1.selectbox("Tipo de documento", ["", "CC", "CE", "NIT", "Pasaporte"])
        num_doc = c2.text_input("Número de documento")
        tel_c = c1.text_input("Teléfono")
        correo_c = c2.text_input("Correo")
        dir_c = c1.text_input("Dirección")
        ciudad_c = c2.text_input("Ciudad")
        if st.form_submit_button("Guardar cliente"):
            if not nombre_c.strip():
                st.error("El nombre es obligatorio")
            elif bool(tipo_doc) != bool(num_doc.strip()):
                st.error("Si indicas documento, completa el tipo y el número")
            elif (tipo_doc, num_doc.strip()) in documentos_existentes:
                st.error("Ya existe un cliente con ese documento")
            else:
                crear(
                    "/clientes",
                    {
                        "nombre": nombre_c.strip(),
                        "apellido": apellido_c,
                        "tipo_documento": tipo_doc,
                        "numero_documento": num_doc.strip(),
                        "telefono": tel_c,
                        "correo": correo_c,
                        "direccion": dir_c,
                        "ciudad": ciudad_c,
                    },
                    "Cliente",
                )
    st.dataframe(
        [
            {"ID": c["id"], "Nombre": c["nombre"], "Apellido": c["apellido"], "Documento": f"{c['tipo_documento'] or ''} {c['numero_documento'] or ''}".strip(), "Teléfono": c["telefono"]}
            for c in pedir("GET", "/clientes")
        ],
        use_container_width=True,
    )

# ---------- Vendedores ----------
with tab_vend:
    with st.form("form_vendedor", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre_v = c1.text_input("Nombre *")
        apellido_v = c2.text_input("Apellido *")
        tipo_v = c1.selectbox("Tipo de documento *", ["CC", "CE", "Pasaporte"])
        num_v = c2.text_input("Número de documento *")
        tel_v = c1.text_input("Teléfono")
        correo_v = c2.text_input("Correo")
        if st.form_submit_button("Guardar vendedor"):
            if not (nombre_v.strip() and apellido_v.strip() and num_v.strip()):
                st.error("Nombre, apellido y documento son obligatorios")
            else:
                crear(
                    "/vendedores",
                    {
                        "nombre": nombre_v.strip(),
                        "apellido": apellido_v.strip(),
                        "tipo_documento": tipo_v,
                        "numero_documento": num_v.strip(),
                        "telefono": tel_v,
                        "correo": correo_v,
                    },
                    "Vendedor",
                )
    st.dataframe(
        [
            {"ID": v["id"], "Nombre": v["nombre"], "Apellido": v["apellido"], "Documento": f"{v['tipo_documento']} {v['numero_documento']}", "Teléfono": v["telefono"]}
            for v in pedir("GET", "/vendedores")
        ],
        use_container_width=True,
    )