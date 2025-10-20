# -*- coding: utf-8 -*-
"""
https://github.com/genecuba
validators.py — validaciones suaves para los CSV del proyecto.
"""
from typing import List, Sequence, Mapping

def check_headers_short(headers: Sequence[str], max_len: int = 12) -> List[str]:
    """
    Recomendación: cabeceras cortas. Devuelve advertencias si superan max_len.
    """
    warns = []
    for h in headers:
        if len(h) > max_len:
            warns.append(f"Cabecera larga: '{h}' ({len(h)} > {max_len}).")
    return warns

def check_required(headers: Sequence[str], required: Sequence[str]) -> List[str]:
    """
    Verifica que existan ciertas cabeceras requeridas.
    """
    missing = [r for r in required if r not in headers]
    return [f"Falta cabecera requerida: {m}" for m in missing]
