#!/usr/bin/env node
/**
 * aggregateIQ.js — Agregador (media simple y ponderada) para IQ Caribe desde 3 fuentes.
 * Uso:
 *   node aggregateIQ.js \
 *     --dp iq_caribe.csv --dp-year 2019 \
 *     --iit iq_caribe_iit_2025.csv --iit-year 2025 \
 *     --wd iq_caribe_worlddata_2024.csv --wd-year 2024 \
 *     --ref-year 2025 \
 *     --adj "dp=0.7,iit=1.0,wd=0.6" \
 *     --outdir out
 *
 * No requiere paquetes externos como la basura de python
 * @genecuba
 *
 */
const fs = require('fs');
const path = require('path');

const INTERNAL_DELIM = '⋮';

function sanitize(s) {
  if (s == null) return '';
  return String(s).replace(/,/g, INTERNAL_DELIM);
}

function parseArgs(argv) {
  const args = {};
  for (let i=2; i<argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.replace(/^--/, '');
      const val = argv[i+1] && !argv[i+1].startsWith('--') ? argv[++i] : true;
      args[key] = val;
    }
  }
  return args;
}

// Minimal CSV parser (handles commas inside double-quotes)
function parseCSV(text) {
  const rows = [];
  let i = 0, field = '', row = [], inQuotes = false;
  function endField() { row.push(field); field=''; }
  function endRow() { rows.push(row); row=[]; }
  while (i < text.length) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"') {
        if (text[i+1] === '"') { field += '"'; i++; }
        else { inQuotes = false; }
      } else {
        field += ch;
      }
    } else {
      if (ch === '"') inQuotes = true;
      else if (ch === ',') endField();
      else if (ch === '\n') { endField(); endRow(); }
      else if (ch === '\r') { /* ignore */ }
      else field += ch;
    }
    i++;
  }
  // flush last field/row
  if (field.length || row.length) { endField(); endRow(); }
  const header = rows.shift() || [];
  return rows.filter(r => r.length && r.some(x=>x!==''))
             .map(r => Object.fromEntries(header.map((h, idx) => [h, r[idx] ?? ''])));
}

function toNumber(x) {
  const n = Number(x);
  return Number.isFinite(n) ? n : NaN;
}

function mean(arr) {
  const xs = arr.map(toNumber).filter(n => Number.isFinite(n));
  if (!xs.length) return NaN;
  return xs.reduce((a,b)=>a+b,0)/xs.length;
}

function parseAdj(text) {
  const d = { dp:0.7, iit:1.0, wd:0.6 };
  if (!text) return d;
  text.split(',').forEach(part => {
    const [k,v] = part.split('=').map(s => s && s.trim());
    if (!k || !v) return;
    const key = k.toLowerCase();
    const val = Number(v);
    if (Number.isFinite(val)) d[key] = val;
  });
  return d;
}

function writeCSV(pathname, rows) {
  const header = Object.keys(rows[0] || {});
  const lines = [header.join(',')];
  for (const r of rows) {
    const line = header.map(k => {
      const v = r[k];
      const s = (typeof v === 'string') ? sanitize(v) : v;
      return s == null ? '' : String(s);
    }).join(',');
    lines.push(line);
  }
  fs.writeFileSync(pathname, lines.join('\n'), 'utf8');
}

function ensureDir(p) {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

(function main(){
  const args = parseArgs(process.argv);
  const dpPath = args['dp'];
  const iitPath = args['iit'];
  const wdPath = args['wd'];
  const outdir = args['outdir'] || '.';

  const dpYear = Number(args['dp-year'] || 2019);
  const iitYear = Number(args['iit-year'] || 2025);
  const wdYear = Number(args['wd-year'] || 2024);
  const refYear = Number(args['ref-year'] || new Date().getFullYear());
  const adj = parseAdj(args['adj'] || 'dp=0.7,iit=1.0,wd=0.6');

  if (!dpPath || !iitPath || !wdPath) {
    console.error('Faltan rutas: --dp, --iit, --wd');
    process.exit(2);
  }
  ensureDir(outdir);

  const dpRows = parseCSV(fs.readFileSync(dpPath, 'utf8'));
  const iitRows = parseCSV(fs.readFileSync(iitPath, 'utf8'));
  const wdRows  = parseCSV(fs.readFileSync(wdPath, 'utf8'));

  function indexByPais(rows, urlKeyGuess) {
    const idx = {};
    for (const r of rows) {
      const pais = r['pais'] || '';
      if (!pais) continue;
      const iq = toNumber(r['iq']);
      const url = r['fuente_url'] || r['url'] || '';
      idx[pais] = { pais, iq, url: url };
    }
    return idx;
  }

  const dpIdx = indexByPais(dpRows);
  const iitIdx = indexByPais(iitRows);
  const wdIdx  = indexByPais(wdRows);

  const common = Object.keys(dpIdx).filter(p => iitIdx[p] && wdIdx[p]).sort();

  // simple mean
  const simple = [];
  for (const pais of common) {
    const dp_iq = dpIdx[pais].iq;
    const iit_iq = iitIdx[pais].iq;
    const wd_iq = wdIdx[pais].iq;
    const m = mean([dp_iq, iit_iq, wd_iq]);
    simple.push({
      pais,
      iq_datapandas_2019: Number.isFinite(dp_iq)? dp_iq.toFixed(2) : '',
      iq_iit_2025: Number.isFinite(iit_iq)? iit_iq.toFixed(2) : '',
      iq_worlddata_2024: Number.isFinite(wd_iq)? wd_iq.toFixed(2) : '',
      iq_promedio_3fuentes: Number.isFinite(m)? m.toFixed(2) : '',
      url_datapandas: dpIdx[pais].url,
      url_iit: iitIdx[pais].url,
      url_worlddata: wdIdx[pais].url
    });
  }
  writeCSV(path.join(outdir, 'iq_caribe_promedio_3fuentes.csv'), simple);

  // weighted mean
  const rec_dp = 1.0/(1.0 + (refYear - dpYear));
  const rec_iit = 1.0/(1.0 + (refYear - iitYear));
  const rec_wd = 1.0/(1.0 + (refYear - wdYear));

  const w_dp_raw = rec_dp * (adj.dp ?? 0.7);
  const w_iit_raw = rec_iit * (adj.iit ?? 1.0);
  const w_wd_raw = rec_wd * (adj.wd ?? 0.6);
  const s = w_dp_raw + w_iit_raw + w_wd_raw;
  const w_dp = w_dp_raw / s;
  const w_iit = w_iit_raw / s;
  const w_wd = w_wd_raw / s;

  const metodo = `Ponderación por recencia${INTERNAL_DELIM}independencia: IIT=${w_iit.toFixed(3)}${INTERNAL_DELIM}WD=${w_wd.toFixed(3)}${INTERNAL_DELIM}DP=${w_dp.toFixed(3)}`;

  const weighted = [];
  for (const pais of common) {
    const dp_iq = dpIdx[pais].iq;
    const iit_iq = iitIdx[pais].iq;
    const wd_iq = wdIdx[pais].iq;
    const m = mean([dp_iq, iit_iq, wd_iq]);
    const pond = w_dp*dp_iq + w_iit*iit_iq + w_wd*wd_iq;
    weighted.push({
      pais,
      iq_datapandas_2019: dp_iq.toFixed(2),
      iq_iit_2025: iit_iq.toFixed(2),
      iq_worlddata_2024: wd_iq.toFixed(2),
      iq_media_simple: m.toFixed(2),
      iq_ponderado_3fuentes: pond.toFixed(2),
      w_datapandas: w_dp.toFixed(6),
      w_iit: w_iit.toFixed(6),
      w_worlddata: w_wd.toFixed(6),
      url_datapandas: dpIdx[pais].url,
      url_iit: iitIdx[pais].url,
      url_worlddata: wdIdx[pais].url,
      metodo
    });
  }
  writeCSV(path.join(outdir, 'iq_caribe_ponderado_3fuentes.csv'), weighted);

  console.log('OK');
  console.log(`Pesos normalizados -> IIT=${w_iit.toFixed(6)}, WD=${w_wd.toFixed(6)}, DP=${w_dp.toFixed(6)}`);
})();