"""
modules/normativa.py
────────────────────
Módulo de Marco Normativo para Promoción de Inversiones.
Fuente: Google Sheets (mismo Sheet ID que el Excel subido).
"""

import streamlit as st
import pandas as pd
import html as _h

# ── Configuración de fuente ───────────────────────────────────────────────────
SHEET_ID   = "1QwFC-EiyuTSGOYNvJvznDPshWI7Z5Uz1"
SHEET_NAME = "Hoja1"
EXPORT_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
)

COLUMNS = [
    "Ultim.Actual", "Sector", "Provincia", "Estado", "Año",
    "Normativa", "Link a la normativa", "Requisitos/Alcance",
    "Principales Beneficios", "Mínima", "Máxima", "Modalidad",
    "Expira", "Aclaración", "Comentarios adicionales", "Autoridad de Aplicacion",
]

# ── Colores por estado ────────────────────────────────────────────────────────
ESTADO_COLOR = {
    "Vigente":                              ("#E1F5EE", "#085041", "Vigente"),
    "Vigente Sin reglamentar":              ("#FEF9C3", "#78350F", "Sin reglamentar"),
    "Vigente en proceso de Reglamentacion": ("#FEF9C3", "#78350F", "En reglamentación"),
    "Operativa ( sin Fondos)":              ("#E6F1FB", "#0C447C", "Sin fondos"),
    "Expirada":                             ("#FEE2E2", "#7F1D1D", "Expirada"),
    "Derogada ( art. 1° del Decreto N° 339/2025 ": ("#FEE2E2", "#7F1D1D", "Derogada"),
    "Verificar vigencia":                   ("#F1EFE8", "#5F5E5A", "Verificar"),
    "Sin Datos":                            ("#F1EFE8", "#5F5E5A", "Sin datos"),
}

SECTOR_ICON = {
    "Agropecuario":            "🌾",
    "Pesca":                   "🐟",
    "Presca":                  "🐟",
    "Economía del conocimiento":"💡",
    "Energías Renovables":     "⚡",
    "Forestal":                "🌲",
    "Industria":               "🏭",
    "Minería":                 "⛏️",
    "Multisectorial":          "🏢",
    "Turismo":                 "✈️",
}

# ── Carga de datos ────────────────────────────────────────────────────────────

@st.cache_data(ttl=120, show_spinner=False)
def _load_normativa() -> pd.DataFrame:
    try:
        df = pd.read_csv(EXPORT_URL)
        df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[COLUMNS].copy()
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(
            f"❌ No se pudo cargar Google Sheets: {e}\n\n"
            "Asegurate de que la hoja esté compartida con 'Cualquier persona con el enlace puede ver'."
        )
        return pd.DataFrame(columns=COLUMNS)


# ── KPI cards ─────────────────────────────────────────────────────────────────

def _kpis(df: pd.DataFrame):
    total    = len(df)
    vigentes = len(df[df["Estado"].str.strip().str.startswith("Vigente")])
    chubut   = len(df[df["Provincia"].str.strip() == "Chubut"])
    nacion   = len(df[df["Provincia"].str.strip() == "Nacional"])

    cards = [
        ("blue",  total,    "Total normativas"),
        ("green", vigentes, "Vigentes"),
        ("amber", chubut,   "Chubut"),
        ("gray",  nacion,   "Nacionales"),
    ]
    html = '<div class="kpi-grid">'
    for color, val, label in cards:
        html += f"""
        <div class="kpi-card {color}">
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── Badge de estado ───────────────────────────────────────────────────────────

def _estado_badge(estado: str) -> str:
    estado_clean = str(estado).strip()
    bg, fg, label = ESTADO_COLOR.get(
        estado_clean,
        ("#F1EFE8", "#5F5E5A", estado_clean[:18] if estado_clean else "—")
    )
    label_safe = _h.escape(label)
    return (
        f'<span style="background:{bg};color:{fg};font-size:11px;'
        f'padding:3px 10px;border-radius:99px;white-space:nowrap;">'
        f'{label_safe}</span>'
    )


# ── Tabla de normativas ───────────────────────────────────────────────────────

def _render_tabla(df: pd.DataFrame, indices):
    if not indices:
        st.info("No hay normativas para mostrar con los filtros actuales.")
        return

    # Encabezado
    cols = st.columns([0.8, 1, 2.8, 1.2, 1.5, 0.7])
    for col, h in zip(cols, ["Año", "Sector", "Normativa", "Provincia", "Estado", "🔗"]):
        col.markdown(f"**{h}**")
    st.markdown("<hr style='margin:0.3rem 0 0.5rem;border-color:#e2e8f0'>", unsafe_allow_html=True)

    for real_i in indices:
        row = df.iloc[real_i]
        anio     = str(row["Año"]).split(".")[0] if row["Año"] else "—"
        sector   = str(row["Sector"]).strip()
        icono    = SECTOR_ICON.get(sector, "📄")
        normativa = str(row["Normativa"]).strip()
        provincia = str(row["Provincia"]).strip()
        estado   = str(row["Estado"]).strip()
        link     = str(row["Link a la normativa"]).strip()

        c1, c2, c3, c4, c5, c6 = st.columns([0.8, 1, 2.8, 1.2, 1.5, 0.7])
        c1.markdown(f"<small style='color:#64748b;'>{_h.escape(anio)}</small>", unsafe_allow_html=True)
        c2.markdown(f"<small>{icono} {_h.escape(sector)}</small>", unsafe_allow_html=True)
        c3.markdown(f"<small><b>{_h.escape(normativa[:90])}{'…' if len(normativa)>90 else ''}</b></small>", unsafe_allow_html=True)
        c4.markdown(f"<small>{_h.escape(provincia)}</small>", unsafe_allow_html=True)
        c5.markdown(_estado_badge(estado), unsafe_allow_html=True)

        if link and link not in ("", "nan"):
            c6.markdown(
                f'<a href="{_h.escape(link)}" target="_blank" style="font-size:13px;text-decoration:none;">↗</a>',
                unsafe_allow_html=True,
            )

        # Detalle expandible
        with st.expander("Ver detalle", expanded=False):
            cols_det = st.columns(2)
            with cols_det[0]:
                st.markdown("**Requisitos / Alcance**")
                st.markdown(
                    f"<div style='font-size:12px;color:#475569;line-height:1.6;'>"
                    f"{_h.escape(str(row['Requisitos/Alcance']))}</div>",
                    unsafe_allow_html=True,
                )
            with cols_det[1]:
                st.markdown("**Principales Beneficios**")
                st.markdown(
                    f"<div style='font-size:12px;color:#475569;line-height:1.6;'>"
                    f"{_h.escape(str(row['Principales Beneficios']))}</div>",
                    unsafe_allow_html=True,
                )
            extras = []
            if row.get("Autoridad de Aplicacion") and str(row["Autoridad de Aplicacion"]) not in ("", "nan"):
                extras.append(f"**Autoridad:** {row['Autoridad de Aplicacion']}")
            if row.get("Comentarios adicionales") and str(row["Comentarios adicionales"]) not in ("", "nan"):
                extras.append(f"**Comentarios:** {row['Comentarios adicionales']}")
            if row.get("Expira") and str(row["Expira"]) not in ("", "nan"):
                extras.append(f"**Expira:** {row['Expira']}")
            if extras:
                st.markdown(" &nbsp;·&nbsp; ".join(extras))


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    st.markdown("""
    <div class="page-header">
        <h1>📜 Marco Normativo</h1>
        <p>Normativas de promoción de inversiones · Provincia del Chubut y Nacional · Fuente: Google Sheets</p>
    </div>
    """, unsafe_allow_html=True)

    # Refresco
    col_ref, _ = st.columns([1, 5])
    with col_ref:
        if st.button("🔄 Actualizar datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    df = _load_normativa()

    # KPIs
    _kpis(df)

    # ── Filtros ───────────────────────────────────────────────────────────────
    st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns([2, 1.5, 1.5, 1.5])
    with f1:
        search = st.text_input(
            "🔍 Buscar",
            placeholder="Normativa, beneficio, requisito…",
            label_visibility="collapsed",
        )
    with f2:
        sectores_disponibles = sorted(df["Sector"].dropna().unique().tolist())
        sector_filter = st.multiselect(
            "Sector",
            options=sectores_disponibles,
            default=[],
            placeholder="Todos los sectores",
            label_visibility="collapsed",
        )
    with f3:
        provincias = sorted(df["Provincia"].dropna().unique().tolist())
        provincia_filter = st.multiselect(
            "Provincia",
            options=provincias,
            default=[],
            placeholder="Todas las provincias",
            label_visibility="collapsed",
        )
    with f4:
        solo_vigentes = st.toggle("Solo vigentes", value=False)

    # ── Aplicar filtros ───────────────────────────────────────────────────────
    mask = pd.Series([True] * len(df), index=df.index)

    if search:
        q = search.lower()
        mask &= (
            df["Normativa"].str.lower().str.contains(q, na=False) |
            df["Principales Beneficios"].str.lower().str.contains(q, na=False) |
            df["Requisitos/Alcance"].str.lower().str.contains(q, na=False) |
            df["Sector"].str.lower().str.contains(q, na=False)
        )
    if sector_filter:
        mask &= df["Sector"].isin(sector_filter)
    if provincia_filter:
        mask &= df["Provincia"].isin(provincia_filter)
    if solo_vigentes:
        mask &= df["Estado"].str.strip().str.startswith("Vigente")

    filtered_indices = list(df[mask].index)

    # ── Tabla ─────────────────────────────────────────────────────────────────
    st.markdown(
        f"<div class='table-title'>📋 Normativas "
        f"<span style='font-weight:400;color:#64748b;'>({len(filtered_indices)} registros)</span></div>",
        unsafe_allow_html=True,
    )
    _render_tabla(df, filtered_indices)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Info conexión ─────────────────────────────────────────────────────────
    with st.expander("ℹ️ Configuración de fuente de datos"):
        st.markdown(f"""
La normativa se carga desde esta hoja de Google Sheets:

**Sheet ID:** `{SHEET_ID}`  
**Hoja:** `{SHEET_NAME}`

Para que funcione, la hoja debe estar compartida como **"Cualquier persona con el enlace puede ver"**.

URL de exportación usada:
```
{EXPORT_URL}
```
        """)
