@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo === Generador de métricas desde log HTML ===
set /p ORIGINAL_HTML=Introduce el nombre del archivo .html del log (incluyendo extensión): 
SET "ORIGINAL_HTML=!ORIGINAL_HTML:"=!"

:: Verificar que existe
IF NOT EXIST "!ORIGINAL_HTML!" (
    echo ❌ El archivo "!ORIGINAL_HTML!" no se encuentra en el directorio actual.
    dir /b *.html
    PAUSE
    EXIT /B
)

:: Crear nombre limpio eliminando '[Jenkins].htm'
SET "RENAMED_HTML=!ORIGINAL_HTML:[Jenkins].htm=!.html"

IF EXIST "!RENAMED_HTML!" (
    echo ⚠ Ya existe un archivo llamado "!RENAMED_HTML!". Se usará ese directamente.
) ELSE (
    ren "!ORIGINAL_HTML!" "!RENAMED_HTML!"
    echo 🔁 Archivo renombrado a: !RENAMED_HTML!
)

:: Ejecutar scripts con nombre limpio
python generar_metricas.py "!RENAMED_HTML!"
SET "METRICAS_NAME=!RENAMED_HTML:.html=_METRICAS.xlsx!"
python generar_graficas.py "!METRICAS_NAME!"

echo Proceso completado.
PAUSE
