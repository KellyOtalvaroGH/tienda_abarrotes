from datetime import date, timedelta

import streamlit as st

from front.api import ErrorAPI, pedir

st.set_page_config(page_title="Promociones", layout="wide")
st.title("Promociones")

try:
    productos = pedir("GET", "/productos")
    promociones = pedir("GET", "/promociones")
except ErrorAPI as error:
    st.error(error)
    st.stop()

if "mensaje_ok" in st.session_state:
    st.success(st.session_state.pop("mensaje_ok"))

st.subheader("Nueva promoción")

TIPOS = {
    "lleva_paga": "Lleva X paga Y (por ejemplo 2x1)",
    "porcentaje": "Porcentaje de descuento",
    "precio_especial": "Precio especial",
}
tipo = st.selectbox("Tipo de promoción", list(TIPOS), format_func=lambda t: TIPOS[t])

with st.form("form_promocion", clear_on_submit=True):
    nombre = st.text_input("Nombre *", placeholder="Día de la Madre")
    descripcion = st.text_input("Descripción")

    cantidad_lleva = cantidad_paga = porcentaje = precio_especial = None
    if tipo == "lleva_paga":
        c1, c2 = st.columns(2)
        cantidad_lleva = c1.number_input("Cantidad que lleva *", min_value=2, value=2, step=1)
        cantidad_paga = c2.number_input("Cantidad que paga *", min_value=0, value=1, step=1)
    elif tipo == "porcentaje":
        porcentaje = st.number_input("Porcentaje de descuento *", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
    else:
        precio_especial = st.number_input("Precio especial por unidad *", min_value=0.0, step=100.0)

    f1, f2 = st.columns(2)
    inicio = f1.date_input("Fecha de inicio", value=date.today())
    fin = f2.date_input("Fecha de fin", value=date.today() + timedelta(days=7))

    solo_frecuentes = st.checkbox("Solo para clientes frecuentes")
    elegidos = st.multiselect(
        "Productos a los que aplica *",
        productos,
        format_func=lambda p: p["nombre"],
    )

    if st.form_submit_button("Guardar promoción"):
        if not nombre.strip():
            st.error("El nombre es obligatorio")
        elif not elegidos:
            st.error("Elige al menos un producto")
        elif fin < inicio:
            st.error("La fecha de fin no puede ser anterior a la de inicio")
        elif tipo == "lleva_paga" and cantidad_paga >= cantidad_lleva:
            st.error("La cantidad que paga debe ser menor que la que lleva")
        elif tipo == "precio_especial" and not precio_especial:
            st.error("Indica el precio especial")
        else:
            datos = {
                "nombre": nombre.strip(),
                "descripcion": descripcion or None,
                "tipo": tipo,
                "porcentaje_descuento": porcentaje,
                "precio_especial": precio_especial,
                "cantidad_lleva": int(cantidad_lleva) if cantidad_lleva else None,
                "cantidad_paga": int(cantidad_paga) if cantidad_lleva else None,
                "fecha_inicio": inicio.isoformat(),
                "fecha_fin": fin.isoformat(),
                "solo_clientes_frecuentes": solo_frecuentes,
            }
            try:
                promo = pedir("POST", "/promociones", json=datos)
                for producto in elegidos:
                    pedir("POST", f"/promociones/{promo['id']}/productos/{producto['id']}")
            except ErrorAPI as error:
                st.error(error)
            else:
                st.session_state.mensaje_ok = f"Promoción '{promo['nombre']}' creada con {len(elegidos)} producto(s)"
                st.rerun()

st.subheader("Promociones registradas")
if promociones:
    hoy = date.today().isoformat()
    st.dataframe(
        [
            {
                "ID": p["id"],
                "Nombre": p["nombre"],
                "Tipo": TIPOS.get(p["tipo"], p["tipo"]),
                "Desde": p["fecha_inicio"],
                "Hasta": p["fecha_fin"],
                "Vigente hoy": "Sí" if p["fecha_inicio"] <= hoy <= p["fecha_fin"] else "No",
                "Solo frecuentes": "Sí" if p["solo_clientes_frecuentes"] else "No",
            }
            for p in promociones
        ],
        use_container_width=True,
    )
else:
    st.info("Todavía no hay promociones.")