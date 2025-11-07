@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo === Generador de gráficas desde archivo de métricas ===
set /p XLSX_FILE=Introduce el nombre del archivo Excel (.xlsx): 
SET "XLSX_FILE=!XLSX_FILE:"=!"

IF NOT EXIST "!XLSX_FILE!" (
    echo ❌ No se encontró el archivo !XLSX_FILE!
    echo Archivos disponibles:
    dir /b *_METRICAS.xlsx
    PAUSE
    EXIT /B
)

SET "LOG_TRACE=traza_!XLSX_FILE:.xlsx=_graficas.txt!"

echo Procesando: !XLSX_FILE!
echo Trazas guardadas en: !LOG_TRACE!

:: Ejecutar script y redirigir su salida
echo === GRAFICA TRZ: %DATE% %TIME% === >> "!LOG_TRACE!"
echo Ejecutando: generar_graficas.py "!XLSX_FILE!" >> "!LOG_TRACE!"
python generar_graficas.py "!XLSX_FILE!" >> "!LOG_TRACE!" 2>&1

:: Registrar estado de ejecución
IF ERRORLEVEL 1 (
    echo ⚠ Error al generar gráficas para !XLSX_FILE!
    echo ⚠ Error al generar gráficas para !XLSX_FILE! >> "!LOG_TRACE!"
) ELSE (
    echo ✓ Gráficas generadas correctamente para !XLSX_FILE!
    echo ✓ Gráficas generadas correctamente para !XLSX_FILE! >> "!LOG_TRACE!"
)

:: Buscar archivo de salida de gráfica
SET "GRAF_ETIQUETAS=!XLSX_FILE:_METRICAS.xlsx=_etiquetas.html!"

IF EXIST "!GRAF_ETIQUETAS!" (
    echo ✓ Gráfica de etiquetas generada: !GRAF_ETIQUETAS!
    set /p ABRIR=¿Deseas abrir la gráfica de etiquetas? (S/N): 
    IF /I "!ABRIR!"=="S" (
        start "" "!GRAF_ETIQUETAS!"
    )
) ELSE (
    echo ⚠ No se encontró la gráfica de etiquetas.
)

echo.
echo Proceso finalizado. Traza: !LOG_TRACE!
PAUSE