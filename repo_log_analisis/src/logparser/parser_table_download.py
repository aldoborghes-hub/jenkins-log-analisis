#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser específico para logs de Jenkins del job "table download".
Actualización:
- "Tiempos" ahora usa el PRIMER y ÚLTIMO timestamp del log para calcular la duración total del proceso.
- GlobalData y Etiquetas mantienen el detalle por tabla descargada.

Hojas generadas:
  * GlobalData: etiqueta, tecnologia, fase, inicio, fin, duracion_ms, duracion_hms
  * Tiempos: Tecnología, Inicio, Fin, Duración (ms), Duración   <-- ahora = (último_ts - primer_ts)
  * Etiquetas: Numero etiqueta, Tecnologia, Inicio, Fin, Duración
  * Medias Tecnologia: Tecnología, Número de etiquetas, Suma total (ms), Media (ms), Media (h:m:s)

Uso:
    python parser_table_download.py "<ruta al HTML>"       # un archivo
    python parser_table_download.py "<ruta al directorio>" # procesa todos los .html del directorio
"""
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    from bs4 import BeautifulSoup
except ImportError as e:
    print("[ERROR] Falta la librería 'beautifulsoup4'. Instálala con: pip install beautifulsoup4")
    sys.exit(1)

_TS_RE = re.compile(r"\[(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\]")
_DL_ECHO_RE = re.compile(r"Downloaded ftp file\s+([A-Z0-9_]+)")
_TO_PATH_RE = re.compile(r"to\s+[A-Z]:/[^/\n]+/([A-Z0-9_]+)\s*$", re.IGNORECASE)

def _extract_console_text(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")
    pre = soup.find("pre") or soup.select_one("#main-panel pre, #main-panel #out")
    return pre.get_text("\n") if pre else soup.get_text("\n")

def _format_hms_from_ms(ms: int) -> str:
    if ms is None or pd.isna(ms):
        return ""
    s = max(0, int(ms // 1000))
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:02d}"

def parse_table_download_console(html_text: str, proyecto: str = "PROD_TD"):
    """
    Devuelve:
      df_events: DataFrame con columnas [etiqueta, tecnologia, fase, inicio, fin, duracion_ms, duracion_hms]
      log_start: datetime del primer timestamp detectado en el log
      log_end:   datetime del último timestamp detectado en el log
    """
    text = _extract_console_text(html_text)
    lines = text.splitlines()

    events = {}  # tabla -> {start, end}
    log_start = None
    log_end = None

    for line in lines:
        m_ts = _TS_RE.search(line)
        if m_ts:
            ts = datetime.strptime(m_ts.group(1), "%Y.%m.%d %H:%M:%S")
            if (log_start is None) or (ts < log_start):
                log_start = ts
            if (log_end is None) or (ts > log_end):
                log_end = ts

            # 1) Línea tipo: "... to D:/.../<TABLA>"
            m_to = _TO_PATH_RE.search(line)
            if m_to:
                table = m_to.group(1)
                e = events.setdefault(table, {"start": ts, "end": ts})
                if ts < e["start"]:
                    e["start"] = ts
                if ts > e["end"]:
                    e["end"] = ts

            # 2) Línea tipo: "[echo] Downloaded ftp file <TABLA>"
            m_dl = _DL_ECHO_RE.search(line)
            if m_dl:
                table = m_dl.group(1)
                e = events.setdefault(table, {"start": ts, "end": ts})
                if ts < e["start"]:
                    e["start"] = ts
                if ts > e["end"]:
                    e["end"] = ts

    rows = []
    for table, e in events.items():
        inicio = e["start"]
        fin = e["end"]
        dur_ms = int((fin - inicio).total_seconds() * 1000)
        rows.append({
            "etiqueta": table,                 # usamos el código de tabla
            "tecnologia": "AS400",
            "fase": "DOWNLOAD",
            "inicio": inicio,
            "fin": fin,
            "duracion_ms": dur_ms,
            "duracion_hms": _format_hms_from_ms(dur_ms),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        # Asegura esquema para no romper el pipeline
        df = pd.DataFrame(columns=[
            "etiqueta","tecnologia","fase","inicio","fin","duracion_ms","duracion_hms"
        ])
    else:
        df = df.sort_values(["inicio","etiqueta"]).reset_index(drop=True)
    return df, log_start, log_end

def _build_sheets(df_events: pd.DataFrame, log_start, log_end) -> dict:
    """
    Construye los DataFrames para las 4 hojas esperadas.
    - En "Tiempos", la duración es (log_end - log_start).
    """
    # 1) GlobalData
    df_global = df_events.copy()
    df_global = df_global[["etiqueta","tecnologia","fase","inicio","fin","duracion_ms","duracion_hms"]]

    # 2) Tiempos (usar primer y último timestamp del log)
    if (log_start is None) or (log_end is None):
        df_tiempos = pd.DataFrame(columns=["Tecnología","Inicio","Fin","Duración (ms)","Duración"])
    else:
        total_ms = int((log_end - log_start).total_seconds() * 1000)
        df_tiempos = pd.DataFrame([{
            "Tecnología": "AS400",
            "Inicio": log_start,
            "Fin": log_end,
            "Duración (ms)": total_ms,
            "Duración": _format_hms_from_ms(total_ms),
        }])

    # 3) Etiquetas (una fila por tabla descargada)
    if df_events.empty:
        df_etq = pd.DataFrame(columns=["Numero etiqueta","Tecnologia","Inicio","Fin","Duración"])
    else:
        tmp = df_events.copy()
        tmp["Duración"] = tmp["duracion_ms"].apply(_format_hms_from_ms)
        tmp = tmp.rename(columns={
            "etiqueta":"Numero etiqueta",
            "tecnologia":"Tecnologia",
            "inicio":"Inicio",
            "fin":"Fin",
        })
        df_etq = tmp[["Numero etiqueta","Tecnologia","Inicio","Fin","Duración"]]

    # 4) Medias Tecnologia (media por tecnología AS400, usando per-table durations)
    if df_events.empty:
        df_medias = pd.DataFrame(columns=[
            "Tecnología","Número de etiquetas","Suma total (ms)","Media (ms)","Media (h:m:s)"
        ])
    else:
        grp = df_events.groupby("tecnologia").agg(
            **{"Número de etiquetas": ("etiqueta","nunique"),
               "Suma total (ms)": ("duracion_ms","sum")}
        ).reset_index().rename(columns={"tecnologia":"Tecnología"})
        grp["Media (ms)"] = (grp["Suma total (ms)"] / grp["Número de etiquetas"]).round().astype("Int64")
        grp["Media (h:m:s)"] = grp["Media (ms)"].apply(lambda ms: _format_hms_from_ms(ms if pd.notna(ms) else 0))
        df_medias = grp[["Tecnología","Número de etiquetas","Suma total (ms)","Media (ms)","Media (h:m:s)"]]

    return {
        "GlobalData": df_global,
        "Tiempos": df_tiempos,
        "Etiquetas": df_etq,
        "Medias Tecnologia": df_medias,
    }

def _write_excel(base_html: Path, sheets: dict):
    out_name = f"{base_html.stem}_METRICAS.xlsx"
    out_path = base_html.with_name(out_name)
    with pd.ExcelWriter(out_path, engine="xlsxwriter", datetime_format="yyyy-mm-dd hh:mm:ss") as xw:
        for sheet_name, df in sheets.items():
            df.to_excel(xw, index=False, sheet_name=sheet_name)
            # Ajustar anchos básicos
            ws = xw.sheets[sheet_name]
            for i, col in enumerate(df.columns):
                width = max(12, min(40, int(df[col].astype(str).str.len().max() if not df.empty else 12) + 2))
                ws.set_column(i, i, width)
    return out_path

def process_path(input_path: Path):
    if input_path.is_file():
        with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
            html_text = f.read()
        df_events, log_start, log_end = parse_table_download_console(html_text, proyecto="PROD_TD")
        sheets = _build_sheets(df_events, log_start, log_end)
        out = _write_excel(input_path, sheets)
        print(f"[OK] Generado: {out}")
    elif input_path.is_dir():
        htmls = sorted([p for p in input_path.glob("*.html")])
        if not htmls:
            print("[WARN] No se encontraron .html en el directorio.")
            return
        for p in htmls:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                html_text = f.read()
            df_events, log_start, log_end = parse_table_download_console(html_text, proyecto="PROD_TD")
            sheets = _build_sheets(df_events, log_start, log_end)
            out = _write_excel(p, sheets)
            print(f"[OK] Generado: {out}")
    else:
        print("[ERROR] Ruta no válida:", input_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python parser_table_download.py <ruta a HTML o directorio>")
        sys.exit(2)
    process_path(Path(sys.argv[1]))
