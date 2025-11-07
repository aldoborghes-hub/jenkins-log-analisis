import pandas as pd
import plotly.express as px
from pathlib import Path

AUTORIA = "Autor: Proyecto Público"

def crear_grafica_tiempos(excel_path):
    try:
        df_tiempos = pd.read_excel(excel_path, sheet_name="Tiempos", engine="openpyxl")
        df_tiempos.columns = [c.strip().lower() for c in df_tiempos.columns]
        if 'tecnología' in df_tiempos.columns:
            df_tiempos = df_tiempos.rename(columns={'tecnología': 'nombre'})
        if 'tecnologia' in df_tiempos.columns:
            df_tiempos = df_tiempos.rename(columns={'tecnologia': 'nombre'})
        posibles_duracion = [c for c in df_tiempos.columns if "duracion" in c or "duración" in c]
        if not posibles_duracion or len(df_tiempos) == 0:
            print("No hay datos suficientes para la gráfica de tiempos.")
            return
        col_duracion = posibles_duracion[0]
        df_tiempos['fin'] = pd.to_datetime(df_tiempos['fin'])
        df_tiempos['inicio'] = pd.to_datetime(df_tiempos['inicio'])
        df_tiempos[col_duracion] = df_tiempos[col_duracion].astype(int)
        df_tiempos['Label'] = df_tiempos['nombre']
        fig = px.timeline(
            df_tiempos,
            x_start="inicio",
            x_end="fin",
            y="Label",
            color="Label",
            title=f"Línea de tiempo Tecnologías<br><sup>{AUTORIA}</sup>",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            xaxis_tickformat="%H:%M",
            legend_title_text='Tecnología',
            template="simple_white",
            title_font_size=24,
            title_x=0.5
        )
        nombre_base = str(excel_path).replace(".html.", ".").replace("_METRICAS.xlsx", "")
        salida = nombre_base + "_tiempos.html"
        fig.write_html(salida)
        print(f"Gráfica de tiempos generada: {salida}")
    except Exception as e:
        print(f"No se pudo generar la gráfica de tiempos: {e}")

def crear_grafica_etiquetas(excel_path):
    try:
        df_etiquetas = pd.read_excel(excel_path, sheet_name="Etiquetas", engine="openpyxl")
        df_etiquetas.columns = [c.strip().lower() for c in df_etiquetas.columns]
        if len(df_etiquetas) == 0:
            print("No hay datos suficientes para la gráfica de etiquetas.")
            return
        df_etiquetas = df_etiquetas.sort_values("inicio").drop_duplicates("etiqueta")
        df_etiquetas['inicio'] = pd.to_datetime(df_etiquetas['inicio'])
        df_etiquetas['fin'] = pd.to_datetime(df_etiquetas['fin'])
        df_etiquetas['Label'] = df_etiquetas['etiqueta'] + " (" + df_etiquetas['tecnologia'] + ")"
        fig = px.timeline(
            df_etiquetas,
            x_start="inicio",
            x_end="fin",
            y="Label",
            color="tecnologia",
            title=f"Línea de tiempo de etiquetas<br><sup>{AUTORIA}</sup>",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            xaxis_tickformat="%H:%M",
            legend_title_text='Tecnología',
            template="simple_white",
            title_font_size=24,
            title_x=0.5
        )
        nombre_base = str(excel_path).replace(".html.", ".").replace("_METRICAS.xlsx", "")
        salida = nombre_base + "_etiquetas.html"
        fig.write_html(salida)
        print(f"Gráfica de etiquetas generada: {salida}")
    except Exception as e:
        print(f"No se pudo generar la gráfica de etiquetas: {e}")

if __name__ == "__main__":
    import sys
    import os
    _logfile = "generar_graficas_log.txt"
    _logfile = os.path.join(os.path.dirname(__file__), _logfile)
    sys.stdout = open(_logfile, "a", encoding="utf-8")
    sys.stderr = sys.stdout
    print("\n--- EJECUCIÓN NUEVA ---")
    if len(sys.argv) < 2:
        print("Uso: python generar_graficas.py archivo_METRICAS.xlsx")
    else:
        excel_path = Path(sys.argv[1])
        crear_grafica_tiempos(excel_path)
        crear_grafica_etiquetas(excel_path)