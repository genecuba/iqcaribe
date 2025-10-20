# -*- coding: utf-8 -*-
"""
https://github.com/genecuba
data_generators.py — generadores de CSV de ejemplo, usando csv_utils.
"""
from typing import List, Dict, Any
from . import csv_utils, table_formats

def ejemplo_platos_csv(path: str) -> None:
    headers = table_formats.SCHEMAS["platos"]["headers"]
    rows = [
        {"Plato": "Paella", "Origen": "Valenciana", "Ingredientes": ["Arroz","Maiz","Cebolla"], "Precio": "$34"},
        {"Plato": "Congri", "Origen": "Cuba", "Ingredientes": ["Arroz","Habichuelas negras","Comino"], "Precio": "$10"},
    ]
    csv_utils.write_csv(path, headers, rows)

def ejemplo_precio_coche_csv(path: str) -> None:
    headers = table_formats.SCHEMAS["precio_coche"]["headers"]
    rows = [
        {"Pais": "Cuba", "Region": "Central", "Precio": "500 USD"},
        {"Pais": "Peru", "Region": "Andes", "Precio": "600 USD"},
    ]
    csv_utils.write_csv(path, headers, rows)
