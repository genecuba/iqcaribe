**Propósito**

Compilar, documentar y reproducir datos de CI promedio para islas/territorios del Caribe, con múltiples fuentes, series históricas y agregación (media simple y ponderada).

**Contenido del paquete**
- iq_caribe.csv _— DataPandas (compilación Lynn & Becker 2019)._
- iq_caribe_iit_2025.csv _— International IQ Test (corte 2025, datos 2024)._
- iq_caribe_worlddata_2024.csv _— WorldData (agregado 2006–2024)._
- iq_caribe_promedio_3fuentes.csv _— promedio simple (intersección de países)._
- iq_caribe_ponderado_3fuentes.csv _— promedio ponderado (v0.2 oficial)._
- iq_caribe_historico_ampliado.csv _— puntos por años/décadas (IQ y proxies ACHQ/NIQ)._
- ci_caribe_tools_scripts.zip _— scripts Python y Node.js para experimentar._

**Formato y convenciones** (CSV)
- Codificación UTF-8.
- Separador de columnas: coma.
- Si un valor contiene comas internas, se sustituyen por **⋮**.

**Columnas típicas:**

- Tablas por fuente: pais, iq, año, fuente_nombre/fuente, fuente_url/url, notas
- Agregados: añaden iq_* por fuente, iq_promedio_3fuentes o iq_ponderado_3fuentes, y las url_*
- Histórico: pais_o_territorio, anio, valor, escala, tipo (IQ/ACHQ/NIQ), fuente_nombre, url, notas
- URLs completas en texto plano (sin hipervínculos) por cada fila

**Metodología de agregación**

Media simple: promedio aritmético de las 3 fuentes para la intersección de países.

Media ponderada (v0.2, estándar): pesos fijos

IIT = 0.60 · WorldData = 0.30 · DataPandas(L&B) = 0.10

El archivo ponderado incluye columnas w_* y un campo metodo con los pesos aplicados.

**Reproducibilidad (CLI)**

Python

```
python python/aggregate_iq.py \
  --dp /ruta/iq_caribe.csv --dp-year 2019 \
  --iit /ruta/iq_caribe_iit_2025.csv --iit-year 2025 \
  --wd /ruta/iq_caribe_worlddata_2024.csv --wd-year 2024 \
  --ref-year 2025 \
  --adj "dp=0.10,iit=0.60,wd=0.30" \
  --outdir ./out_v02
```

Node.js

```
node node/aggregateIQ.js \
  --dp /ruta/iq_caribe.csv --dp-year 2019 \
  --iit /ruta/iq_caribe_iit_2025.csv --iit-year 2025 \
  --wd /ruta/iq_caribe_worlddata_2024.csv --wd-year 2024 \
  --ref-year 2025 \
  --adj "dp=0.10,iit=0.60,wd=0.30" \
  --outdir ./out_v02
```

**Control de calidad**
- Diferenciar IQ psicométrico (Raven, WISC/WAIS, etc.) de ACHQ/NIQ (proxies de rendimiento académico)
- Marcar explícitamente tipo y escala
- Documentar muestra, año y notas cuando la fuente lo permita
- Usar siempre URL completa y, si cambia, anotar fecha de consulta

**Limitaciones y cautelas**
- Cobertura desigual por país/año; las fuentes tienen metodologías distintas y algunas se reutilizan entre sí.
- Parte del histórico usa proxies (CXC/NAEP/PISA convertidos a escala tipo-IQ). Interpretación con cautela.
- Las estimaciones de Lynn/Becker/Lynn&Vanhanen son controvertidas; se incluyen por comparabilidad histórica y van con peso reducido.

**Versiones**
- Convención: vYYYYMMDD_HHMMSS y/o v0.x.
- v0.2 oficial = esquema de pesos fijos indicado arriba.
- Los releases incluyen _data_sources/_, agregados y _README_release.md_

**Actualización de datos**
- Añadir/actualizar filas en las tablas por fuente (mantener formato y URLs).
- Ejecutar los scripts para regenerar promedio simple y ponderado.

Registrar versión y cambios de pesos si aplica.

**Licencia y uso**
Uso académico. Citar las fuentes originales de cada fila y este paquete de integración. Para análisis de política pública, contrastar con baterías estandarizadas y metadatos de calidad. Todos los datos provienen de fuentes externas, si tienes algún problema con las estadísticas ya sabes a quién le tienes que ir a protestar.
