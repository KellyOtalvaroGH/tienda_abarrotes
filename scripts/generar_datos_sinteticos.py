import random
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import text

import app.models  # registra las tablas
from app.crud import ventas as v
from app.crud.categorias import categorias
from app.crud.clientes import clientes, es_cliente_frecuente
from app.crud.productos import productos
from app.crud.promociones import agregar_producto, promociones
from app.crud.proveedores import proveedores
from app.crud.reglas_cliente_frecuente import reglas
from app.crud.vendedores import vendedores
from app.database import Base, SessionLocal

random.seed(42)  # mismos datos cada vez que se ejecuta

# categoría -> subcategoría -> lista de (nombre, unidad, precio_compra, precio_venta)
CATALOGO = {
    "Lácteos": {
        "Leches": [
            ("Leche entera 1L", "unidad", 3600, 4500),
            ("Leche deslactosada 1L", "unidad", 4000, 5000),
        ],
        "Quesos y yogures": [
            ("Queso campesino 500g", "unidad", 8500, 11000),
            ("Yogur fresa 1L", "unidad", 5200, 6800),
        ],
    },
    "Bebidas": {
        "Gaseosas": [
            ("Coca-Cola 1.5L", "unidad", 4800, 6500),
            ("Gaseosa manzana 1.5L", "unidad", 4200, 5800),
        ],
        "Jugos y agua": [
            ("Jugo de mango 1L", "unidad", 3500, 4800),
            ("Agua botella 600ml", "unidad", 1200, 2000),
        ],
    },
    "Despensa": {
        "Granos": [
            ("Arroz blanco", "kilo", 3800, 5000),
            ("Frijol rojo", "kilo", 7500, 9800),
            ("Lentejas", "kilo", 5200, 7000),
        ],
        "Aceites y condimentos": [
            ("Aceite de girasol 1L", "unidad", 11500, 14500),
            ("Sal 500g", "unidad", 1100, 1800),
        ],
    },
    "Aseo": {
        "Hogar": [
            ("Detergente en polvo 1kg", "unidad", 9000, 12000),
            ("Jabón de loza", "unidad", 2800, 4000),
        ],
        "Personal": [
            ("Jabón de baño", "unidad", 2000, 3200),
            ("Papel higiénico x4", "unidad", 5500, 7500),
        ],
    },
    "Frescos": {
        "Huevos": [("Huevos AA x30", "unidad", 15500, 19500)],
        "Frutas y verduras": [
            ("Banano", "kilo", 2200, 3200),
            ("Tomate", "kilo", 3000, 4500),
        ],
    },
}

PROVEEDORES = [
    ("Lácteos del Valle S.A.S.", "900123456-1", "Marta Ríos", "3101234567", "Medellín"),
    ("Distribuidora La Sabana", "900234567-2", "Carlos Gómez", "3112345678", "Bogotá"),
    ("Bebidas y Más Ltda.", "900345678-3", "Luisa Mejía", "3123456789", "Medellín"),
    ("Aseo Total S.A.", "900456789-4", "Andrés Vélez", "3134567890", "Itagüí"),
    ("Agro Fresco del Oriente", "900567890-5", "Paula Cano", "3145678901", "Rionegro"),
]

NOMBRES = ["Camila", "Juan", "Valentina", "Andrés", "Sofía", "Mateo", "Laura",
           "Santiago", "Daniela", "Felipe", "Isabella", "Sebastián", "Natalia",
           "David", "Mariana", "Julián", "Carolina", "Esteban", "Paula", "Nicolás"]
APELLIDOS = ["Gómez", "Rodríguez", "Martínez", "López", "García", "Hernández",
             "Torres", "Ramírez", "Vargas", "Castro", "Ospina", "Zapata"]

VENDEDORES = [("Luis", "Pérez"), ("Ana", "Cárdenas"), ("Jorge", "Restrepo")]

N_VENTAS = 150
DIAS_HISTORIAL = 90


def limpiar_base(session):
    tablas = ", ".join(t.name for t in Base.metadata.sorted_tables)
    session.execute(text(f"TRUNCATE {tablas} RESTART IDENTITY CASCADE"))
    session.commit()


def crear_catalogo(session):
    proveedores_creados = [
        proveedores.crear(
            session, razon_social=r, nit=n, nombre_contacto=c, telefono=t, ciudad=ci
        )
        for r, n, c, t, ci in PROVEEDORES
    ]
    lista_productos = []
    codigo = 0
    for nombre_cat, subcategorias in CATALOGO.items():
        padre = categorias.crear(session, nombre=nombre_cat)
        for nombre_sub, items in subcategorias.items():
            hija = categorias.crear(
                session, nombre=nombre_sub, categoria_padre_id=padre.id
            )
            for nombre, unidad, compra, venta in items:
                codigo += 1
                en_kilos = unidad == "kilo"
                lista_productos.append(
                    productos.crear(
                        session,
                        codigo_barras=f"770{codigo:010d}",
                        nombre=nombre,
                        categoria_id=hija.id,
                        proveedor_id=random.choice(proveedores_creados).id,
                        unidad_medida=unidad,
                        precio_compra=Decimal(compra),
                        precio_venta=Decimal(venta),
                        stock=Decimal(random.randint(40, 80) if en_kilos else random.randint(80, 200)),
                        stock_minimo=Decimal(5 if en_kilos else 10),
                    )
                )
    return lista_productos


def crear_personas(session):
    lista_clientes = []
    documentos = set()
    while len(lista_clientes) < 20:
        numero = str(random.randint(10_000_000, 1_099_999_999))
        if numero in documentos:
            continue
        documentos.add(numero)
        lista_clientes.append(
            clientes.crear(
                session,
                tipo_documento="CC",
                numero_documento=numero,
                nombre=random.choice(NOMBRES),
                apellido=f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}",
                telefono="3" + str(random.randint(100_000_000, 299_999_999)),
            )
        )
    lista_vendedores = [
        vendedores.crear(
            session,
            tipo_documento="CC",
            numero_documento=str(random.randint(10_000_000, 99_999_999)),
            nombre=n,
            apellido=a,
            fecha_ingreso=date.today() - timedelta(days=random.randint(90, 900)),
        )
        for n, a in VENDEDORES
    ]
    return lista_clientes, lista_vendedores


def crear_promociones(session, lista_productos):
    por_nombre = {p.nombre: p for p in lista_productos}
    hoy = date.today()
    promo_por_producto = defaultdict(list)  # producto_id -> promociones vigentes

    def nueva(datos, nombres_productos, vigente=True):
        promo = promociones.crear(session, **datos)
        for nombre in nombres_productos:
            producto = por_nombre[nombre]
            agregar_producto(session, promo.id, producto.id)
            if vigente:
                promo_por_producto[producto.id].append(
                    {
                        "id": promo.id,
                        "tipo": datos["tipo"],
                        "solo_frecuentes": datos.get("solo_clientes_frecuentes", False),
                    }
                )

    nueva(
        dict(
            nombre="2x1 de fin de semana", tipo="lleva_paga",
            cantidad_lleva=2, cantidad_paga=1,
            fecha_inicio=hoy - timedelta(days=3), fecha_fin=hoy + timedelta(days=14),
        ),
        ["Leche entera 1L", "Coca-Cola 1.5L"],
    )
    nueva(
        dict(
            nombre="10% para clientes frecuentes", tipo="porcentaje",
            porcentaje_descuento=Decimal("10"), solo_clientes_frecuentes=True,
            fecha_inicio=hoy - timedelta(days=30), fecha_fin=hoy + timedelta(days=60),
        ),
        ["Gaseosa manzana 1.5L", "Jugo de mango 1L", "Aceite de girasol 1L"],
    )
    nueva(
        dict(
            nombre="Día de la Madre", tipo="porcentaje",
            porcentaje_descuento=Decimal("15"),
            fecha_inicio=hoy - timedelta(days=200), fecha_fin=hoy - timedelta(days=190),
        ),
        ["Jabón de baño"],
        vigente=False,
    )
    return promo_por_producto


def crear_ventas(session, lista_productos, lista_clientes, lista_vendedores, promo_por_producto):
    # Los primeros 5 clientes compran mucho más: así hay clientes frecuentes
    pesos = [8] * 5 + [1] * (len(lista_clientes) - 5)
    opciones_cliente = [None] + lista_clientes
    pesos_cliente = [40] + pesos
    contador_pagos = Counter()
    omitidas = 0

    for _ in range(N_VENTAS):
        cliente = random.choices(opciones_cliente, weights=pesos_cliente)[0]
        items = []
        for p in random.sample(lista_productos, random.randint(1, 5)):
            if p.unidad_medida == "unidad":
                cantidad = random.randint(1, 4)
            else:
                cantidad = round(random.uniform(0.5, 3), 1)
            promo_id = None
            for promo in promo_por_producto[p.id]:
                if promo["solo_frecuentes"] and not (
                    cliente and es_cliente_frecuente(session, cliente.id)
                ):
                    continue
                if promo["tipo"] == "lleva_paga" and cantidad < 2:
                    continue
                if random.random() < 0.7:
                    promo_id = promo["id"]
                    break
            items.append(
                {"producto_id": p.id, "cantidad": cantidad, "promocion_id": promo_id}
            )

        metodo = random.choices(
            ["efectivo", "tarjeta", "transferencia"], weights=[60, 25, 15]
        )[0]
        try:
            venta = v.crear_venta(
                session,
                vendedor_id=random.choice(lista_vendedores).id,
                metodo_pago=metodo,
                items=items,
                cliente_id=cliente.id if cliente else None,
            )
        except ValueError:
            omitidas += 1
            continue

        # Se mueve la venta a una fecha pasada para tener historial
        venta.fecha_venta = datetime.now() - timedelta(
            days=random.randint(0, DIAS_HISTORIAL - 1),
            hours=random.randint(0, 9),
            minutes=random.randint(0, 59),
        )
        session.commit()
        contador_pagos[metodo] += 1

    return contador_pagos, omitidas


def main():
    respuesta = input(
        "Esto BORRA todos los datos de la base y carga datos sintéticos.\n"
        "Escribe SI para continuar: "
    )
    if respuesta.strip() != "SI":
        print("Cancelado, no se tocó nada.")
        return

    with SessionLocal() as session:
        limpiar_base(session)
        lista_productos = crear_catalogo(session)
        lista_clientes, lista_vendedores = crear_personas(session)
        promo_por_producto = crear_promociones(session, lista_productos)
        reglas.crear(session, min_compras=6, dias_ventana=180)

        pagos, omitidas = crear_ventas(
            session, lista_productos, lista_clientes, lista_vendedores, promo_por_producto
        )

        # Dos productos con poco stock para que se vean las alertas
        for producto in random.sample(lista_productos, 2):
            productos.actualizar(session, producto.id, stock=Decimal("3"))

        print(f"Productos: {len(lista_productos)} | Clientes: {len(lista_clientes)} | Vendedores: {len(lista_vendedores)}")
        print(f"Ventas creadas: {sum(pagos.values())} (omitidas por falta de stock: {omitidas})")
        print("Ventas por método de pago:", dict(pagos))


if __name__ == "__main__":
    main()