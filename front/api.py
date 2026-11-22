import requests

API_URL = "http://127.0.0.1:8000"


class ErrorAPI(Exception):
    pass


def pedir(metodo, ruta, **kwargs):
    try:
        respuesta = requests.request(metodo, API_URL + ruta, timeout=10, **kwargs)
    except requests.ConnectionError:
        raise ErrorAPI("No se pudo conectar con la API. ¿Está corriendo?")
    if respuesta.status_code >= 400:
        try:
            detalle = respuesta.json().get("detail", respuesta.text)
        except ValueError:
            detalle = respuesta.text
        raise ErrorAPI(str(detalle))
    return respuesta.json()