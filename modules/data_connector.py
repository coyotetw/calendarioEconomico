"""
data_connector.py
─────────────────
Handles all read/write operations against Google Sheets.
Falls back to a local CSV cache when credentials are not configured.
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

SHEET_ID   = "1BDan8C8ZMtVJgtN2EW3TB4LCmboK8rcN5SI7oqMkqlU"
SHEET_NAME = "Eventos"

# ── Column schema (must match the sheet exactly) ─────────────────────────────
COLUMNS = ["Fecha", "Nombre del evento", "Organizador",
           "Lugar / Modalidad", "Enfoque principal", "Más info", "Estado"]


def _get_gc():
    """Return an authenticated gspread client, or None if not configured."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # Credentials can be stored as a JSON string in st.secrets["gcp_service_account"]
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


@st.cache_data(ttl=60, show_spinner=False)
def load_eventos() -> pd.DataFrame:
    """Load events from Google Sheets (with 60 s cache)."""
    gc = _get_gc()

    if gc:
        try:
            sh = gc.open_by_key(SHEET_ID)
            ws = sh.worksheet(SHEET_NAME)
            records = ws.get_all_records()
            df = pd.DataFrame(records)
            if df.empty:
                return _empty_df()
            # Normalise column names
            df.columns = [c.strip() for c in df.columns]
            # Ensure all expected columns exist
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            df = df[COLUMNS].copy()
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
            return df
        except Exception as e:
            st.warning(f"⚠️ No se pudo leer Google Sheets: {e}. Mostrando datos locales.")

    # ── Fallback: demo data ──────────────────────────────────────────────────
    return _demo_df()


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNS)


def _demo_df() -> pd.DataFrame:
    rows = [
        {
            "Fecha": pd.Timestamp("2026-03-10"),
            "Nombre del evento": "Certificación de Idoneidad – SGR (inicio de clases)",
            "Organizador": "CASFOG",
            "Lugar / Modalidad": "Virtual / Intensivo",
            "Enfoque principal": "Marco regulatorio SGR, Mercado de Capitales PyME, lavado de dinero",
            "Más info": "casfog.com.ar",
            "Estado": "✓ Realizado",
        },
        {
            "Fecha": pd.NaT,
            "Nombre del evento": "IV Foro Provincial de Garantías y II Foro de la Región Litoral",
            "Organizador": "FOGAMI, FONRED, FoGaCh, FOGAER, FOGAFE, CFI",
            "Lugar / Modalidad": "Posadas, Misiones",
            "Enfoque principal": "Participación de más de diez fondos de garantía provinciales",
            "Más info": "",
            "Estado": "✓ Realizado",
        },
        {
            "Fecha": pd.Timestamp("2026-04-28"),
            "Nombre del evento": "EXPO EFI 2026 – Congreso de Economía, Finanzas e Inversiones",
            "Organizador": "Invecq + CASFOG + entidades",
            "Lugar / Modalidad": "CABA – Centro de Convenciones (CEC)",
            "Enfoque principal": "Economía, finanzas, inversiones, PyMEs, mercado de capitales, Agro",
            "Más info": "expoefi.com",
            "Estado": "Próximo",
        },
        {
            "Fecha": pd.Timestamp("2026-04-18"),
            "Nombre del evento": "Inicio de Inscripción Programa INNOVA CFI",
            "Organizador": "CFI",
            "Lugar / Modalidad": "Virtual",
            "Enfoque principal": "Impulsar ecosistema de innovación. Capitalizar startups y PyMEs nacientes.",
            "Más info": "https://innova.cfi.org.ar/",
            "Estado": "Próximo",
        },
        {
            "Fecha": pd.Timestamp("2026-05-26"),
            "Nombre del evento": "Venture Capital World Summit",
            "Organizador": "Regus / Global",
            "Lugar / Modalidad": "Buenos Aires",
            "Enfoque principal": "Inversión ángel y capital de riesgo para proyectos locales.",
            "Más info": "",
            "Estado": "Próximo",
        },
        {
            "Fecha": pd.Timestamp("2026-08-27"),
            "Nombre del evento": "eCommerce Day Argentina 2026",
            "Organizador": "CACE",
            "Lugar / Modalidad": "CABA – Centro de Convenciones (CEC)",
            "Enfoque principal": "IA como tejido conectivo del comercio unificado y el crecimiento escalable.",
            "Más info": "https://ecommerceday.org.ar/2026/",
            "Estado": "Próximo",
        },
        {
            "Fecha": pd.Timestamp("2026-09-17"),
            "Nombre del evento": "XXIX Foro Iberoamericano de Garantías y Financiamiento PyME – REGAR",
            "Organizador": "REGAR",
            "Lugar / Modalidad": "Arequipa, Perú",
            "Enfoque principal": "Transformación de sistemas de garantías en entorno global cambiante.",
            "Más info": "https://redegarantias.com/foro-peru-inicio/",
            "Estado": "Próximo",
        },
    ]
    return pd.DataFrame(rows, columns=COLUMNS)


# ── Write helpers ─────────────────────────────────────────────────────────────

def _get_worksheet():
    gc = _get_gc()
    if not gc:
        return None
    sh = gc.open_by_key(SHEET_ID)
    return sh.worksheet(SHEET_NAME)


def _refresh():
    """Clear cache so next load re-fetches."""
    load_eventos.clear()


def append_evento(row: dict) -> bool:
    """Add a new row to the sheet."""
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
    """
    Update an existing row. row_index is 0-based relative to data rows
    (the sheet has a header at row 1, so data starts at row 2).
    """
    ws = _get_worksheet()
    if not ws:
        return False
    try:
        sheet_row = row_index + 2  # +1 header, +1 for 1-based index
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
    """Delete a row. row_index is 0-based relative to data rows."""
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
