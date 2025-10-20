# -*- coding: utf-8 -*-
"""
https://github.com/genecuba
¡Esto es simplemente un ejemplo de como funciona!
table_formats.py — esquemas/plantillas frecuentes de tablas del proyecto.
Se definen headers "cortos" y una breve descripción para referencia.
"""
from typing import Dict, List

SCHEMAS: Dict[str, Dict[str, List[str]]] = {
    # Ejemplo de la conversación:
    # Tabla: Precio por coche
    "precio_coche": {
        "headers": ["Pais", "Region", "Precio"],
        "desc": ["País", "Región (breve)", "Precio con unidad (p. ej. 500 USD)"]
    },
    # Catálogo gastronómico (ejemplo con listas en valores)
    "platos": {
        "headers": ["Plato", "Origen", "Ingredientes", "Precio"],
        "desc": ["Nombre", "Región/país", "Lista separada con '⋮'", "Precio con símbolo"]
    }
}
