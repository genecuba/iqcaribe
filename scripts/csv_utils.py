# -*- coding: utf-8 -*-
"""
https://github.com/genecuba
csv_utils.py — utilidades para escribir CSVs con el formato del proyecto:
- Separador de columnas: coma (,)
- Comas dentro de los valores: se reemplazan por el símbolo '⋮'
- Si un valor es lista/tupla/conjunto, se unen con '⋮'
- Las cabeceras deben ser cortas (recomendado ≤ 12 chars). No se fuerza, pero se advierte.
"""
from typing import Iterable, List, Dict, Any, Sequence, Union, Optional
import io

INTERNAL_DELIM = "⋮"
COLUMN_SEP = ","

def _to_str(value: Any) -> str:
    """Convierte un valor heterogéneo a str siguiendo las reglas del proyecto."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        # Unimos elementos con '⋮'
        return INTERNAL_DELIM.join(_to_str(v) for v in value)
    s = str(value)
    # Reemplazamos comas reales por '⋮'
    return s.replace(",", INTERNAL_DELIM)

def normalize_row(row: Union[Dict[str, Any], Sequence[Any]], headers: List[str]) -> List[str]:
    """
    Normaliza una fila a lista de strings en el orden de headers.
    Admite dict con claves = headers o una secuencia del mismo largo.
    """
    if isinstance(row, dict):
        return [_to_str(row.get(h, "")) for h in headers]
    if not isinstance(row, (list, tuple)):
        raise TypeError("La fila debe ser dict o secuencia")
    if len(row) != len(headers):
        raise ValueError("La fila no coincide en longitud con headers")
    return [_to_str(v) for v in row]

def warn_long_headers(headers: List[str], max_len: int = 12) -> List[str]:
    """
    Devuelve advertencias no bloqueantes si alguna cabecera es demasiado larga.
    (No altera nada; solo devuelve lista de advertencias!!)
    """
    warnings = []
    for h in headers:
        if len(h) > max_len:
            warnings.append(f"ADVERTENCIA: la cabecera '{h}' tiene {len(h)} caracteres (> {max_len}).")
    return warnings

def render_csv(headers: List[str], rows: Iterable[Union[Dict[str, Any], Sequence[Any]]]) -> str:
    """
    Devuelve el CSV como texto (sin BOM, por default). No añade salto de línea final extra
    """
    # Línea de cabeceras
    out = [COLUMN_SEP.join(headers)]
    # Filas
    for row in rows:
        values = normalize_row(row, headers)
        out.append(COLUMN_SEP.join(values))
    return "\n".join(out)

def write_csv(path: str, headers: List[str], rows: Iterable[Union[Dict[str, Any], Sequence[Any]]]) -> None:
    """Escribe el CSV"""
    data = render_csv(headers, rows)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(data)
