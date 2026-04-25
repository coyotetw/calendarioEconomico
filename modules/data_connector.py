"""
data_connector.py
─────────────────
Lee desde Google Sheets vía URL pública de exportación CSV.
No requiere credenciales para lectura.
Escritura disponible si se configuran credenciales de service account.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

SHEET_ID   = "1BDan8C8ZMtVJgtN2EW3TB4LCmboK8rcN5SI7oqMkqlU"
SHEET_NAME = "Eventos"

# URL pública de exportación CSV — no requiere credenciales
# Si tu hoja "Eventos" no es la primera, buscá el gid en la URL al hacer click en la pestaña
EXPORT_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
)

COLUMNS = [
    "Fecha", "Nombre del evento", "Organizador",
    "Lugar / Modalidad", "Enfoque principal", "Más info", "Estado"
]


# ── Autenticación para escritura (opcional) ───────────────────────────────────

def _get_gc():
    """Devuelve cliente gspread autenticado, o None si no hay credenciales."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        elif os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        else:
            return None

        return gspread.authorize(creds)
    except Exception:
        return None


# ── Lectura ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def load_eventos() -> pd.DataFrame:
    """
    Carga eventos desde Google Sheets vía exportación CSV pública.
    Refresca automáticamente cada 60 segundos.
    
    REQUISITO: La hoja debe estar compartida como "Cualquier persona con el enlace puede ver".
    """
    try:
        df = pd.read_csv(EXPORT_URL)

        if df.empty:
            return _empty_df()

        # Limpiar nombres de columnas (espacios extra, BOM, etc.)
        df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]

        # Asegurar que existan todas las columnas esperadas
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""

        df = df[COLUMNS].copy()
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", dayfirst=True)
        df = df.fillna("")
        # Restaurar NaT donde correspondía
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        return df

    except Exception as e:
        st.error(
            f"❌ No se pudo cargar Google Sheets: {e}\n\n"
            "**Solución:** Asegurate de que la hoja esté compartida con "
            "'Cualquier persona con el enlace puede ver'."
        )
        return _empty_df()


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNS)


def _refresh():
    """Limpia el caché para que el próximo load traiga datos frescos."""
    load_eventos.clear()


# ── Escritura (requiere credenciales de service account) ─────────────────────

def _get_worksheet():
    gc = _get_gc()
    if not gc:
        return None
    try:
        sh = gc.open_by_key(SHEET_ID)
        return sh.worksheet(SHEET_NAME)
    except Exception as e:
        st.error(f"Error al conectar con la hoja: {e}")
        return None


def append_evento(row: dict) -> bool:
    """Agrega una fila nueva a la hoja."""
    ws = _get_worksheet()
    if not ws:
        return False
    try:
        fecha_str = row.get("Fecha", "")
        if isinstance(fecha_str, datetime):
            fecha_str = fecha_str.strftime("%Y-%m-%d")
        values = [
            fecha_str,
            row.get("Nombre del evento", ""),
            row.get("Organizador", ""),
            row.get("Lugar / Modalidad", ""),
            row.get("Enfoque principal", ""),
            row.get("Más info", ""),
            row.get("Estado", "Próximo"),
        ]
        ws.append_row(values, value_input_option="USER_ENTERED")
        _refresh()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False


def update_evento(row_index: int, row: dict) -> bool:
    """Actualiza una fila existente. row_index es 0-based."""
    ws = _get_worksheet()
    if not ws:
        return False
    try:
        sheet_row = row_index + 2  # +1 encabezado, +1 índice 1-based
        fecha_str = row.get("Fecha", "")
        if isinstance(fecha_str, datetime):
            fecha_str = fecha_str.strftime("%Y-%m-%d")
        values = [
            fecha_str,
            row.get("Nombre del evento", ""),
            row.get("Organizador", ""),
            row.get("Lugar / Modalidad", ""),
            row.get("Enfoque principal", ""),
            row.get("Más info", ""),
            row.get("Estado", "Próximo"),
        ]
        ws.update(f"A{sheet_row}:G{sheet_row}", [values], value_input_option="USER_ENTERED")
        _refresh()
        return True
    except Exception as e:
        st.error(f"Error al actualizar: {e}")
        return False


def delete_evento(row_index: int) -> bool:
    """Elimina una fila. row_index es 0-based."""
    ws = _get_worksheet()
    if not ws:
        return False
    try:
        sheet_row = row_index + 2
        ws.delete_rows(sheet_row)
        _refresh()
        return True
    except Exception as e:
        st.error(f"Error al eliminar: {e}")
        return False
