# -*- coding: utf-8 -*-
"""
https://github.com/genecuba
zip_packager.py — utilidades para empaquetar carpetas en .zip
Es mejor ignorar este, es para uso interno ¡gracias!
"""
import os, zipfile
from typing import Iterable

def zip_folder(folder_path: str, zip_path: str, include_root: bool = True) -> None:
    """
    Crea un .zip de folder_path en zip_path.
    """
    folder_path = os.path.abspath(folder_path)
    base_root = os.path.dirname(folder_path) if include_root else folder_path
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(folder_path):
            for f in files:
                full = os.path.join(root, f)
                arcname = os.path.relpath(full, base_root)
                zf.write(full, arcname)
