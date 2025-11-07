
# Analizador de logs de Jenkins (mínimo viable)

Este repo **solo** cubre el análisis de logs y la generación de métricas/gráficas a partir de consolas HTML de Jenkins.

## Instalación rápida
```bash
python -m venv .venv
# Windows:
. .venv/Scripts/activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

## Uso básico
1) Generar métricas (Excel) a partir de un log HTML:
```bash
python -m logparser.generar_metricas ruta/al/log.html
```
— o, para el caso específico de `table download`:
```bash
python -m logparser.parser_table_download ruta/o/carpeta
```
(se generan ficheros `_METRICAS.xlsx` junto al HTML).

2) Crear gráficas desde el Excel generado:
```bash
python -m logparser.generar_graficas ruta/al/archivo_METRICAS.xlsx
```

Los resultados se guardan como `*_tiempos.html` y `*_etiquetas.html` junto al Excel.

## Privacidad
- **No** subas datos reales de cliente.
- Este repo no incluye ni requiere nombres de empresas/usuarios. Los metadatos de los informes se han neutralizado.
- Si necesitas anonimizar cadenas sensibles, añade un paso previo de redacción/anonimización antes de generar métricas.

## Estructura
```
src/logparser/
  generar_metricas.py
  generar_graficas.py
  parser_table_download.py
examples/
  # coloca aquí logs HTML sintéticos para probar
scripts/
  # (opcional) BAT o shell para automatizar en tu equipo
```
