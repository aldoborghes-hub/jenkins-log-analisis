@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Ruta base
SET "BASE_DIR=C:\RepositorioLocal\LABORATORIO\Analisis_logs_Jenkins"
SET "LOGS_DIR=%BASE_DIR%\logs"
SET "METRICAS_DIR=%BASE_DIR%\METRICAS"

:: Mostrar subdirectorios disponibles en logs
echo === Proyectos disponibles ===
dir /b /ad "%LOGS_DIR%"
echo =============================
set /p PROYECTO=Introduce el nombre exacto del proyecto (carpeta dentro de logs): 

SET "RUTA_LOGS_PROY=%LOGS_DIR%\%PROYECTO%"
SET "RUTA_METRICAS_PROY=%METRICAS_DIR%\%PROYECTO%"

IF NOT EXIST "!RUTA_LOGS_PROY!" (
    echo ❌ El proyecto "!PROYECTO!" no existe dentro de "logs".
    PAUSE
    EXIT /B
)

IF NOT EXIST "!RUTA_METRICAS_PROY!" (
    mkdir "!RUTA_METRICAS_PROY!"
)

echo Procesando archivos en: !RUTA_LOGS_PROY!
echo Guardando métricas en:  !RUTA_METRICAS_PROY!
echo.

:: Recorre todos los archivos .html en la carpeta seleccionada
FOR %%F IN ("!RUTA_LOGS_PROY!\*.html") DO (
    echo ▸ Generando métricas para: %%~nxF
    python generar_metricas.py "%%~fF"

    :: Detectar nombre del Excel generado
    SET "NOMBRE_LOG=%%~nxF"
    SET "NOMBRE_XLSX=!NOMBRE_LOG:.html=_METRICAS.xlsx!"

    IF EXIST "!NOMBRE_XLSX!" (
        move /Y "!NOMBRE_XLSX!" "!RUTA_METRICAS_PROY!\"
        echo ✔ Guardado en !RUTA_METRICAS_PROY!\!NOMBRE_XLSX!
    ) ELSE (
        echo ⚠ No se generó el Excel esperado: !NOMBRE_XLSX!
    )
    echo.
)

echo ✅ Proceso finalizado.
PAUSE
