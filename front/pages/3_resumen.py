from datetime import date
import streamlit as st
from front.api import ErrorAPI, pedir
from collections import Counter
from datetime import date, datetime

st.set_page_config(page_title="Resumen", layout="wide")
st.title("Resumen del negocio")

hoy = date.today()
c1, c2 = st.columns(2)
desde = c1.date_input("Desde", value=hoy)
hasta = c2.date_input("Hasta", value=hoy)

if desde > hasta:
    st.error("La fecha inicial no puede ser posterior a la final")
    st.stop()

try:
    datos = pedir(
        "GET", "/reportes/resumen",
        params={"desde": desde.isoformat(), "hasta": hasta.isoformat()},
    )
    bajo_stock = pedir("GET", "/productos/bajo-stock")
except ErrorAPI as error:
    st.error(error)
    st.stop()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Ventas", datos["num_ventas"])
m2.metric("Total vendido", f"{float(datos['total_vendido']):,.0f}")
m3.metric("Ganancia", f"{float(datos['ganancia']):,.0f}")
m4.metric("Ticket promedio", f"{float(datos['ticket_promedio']):,.0f}")

st.caption(f"Descuentos otorgados en el periodo: {float(datos['descuento_total']):,.0f}")

izq, der = st.columns(2)

with izq:
    st.subheader("Más vendidos")
    if datos["mas_vendidos"]:
        st.dataframe(
            [
                {
                    "Producto": p["producto"],
                    "Unidades": float(p["unidades"]),
                    "Ingresos": float(p["ingresos"]),
                }
                for p in datos["mas_vendidos"]
            ],
            use_container_width=True,
        )
    else:
        st.info("No hay ventas en este periodo.")

with der:
    st.subheader("Por método de pago")
    if datos["por_metodo_pago"]:
        st.bar_chart(
            {m["metodo"]: float(m["total"]) for m in datos["por_metodo_pago"]}
        )
    else:
        st.info("No hay ventas en este periodo.")

st.subheader("Alertas de stock bajo")
if bajo_stock:
    st.warning(f"{len(bajo_stock)} producto(s) están en o por debajo de su stock mínimo.")
    st.dataframe(
        [
            {
                "Producto": p["nombre"],
                "Stock": float(p["stock"]),
                "Mínimo": float(p["stock_minimo"]),
            }
            for p in bajo_stock
        ],
        use_container_width=True,
    )
else:
    st.success("Ningún producto está por debajo de su stock mínimo.")

# Counter en memoria: cuenta las ventas por día de la semana
st.subheader("Ventas por día de la semana")
try:
    ventas = pedir(
        "GET",
        "/ventas",
        params={
            "desde": f"{desde.isoformat()}T00:00:00",
            "hasta": f"{hasta.isoformat()}T23:59:59",
        },
    )
except ErrorAPI as error:
    st.error(error)
    st.stop()

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
conteo = Counter(
    datetime.fromisoformat(venta["fecha_venta"]).weekday()
    for venta in ventas
    if venta["estado"] == "completada"
)

if conteo:
    dia_fuerte, cantidad = conteo.most_common(1)[0]
    st.info(f"El día con más ventas es el {DIAS[dia_fuerte].lower()}, con {cantidad}.")
    st.dataframe(
        [{"Día": DIAS[d], "Ventas": conteo[d]} for d in range(7)],
        use_container_width=True,
    )
else:
    st.info("No hay ventas en este periodo.")