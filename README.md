# Tienda de abarrotes

Aplicación para administrar una tienda de abarrotes: inventario, ventas, promociones y un resumen del negocio.

## Qué incluye

- Catálogos: categorías (con subcategorías), proveedores, productos, clientes y vendedores
- Caja para registrar ventas, con búsqueda por código de barras y promociones
- Promociones (2x1, porcentaje, precio especial) y cliente frecuente calculado automáticamente
- Resumen del negocio: ventas, ganancia, más vendidos, métodos de pago y alertas de stock bajo

Fuera del alcance de esta versión: inicio de sesión con roles, fiado o crédito.

## Cómo está armado

```
Front (Streamlit)  ->  API (FastAPI)  ->  CRUD (SQLAlchemy)  ->  PostgreSQL
```

- `app/`: la API (modelos, CRUD, schemas y routers)
- `front/`: las pantallas en Streamlit
- `scripts/`: creación de tablas y generación de datos sintéticos

## Requisitos

- Python 3
- PostgreSQL (con pgAdmin, para crear la base de datos)
- Git

## Instalación

1. Clona el repositorio y entra a la carpeta:

```bash
git clone https://github.com/KellyOtalvaroGH/tienda_abarrotes.git
cd tienda_abarrotes
```

2. Crea y activa el entorno virtual (Windows):

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instala las librerías:

```bash
pip install -r requirements.txt
```

4. En pgAdmin crea una base de datos llamada `tienda_abarrotes`.

5. Crea un archivo `.env` en la raíz del proyecto con esta línea, usando la contraseña de TU instalación de PostgreSQL:

```
DATABASE_URL=postgresql+psycopg://postgres:TU_CONTRASEÑA@localhost:5432/tienda_abarrotes
```

6. Crea las tablas:

```bash
python -m scripts.crear_tablas
```

7. (Opcional) Carga datos sintéticos de prueba. Este paso BORRA todo lo que haya en la base:

```bash
python -m scripts.generar_datos_sinteticos
```

## Ejecución

Se necesitan dos terminales, con el entorno virtual activo en ambas.

Terminal 1, la API:

```bash
fastapi dev app/main.py
```

Documentación de la API en http://127.0.0.1:8000/docs

Terminal 2, el front:

```bash
python -m streamlit run front/app.py
```

## Trabajo en equipo

- El archivo `.env` nunca se sube al repositorio (está en `.gitignore`).
- Antes de empezar a trabajar: `git pull`.
- Para subir cambios:

```bash
git add .
git commit -m "Descripción del cambio"
git push
```