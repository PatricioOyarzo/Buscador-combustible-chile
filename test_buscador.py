import pytest
from unittest.mock import patch
from Prueba import Busca_estacion , Formula_Haversine, Obtener_Precio, Tiene_Tienda

Estacion_ejemplo = [
    {
        "CodeES": "001",
        "Compania": "COPEC",
        "Direccion": "Av. Providencia 123",
        "Comuna": "Providencia",
        "Region": "METROPOLITANA",
        "Latitud": "-33.4317",
        "Longitud": "-70.6092",
        "Tienda": {
            "CodigoTienda": "001",
            "NombreTienda": "Tienda COPEC Providencia",
            "Tipo": "Pronto"
        },
        "Prices":[
            {"Producto": "Gasolina 95", "Precio": "1200"},
            {"Producto": "Diesel", "Precio": "900"},
        ]
    },
    {
        "CodeES": "002",
        "Compania": "SHELL",
        "Direccion": "Av. Las Condes 456",
        "Comuna": "Las Condes",
        "Region": "METROPOLITANA",
        "Latitud": "-33.4100",
        "Longitud": "-70.5800",
        "Tienda": {},
        "Prices":[
            {"Producto": "Gasolina 95", "Precio": "1150"},
            {"Producto": "Diesel", "Precio": "880"},
        ]
    },
    {
        "CodeES": "003",
        "Compania": "PETROBRAS",
        "Direccion": "Gran AV. 789",
        "Comuna": "La Cisterna",
        "Region": "METROPOLITANA",
        "Latitud": "-33.5200",
        "Longitud": "-70.7100",
        "Tienda": {
            "CodigoTienda": "003",
            "NombreTienda": "Stop",
            "Tipo": "Stop"
        },
        "Prices":[
            {"Producto": "Gasolina 95", "Precio": "1180"},
            {"Producto": "Diesel", "Precio": "870"},
        ]
    },
]

def test_haversine_misma_ubicacion():
    assert Formula_Haversine(-33.45, -70.65, -33.45, -70.65) == 0.0

def test_haversine_distancia_positiva():
    assert Formula_Haversine(-33.45, -70.65, -23.64, -70.40) > 0

def test_obtener_precio_existe():
    assert Obtener_Precio(Estacion_ejemplo[0], "Gasolina 95") == 1200

def test_obtener_precio_no_existe():
    assert Obtener_Precio(Estacion_ejemplo[0], "Gasolina 97") == float("inf")

def test_tiene_tienda_true():
    assert Tiene_Tienda(Estacion_ejemplo[0]) == True

def test_tiene_tienda_false():
    assert Tiene_Tienda(Estacion_ejemplo[1]) == False


@patch("Prueba.Obtener_Estaciones", return_value=Estacion_ejemplo)
def test_caso1_mas_cercana(mock_api):
    resultado = Busca_estacion(-33.45, -70.65, "95", nearest=True)
    assert resultado["success"] == True
    assert resultado["data"]["compania"] == "COPEC"

@patch("Prueba.Obtener_Estaciones", return_value=Estacion_ejemplo)
def test_caso2_mas_cercana_menor_precio(mock_api):
    resultado = Busca_estacion(-33.45, -70.65, "95", nearest= True, cheapest=True)
    assert resultado["success"] == True
    assert resultado["data"]["precio_producto"] <= 1200

@patch("Prueba.Obtener_Estaciones", return_value=Estacion_ejemplo)
def test_caso3_con_tienda(mock_api):
    resultado = Busca_estacion(-33.45, -70.65, "95", store=True)
    assert resultado["success"] == True
    assert resultado["data"]["Tiene_tienda"] == True

@patch("Prueba.Obtener_Estaciones", return_value=Estacion_ejemplo)
def test_caso4_tienda_menor_precio(mock_api):
    resultado = Busca_estacion(-33.45, -70.65, "95", store=True, cheapest=True)
    assert resultado["success"] == True
    assert resultado["data"]["Tiene_tienda"] == True