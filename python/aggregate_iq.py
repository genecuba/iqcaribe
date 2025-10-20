#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aggregate_iq.py — Agregador (media simple y ponderada) para IQ Caribe desde 3 fuentes.
No requiere librerías externas. Uso típico:

    python aggregate_iq.py \
        --dp iq_caribe.csv --dp-year 2019 \
        --iit iq_caribe_iit_2025.csv --iit-year 2025 \
        --wd iq_caribe_worlddata_2024.csv --wd-year 2024 \
        --ref-year 2025 \
        --adj "dp=0.7,iit=1.0,wd=0.6" \
        --outdir out

Salida:
  - iq_caribe_promedio_3fuentes.csv
  - iq_caribe_ponderado_3fuentes.csv

Ponderación por defecto: w_raw = recencia * independencia,
    recencia = 1 / (1 + (ref_year - source_year))
    independencia: dp=0.7, iit=1.0, wd=0.6
Los pesos finales se normalizan por suma.
@genecuba
"""
import argparse, csv, os, sys, math, datetime

INTERNAL_DELIM = "⋮"

def sanitize(s):
    if s is None:
        return ""
    return str(s).replace(",", INTERNAL_DELIM)

def read_csv_rows(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [ {k: v for k, v in r.items()} for r in reader ]
    return rows

def pick_cols(rows, mapping):
    # mapping: {"pais":"pais", "iq":"iq", "url":"url_datapandas"}
    out = []
    for r in rows:
        x = {}
        for k, newk in mapping.items():
            x[newk] = r.get(k, "")
        out.append(x)
    return out

def mean(vals):
    vals = [v for v in vals if isinstance(v,(int,float)) and not math.isnan(v)]
    return sum(vals)/len(vals) if vals else float("nan")

def to_float(x):
    try:
        return float(x)
    except Exception:
        return float("nan")

def parse_adj(text):
    # "dp=0.7,iit=1.0,wd=0.6"
    d = {"dp":0.7, "iit":1.0, "wd":0.6}
    if not text:
        return d
    for part in text.split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k,v = part.split("=",1)
        k=k.strip().lower(); v=v.strip()
        try:
            d[k] = float(v)
        except Exception:
            pass
    return d

def ensure_dir(p):
    if not os.path.isdir(p):
        os.makedirs(p, exist_ok=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dp", required=True, help="CSV DataPandas (Lynn&Becker 2019 comp.)")
    ap.add_argument("--iit", required=True, help="CSV International IQ Test (2025)")
    ap.add_argument("--wd", required=True, help="CSV WorldData (2006–2024)")

    ap.add_argument("--dp-year", type=int, default=2019)
    ap.add_argument("--iit-year", type=int, default=2025)
    ap.add_argument("--wd-year", type=int, default=2024)
    ap.add_argument("--ref-year", type=int, default=datetime.datetime.now().year)

    ap.add_argument("--adj", default="dp=0.7,iit=1.0,wd=0.6",
                    help="Ajustes de independencia (dp,iit,wd), ej: 'dp=0.7,iit=1.0,wd=0.6'")

    ap.add_argument("--outdir", default=".", help="Carpeta de salida")
    args = ap.parse_args()

    ensure_dir(args.outdir)

    # --- Leer CSVs en esquemas esperados ---
    # DP: cols esperadas: pais, iq, url
    dp_rows = read_csv_rows(args.dp)
    if not dp_rows:
        print("Archivo DP vacío", file=sys.stderr); sys.exit(2)
    # detectar columnas por nombre típico
    # soportamos 'url' o 'fuente_url'
    dp_map = {}
    # hallamos nombres reales
    dp_cols = dp_rows[0].keys()
    dp_map["pais"] = "pais" if "pais" in dp_cols else next(iter(dp_cols))
    dp_map["iq"] = "iq" if "iq" in dp_cols else next(iter(dp_cols))
    dp_url_key = "url" if "url" in dp_cols else ("fuente_url" if "fuente_url" in dp_cols else None)

    dp_rows2 = []
    for r in dp_rows:
        dp_rows2.append({
            "pais": r.get(dp_map["pais"], ""),
            "iq": to_float(r.get(dp_map["iq"], "")),
            "url_datapandas": r.get(dp_url_key, "") if dp_url_key else ""
        })

    # IIT: pais, iq, fuente_url
    iit_rows = read_csv_rows(args.iit)
    iit_cols = iit_rows[0].keys()
    iit_url_key = "fuente_url" if "fuente_url" in iit_cols else ("url" if "url" in iit_cols else None)
    iit_rows2 = []
    for r in iit_rows:
        iit_rows2.append({
            "pais": r.get("pais",""),
            "iq": to_float(r.get("iq","")),
            "url_iit": r.get(iit_url_key,"") if iit_url_key else ""
        })

    # WD: pais, iq, fuente_url
    wd_rows = read_csv_rows(args.wd)
    wd_cols = wd_rows[0].keys()
    wd_url_key = "fuente_url" if "fuente_url" in wd_cols else ("url" if "url" in wd_cols else None)
    wd_rows2 = []
    for r in wd_rows:
        wd_rows2.append({
            "pais": r.get("pais",""),
            "iq": to_float(r.get("iq","")),
            "url_worlddata": r.get(wd_url_key,"") if wd_url_key else ""
        })

    # --- Intersección de países ---
    set_dp = {r["pais"] for r in dp_rows2 if r["pais"]}
    set_iit = {r["pais"] for r in iit_rows2 if r["pais"]}
    set_wd = {r["pais"] for r in wd_rows2 if r["pais"]}
    common = sorted(set_dp & set_iit & set_wd)

    # index por pais
    idx_dp = {r["pais"]: r for r in dp_rows2}
    idx_iit = {r["pais"]: r for r in iit_rows2}
    idx_wd = {r["pais"]: r for r in wd_rows2}

    # --- Media simple ---
    simple_out = []
    for pais in common:
        dp_iq = idx_dp[pais]["iq"]
        iit_iq = idx_iit[pais]["iq"]
        wd_iq = idx_wd[pais]["iq"]
        m = mean([dp_iq, iit_iq, wd_iq])
        simple_out.append({
            "pais": pais,
            "iq_datapandas_2019": round(dp_iq,2),
            "iq_iit_2025": round(iit_iq,2),
            "iq_worlddata_2024": round(wd_iq,2),
            "iq_promedio_3fuentes": round(m,2),
            "url_datapandas": idx_dp[pais]["url_datapandas"],
            "url_iit": idx_iit[pais]["url_iit"],
            "url_worlddata": idx_wd[pais]["url_worlddata"],
        })

    simple_path = os.path.join(args.outdir, "iq_caribe_promedio_3fuentes.csv")
    with open(simple_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(simple_out[0].keys()))
        writer.writeheader()
        for r in simple_out:
            r2 = {k: (sanitize(v) if isinstance(v,str) else v) for k,v in r.items()}
            writer.writerow(r2)

    # --- Media ponderada ---
    adj = parse_adj(args.adj)
    rec_dp = 1.0/(1.0 + (args.ref_year - args.dp_year))
    rec_iit = 1.0/(1.0 + (args.ref_year - args.iit_year))
    rec_wd = 1.0/(1.0 + (args.ref_year - args.wd_year))

    w_dp_raw = rec_dp * adj.get("dp",0.7)
    w_iit_raw = rec_iit * adj.get("iit",1.0)
    w_wd_raw = rec_wd * adj.get("wd",0.6)
    s = w_dp_raw + w_iit_raw + w_wd_raw
    w_dp, w_iit, w_wd = w_dp_raw/s, w_iit_raw/s, w_wd_raw/s

    weighted_out = []
    metodo = f"Ponderación por recencia{INTERNAL_DELIM}independencia: IIT={w_iit:.3f}{INTERNAL_DELIM}WD={w_wd:.3f}{INTERNAL_DELIM}DP={w_dp:.3f}"
    for pais in common:
        dp_iq = idx_dp[pais]["iq"]
        iit_iq = idx_iit[pais]["iq"]
        wd_iq = idx_wd[pais]["iq"]
        media = mean([dp_iq, iit_iq, wd_iq])
        ponderado = w_dp*dp_iq + w_iit*iit_iq + w_wd*wd_iq
        weighted_out.append({
            "pais": pais,
            "iq_datapandas_2019": round(dp_iq,2),
            "iq_iit_2025": round(iit_iq,2),
            "iq_worlddata_2024": round(wd_iq,2),
            "iq_media_simple": round(media,2),
            "iq_ponderado_3fuentes": round(ponderado,2),
            "w_datapandas": round(w_dp,6),
            "w_iit": round(w_iit,6),
            "w_worlddata": round(w_wd,6),
            "url_datapandas": idx_dp[pais]["url_datapandas"],
            "url_iit": idx_iit[pais]["url_iit"],
            "url_worlddata": idx_wd[pais]["url_worlddata"],
            "metodo": metodo
        })

    weighted_path = os.path.join(args.outdir, "iq_caribe_ponderado_3fuentes.csv")
    with open(weighted_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(weighted_out[0].keys()))
        writer.writeheader()
        for r in weighted_out:
            r2 = {k: (sanitize(v) if isinstance(v,str) else v) for k,v in r.items()}
            writer.writerow(r2)

    # pequeño log en stdout
    print("OK")
    print("Promedio simple:", os.path.abspath(simple_path))
    print("Promedio ponderado:", os.path.abspath(weighted_path))

if __name__ == "__main__":
    main()
