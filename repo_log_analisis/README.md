
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
Ventajas

100 % offline: no requiere conexión a Jenkins ni credenciales.

Análisis avanzado de paralelismos: detecta pasos simultáneos.

Gráficas interactivas: exportables a HTML sin dependencias externas.

Fácilmente ampliable: se pueden añadir nuevas métricas o filtros.

Privacidad garantizada: se eliminan nombres de usuario, host o etiquetas reales.

Privacidad y buenas prácticas

No subas datos reales de cliente.

Usa logs anonimizados o sintéticos para ejemplos públicos.

Las etiquetas CR- o PF- pueden sustituirse por códigos genéricos (ej. CR-001 → TASK-001).

No compartas rutas internas ni servidores reales.

Autor

Desarrollado por Aldo Borghes como proyecto público de aprendizaje y mejora de automatizaciones para entornos Jenkins.
Inspirado en las herramientas internas utilizadas para estimación y análisis de tiempos de promoción.
## Privacidad
- **Nota:** por motivos de confidencialidad, **no se incluyen ejemplos reales de salida ni archivos generados** (Excel o gráficas).  
> El propósito del repositorio es mostrar la **estructura y lógica técnica** del analizador, manteniendo la **privacidad y anonimato** de cualquier dato de cliente o entorno interno.
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
