import math
import requests
import json 
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Buscador de Estaciones de Combustible",
    description="API para encontrar estaciones de combustible en Chile",
    version="1.0.0",
)

Mapeo_producto = {
    "diesel": "Diesel",
    "93": "Gasolina 93",
    "95": "Gasolina 95",
    "97": "Gasolina 97",
    "kerosene": "Kerosene",
}

def Formula_Haversine(lat1, lon1, lat2, lon2):
    Radio_tierra = 6371
    calcular_latitud = math.radians(lat2 - lat1)
    calcular_longitud = math.radians(lon2 - lon1)
    calculo_mismo_punto = (math.sin(calcular_latitud / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(calcular_longitud / 2) ** 2)
    return Radio_tierra *2 * math.asin(math.sqrt(calculo_mismo_punto))



def Obtener_Precio(estacion, nombre_producto):
    for producto in estacion.get ("Prices", []):
        if producto["Producto"] == nombre_producto:
            return float(producto["Precio"])
    return float("inf")


def Tiene_Tienda(estacion):
    tienda = estacion.get("Tienda", {})
    return bool(tienda.get("CodigoTienda"))

def Obtener_Estaciones () -> list:
    url= "https://integracion.copec.cl/stations?codEs=-1&company=-1&region=-1&comuna=-1"
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()


def Formatear_respuesta(estacion):
    tienda = estacion.get("Tienda", {})
    return {
        "success": True,
        "data":{
            "id": estacion.get("CodEs"),
            "compania": estacion.get("Compania"),
            "direccion": estacion.get("Direccion"),
            "comuna": estacion.get("Comuna"),
            "region": estacion.get("Region"),
            "latitud": float(estacion.get("Latitud")),
            "longitud": float(estacion.get("Longitud")),
            "distancia_lineal": float(estacion.get("_distancia", 0)),
            "precio_producto": int(estacion.get("_precio", 0)),
            "tienda":{
                "codigo": tienda.get("CodigoTienda", ""),
                "nombre": tienda.get("NombreTienda", ""),
                "tipo": tienda.get("Tipo", "")
            } if Tiene_Tienda(estacion) else None,
            "Tiene_tienda": Tiene_Tienda(estacion)
        }
}

def Busca_estacion(
    lat,
    lng,
    product,
    nearest = False,
    store=  False,
    cheapest = False
):

    nombre_producto = Mapeo_producto.get(product)
    if not nombre_producto:
        return {
            "success": False,
            "error": f"Producto '{product}' no es válido. Use uno de: {', '.join(Mapeo_producto.keys())}"
        }

    estaciones = Obtener_Estaciones()

    for e in estaciones:
        e["_distancia"] = Formula_Haversine(
            lat, lng, float(e["Latitud"]), float(e["Longitud"])
        )
        e["_precio"] = Obtener_Precio(e, nombre_producto)

    estaciones = [e for e in estaciones if e["_precio"] != float("inf")]

    if store:
        estaciones = [e for e in estaciones if Tiene_Tienda(e)]

    if not estaciones:
        return {"error": "No se encontraron estaciones con los criterios dados"}
    
    if nearest and not cheapest:
        resultado= min (estaciones, key= lambda e: e["_distancia"])
    
    elif nearest and cheapest:
        resultado= min (estaciones, key= lambda e:  (e["_distancia"], e["_precio"]))
    
    elif store and not cheapest:
        resultado= min (estaciones, key= lambda e: e["_distancia"])
    
    elif store and cheapest:
        resultado= min (estaciones, key= lambda e:  (e["_distancia"], e["_precio"]))

    else:
        resultado = min(estaciones, key=lambda e: e["_distancia"])
    
    return Formatear_respuesta(resultado)

@app.get("/api/stations/search")
def buscar(
    lat: float = Query(..., description="Latitud (ej: -33.45)"),
    lng: float = Query(..., description="Longitud (ej: -70.65)"),
    product: str = Query(..., description=f"Tipo de combustible ('diesel', '93', '95', '97', 'kerosene')"),
    nearest: bool = Query(False, description="Buscar la estación más cercana"),
    store: bool = Query(False, description="Buscar estación con tienda"),
    cheapest: bool = Query(False, description="Buscar la estación con el precio más bajo")
):
    resultado = Busca_estacion(lat, lng, product, nearest, store, cheapest)
    if not resultado.get("success"):
        raise HTTPException(status_code=404, detail=resultado.get("error"))
    return resultado
