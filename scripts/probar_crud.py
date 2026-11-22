from datetime import date, datetime, timedelta
from decimal import Decimal

from app.database import SessionLocal
from app.crud.categorias import categorias
from app.crud.proveedores import proveedores
from app.crud.productos import productos, buscar_por_codigo_barras, listar_bajo_stock
from app.crud.clientes import clientes, es_cliente_frecuente
from app.crud.vendedores import vendedores
from app.crud.promociones import promociones, agregar_producto, promociones_de_producto
from app.crud.reglas_cliente_frecuente import obtener_regla_activa
from app.crud import ventas as v

sufijo = datetime.now().strftime("%H%M%S")

with SessionLocal() as s:
    # Catálogos
    padre = categorias.crear(s, nombre=f"Lácteos {sufijo}")
    hija = categorias.crear(s, nombre=f"Leches {sufijo}", categoria_padre_id=padre.id)
    prov = proveedores.crear(s, razon_social=f"Proveedor {sufijo}", nit=f"NIT{sufijo}")
    prod = productos.crear(
        s,
        codigo_barras=f"TEST{sufijo}",
        nombre=f"Leche entera {sufijo}",
        categoria_id=hija.id,
        proveedor_id=prov.id,
        precio_compra=Decimal("600.00"),
        precio_venta=Decimal("1500.00"),
        stock=Decimal("10"),
        stock_minimo=Decimal("3"),
    )
    cli = clientes.crear(s, nombre=f"Cliente {sufijo}")
    vend = vendedores.crear(
        s, tipo_documento="CC", numero_documento=sufijo,
        nombre="Vendedor", apellido=f"Prueba {sufijo}",
    )
    print("1. Catálogos creados")

    # Actualizar y desactivar
    categorias.actualizar(s, padre.id, descripcion="Leche, queso y yogur")
    assert categorias.obtener(s, padre.id).descripcion == "Leche, queso y yogur"
    print("2. Actualizar funciona")

    extra = categorias.crear(s, nombre=f"Temporal {sufijo}")
    categorias.desactivar(s, extra.id)
    assert extra.id not in [c.id for c in categorias.listar(s)]
    assert extra.id in [c.id for c in categorias.listar(s, solo_activos=False)]
    print("3. Desactivar funciona")

    assert buscar_por_codigo_barras(s, f"TEST{sufijo}").id == prod.id
    print("4. Búsqueda por código de barras funciona")

    # Promoción 2x1
    promo = promociones.crear(
        s,
        nombre=f"2x1 {sufijo}",
        tipo="lleva_paga",
        cantidad_lleva=2,
        cantidad_paga=1,
        fecha_inicio=date.today(),
        fecha_fin=date.today() + timedelta(days=1),
    )
    agregar_producto(s, promo.id, prod.id)
    assert promo.id in [p.id for p in promociones_de_producto(s, prod.id)]
    print("5. Promoción creada y ligada al producto")

    # Venta con 2x1: 2 unidades de 1500, se paga 1
    venta = v.crear_venta(
        s,
        vendedor_id=vend.id,
        metodo_pago="efectivo",
        cliente_id=cli.id,
        items=[{"producto_id": prod.id, "cantidad": 2, "promocion_id": promo.id}],
    )
    print("6. Venta:", venta.subtotal, venta.descuento_total, venta.total)
    assert venta.subtotal == Decimal("3000.00")
    assert venta.descuento_total == Decimal("1500.00")
    assert venta.total == Decimal("1500.00")
    assert productos.obtener(s, prod.id).stock == Decimal("8")
    print("   Stock después de vender:", productos.obtener(s, prod.id).stock)

    # Ganancia: 1500 cobrados - (2 * 600 de costo) = 300
    print("7. Ganancia:", v.ganancia_venta(s, venta.id))
    assert v.ganancia_venta(s, venta.id) == Decimal("300.00")

    # Venta con error: no debe dejar nada a medias
    ventas_antes = len(v.listar_ventas(s))
    try:
        v.crear_venta(
            s, vendedor_id=vend.id, metodo_pago="efectivo",
            items=[{"producto_id": prod.id, "cantidad": 999}],
        )
        print("   ERROR: debió fallar por stock")
    except ValueError as e:
        print("8. Venta rechazada correctamente:", e)
    assert len(v.listar_ventas(s)) == ventas_antes
    assert productos.obtener(s, prod.id).stock == Decimal("8")

    # Anular devuelve el stock
    v.anular_venta(s, venta.id)
    assert v.obtener_venta(s, venta.id).estado == "anulada"
    assert productos.obtener(s, prod.id).stock == Decimal("10")
    print("9. Anular devolvió el stock")

    # Cliente frecuente: con una venta anulada no cuenta
    regla = obtener_regla_activa(s)
    print("10. Regla:", regla.min_compras, "compras en", regla.dias_ventana, "días")
    print("    ¿Cliente frecuente?", es_cliente_frecuente(s, cli.id))

    print("Bajo stock:", [p.nombre for p in listar_bajo_stock(s)])
    print("\nTodas las pruebas pasaron")