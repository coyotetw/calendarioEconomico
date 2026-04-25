"""
modules/eventos.py
──────────────────
Módulo de Eventos Financieros con CRUD completo.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
import html as _h
import html as html_lib

from modules.data_connector import (
    load_eventos, append_evento, delete_evento
)

STATUS_OPTIONS = ["Próximo", "✓ Realizado", "Cancelado", "En curso"]

STATUS_BADGE = {
    "✓ Realizado": ("badge-done",   "✓ Realizado"),
    "Próximo":     ("badge-next",   "Próximo"),
    "En curso":    ("badge-next",   "En curso"),
    "Cancelado":   ("badge-unknown","Cancelado"),
}

STATUS_COLOR = {
    "✓ Realizado": ("#E1F5EE", "#085041"),
    "Próximo":     ("#E6F1FB", "#0C447C"),
    "En curso":    ("#EEEDFE", "#3C3489"),
    "Cancelado":   ("#F1EFE8", "#5F5E5A"),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _badge(status: str) -> str:
    cls, label = STATUS_BADGE.get(status, ("badge-unknown", status or "—"))
    return f'<span class="badge {cls}">{label}</span>'


def _fmt_date(val) -> str:
    if pd.isna(val) or val is None:
        return "—"
    try:
        return pd.Timestamp(val).strftime("%d/%m/%Y")
    except Exception:
        return str(val)


# ── KPI cards ─────────────────────────────────────────────────────────────────

def _kpis(df: pd.DataFrame):
    total      = len(df)
    proximos   = len(df[df["Estado"].str.strip() == "Próximo"])
    realizados = len(df[df["Estado"].str.strip() == "✓ Realizado"])
    otros      = total - proximos - realizados

    cards = [
        ("blue",  total,      "Total eventos"),
        ("amber", proximos,   "Próximos"),
        ("green", realizados, "Realizados"),
        ("gray",  otros,      "Otros"),
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


# ── Timeline (tarjetas agrupadas por mes) ─────────────────────────────────────

def _make_card(dia, nombre, detalle, estado, bg_card="#ffffff"):
    bg, fg = STATUS_COLOR.get(estado, ("#F1EFE8", "#5F5E5A"))
    e_nombre  = _h.escape(str(nombre))
    e_detalle = _h.escape(str(detalle))
    e_estado  = _h.escape(str(estado))
    e_dia     = _h.escape(str(dia))
    det = (
        f'<div style="font-size:11px;color:#94a3b8;margin-top:2px;'
        f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{e_detalle}</div>'
    ) if detalle else ""
    return (
        f'<div style="background:{bg_card};border:0.5px solid #e2e8f0;'
        f'border-radius:10px;padding:10px 14px;display:flex;align-items:center;'
        f'gap:12px;margin-bottom:6px;">'
        f'<div style="min-width:24px;font-size:13px;font-weight:500;color:#94a3b8;'
        f'text-align:center;flex-shrink:0;">{e_dia}</div>'
        f'<div style="flex:1;min-width:0;">'
        f'<div style="font-size:13px;font-weight:500;color:#1e293b;'
        f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{e_nombre}</div>'
        f'{det}</div>'
        f'<span style="background:{bg};color:{fg};font-size:11px;padding:3px 10px;'
        f'border-radius:99px;white-space:nowrap;flex-shrink:0;">{e_estado}</span>'
        f'</div>'
    )


def _timeline_chart(df: pd.DataFrame):
    if df.empty:
        st.info("No hay eventos para mostrar.")
        return

    dated   = df[df["Fecha"].notna()].copy()
    undated = df[df["Fecha"].isna()].copy()

    if not dated.empty:
        dated["Fecha"] = pd.to_datetime(dated["Fecha"])
        dated = dated.sort_values("Fecha").reset_index(drop=True)

    partes = []

    if not dated.empty:
        meses    = dated.groupby(dated["Fecha"].dt.to_period("M"), sort=True)
        mes_keys = list(meses.groups.keys())

        for mi, mes_key in enumerate(mes_keys):
            grupo     = meses.get_group(mes_key).sort_values("Fecha")
            mes_label = _h.escape(grupo.iloc[0]["Fecha"].strftime("%b %Y").capitalize())
            es_ultimo = (mi == len(mes_keys) - 1) and undated.empty
            conector  = "" if es_ultimo else "<div style=\'width:1.5px;flex:1;background:#e2e8f0;min-height:16px;\'></div>"

            cards = ""
            for _, row in grupo.iterrows():
                estado  = str(row.get("Estado", "")).strip()
                dia     = pd.Timestamp(row["Fecha"]).strftime("%d")
                nombre  = str(row.get("Nombre del evento", ""))
                org     = str(row.get("Organizador", "") or "").strip()
                lugar   = str(row.get("Lugar / Modalidad", "") or "").strip()
                detalle = " · ".join(filter(None, [org, lugar]))
                cards  += _make_card(dia, nombre, detalle, estado)

            partes.append(
                '<div style="display:flex;gap:16px;align-items:flex-start;">' +
                '<div style="min-width:72px;padding-top:5px;text-align:right;flex-shrink:0;">' +
                f'<span style="font-size:11px;font-weight:500;color:#94a3b8;">{mes_label}</span>' +
                '</div>' +
                '<div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;">' +
                '<div style="width:9px;height:9px;border-radius:50%;background:#378ADD;margin-top:5px;flex-shrink:0;"></div>' +
                conector +
                '</div>' +
                '<div style="flex:1;min-width:0;padding-bottom:14px;">' +
                cards +
                '</div></div>'
            )

    if not undated.empty:
        cards = ""
        for _, row in undated.iterrows():
            estado  = str(row.get("Estado", "")).strip()
            nombre  = str(row.get("Nombre del evento", ""))
            org     = str(row.get("Organizador", "") or "").strip()
            lugar   = str(row.get("Lugar / Modalidad", "") or "").strip()
            detalle = " · ".join(filter(None, [org, lugar]))
            cards  += _make_card("—", nombre, detalle, estado, bg_card="#f8fafc")

        partes.append(
            '<div style="display:flex;gap:16px;align-items:flex-start;">' +
            '<div style="min-width:72px;padding-top:5px;text-align:right;flex-shrink:0;">' +
            '<span style="font-size:11px;font-weight:500;color:#cbd5e1;">Sin fecha</span>' +
            '</div>' +
            '<div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;">' +
            '<div style="width:9px;height:9px;border-radius:50%;background:#cbd5e1;margin-top:5px;"></div>' +
            '</div>' +
            '<div style="flex:1;min-width:0;padding-bottom:4px;">' +
            cards +
            '</div></div>'
        )

    html_out = (
        '<div style="display:flex;flex-direction:column;gap:0;padding:4px 0;">' +
        "".join(partes) +
        '</div>'
    )
    st.markdown(html_out, unsafe_allow_html=True)


# ── Tabla de eventos ──────────────────────────────────────────────────────────

def _render_table(df: pd.DataFrame, filtered_indices):
    """Render the events table with delete button only."""
    if not filtered_indices:
        st.info("No hay eventos para mostrar con los filtros actuales.")
        return

    # Header
    cols = st.columns([1.2, 3.5, 2, 2, 1.5, 0.8])
    for col, h in zip(cols, ["Fecha", "Evento", "Organizador", "Lugar", "Estado", "🗑️"]):
        col.markdown(f"**{h}**")
    st.markdown("<hr style='margin:0.3rem 0 0.5rem;border-color:#e2e8f0'>", unsafe_allow_html=True)

    for real_i in filtered_indices:
        row = df.iloc[real_i]
        c1, c2, c3, c4, c5, c6 = st.columns([1.2, 3.5, 2, 2, 1.5, 0.8])
        c1.markdown(f"<small>{_fmt_date(row['Fecha'])}</small>", unsafe_allow_html=True)
        c2.markdown(f"<small><b>{row['Nombre del evento']}</b></small>", unsafe_allow_html=True)
        c3.markdown(f"<small>{row['Organizador'] or '—'}</small>", unsafe_allow_html=True)
        c4.markdown(f"<small>{row['Lugar / Modalidad'] or '—'}</small>", unsafe_allow_html=True)
        c5.markdown(_badge(str(row["Estado"])), unsafe_allow_html=True)

        if c6.button("🗑️", key=f"del_{real_i}", help="Eliminar"):
            st.session_state["confirm_delete"] = real_i
            st.rerun()

    # Confirmar eliminación
    if "confirm_delete" in st.session_state:
        idx  = st.session_state["confirm_delete"]
        name = df.iloc[idx]["Nombre del evento"]
        st.warning(f"¿Eliminar **{name}**?")
        col_y, col_n = st.columns(2)
        if col_y.button("✅ Sí, eliminar", key="confirm_yes"):
            ok = delete_evento(idx)
            del st.session_state["confirm_delete"]
            st.success("Evento eliminado.") if ok else st.error("No se pudo eliminar (sin credenciales de escritura).")
            st.rerun()
        if col_n.button("❌ Cancelar", key="confirm_no"):
            del st.session_state["confirm_delete"]
            st.rerun()


# ── Formulario de nuevo evento ────────────────────────────────────────────────

def _event_form(df: pd.DataFrame):
    """Formulario solo para agregar nuevos eventos."""
    st.markdown("#### ➕ Nuevo evento")

    with st.form("event_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("📅 Fecha", value=None, format="DD/MM/YYYY")
        with col2:
            estado = st.selectbox("🔖 Estado", STATUS_OPTIONS, index=0)

        nombre = st.text_input("📌 Nombre del evento *", max_chars=200)

        col3, col4 = st.columns(2)
        with col3:
            organizador = st.text_input("🏢 Organizador", max_chars=120)
        with col4:
            lugar = st.text_input("📍 Lugar / Modalidad", max_chars=120)

        enfoque  = st.text_area("🎯 Enfoque principal", height=80, max_chars=500)
        mas_info = st.text_input("🔗 Más info (URL o referencia)", max_chars=200)

        col_submit, col_cancel = st.columns([1, 3])
        submitted = col_submit.form_submit_button("➕ Agregar", type="primary", use_container_width=True)
        cancelled = col_cancel.form_submit_button("Cancelar")

    if submitted:
        if not nombre.strip():
            st.error("El nombre del evento es obligatorio.")
            return

        row = {
            "Fecha":             fecha.strftime("%Y-%m-%d") if fecha else "",
            "Nombre del evento": nombre.strip(),
            "Organizador":       organizador.strip(),
            "Lugar / Modalidad": lugar.strip(),
            "Enfoque principal": enfoque.strip(),
            "Más info":          mas_info.strip(),
            "Estado":            estado,
        }
        ok = append_evento(row)
        if ok:
            st.success("Evento agregado correctamente.")
        else:
            st.warning("No se pudo guardar (sin credenciales de escritura en Google Sheets).")

        st.session_state["show_form"] = None
        st.rerun()

    if cancelled:
        st.session_state["show_form"] = None
        st.rerun()


# ── Render principal ──────────────────────────────────────────────────────────

def render():
    # Encabezado
    st.markdown("""
    <div class="page-header">
        <h1>📅 Eventos Financieros</h1>
        <p>Seguimiento de eventos del sector financiero, garantías y PyMEs · Fuente: Google Sheets</p>
    </div>
    """, unsafe_allow_html=True)

    # Cargar datos
    df = load_eventos()

    # Botón de refresco manual
    col_ref, _ = st.columns([1, 5])
    with col_ref:
        if st.button("🔄 Actualizar datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # KPIs
    _kpis(df)

    # Timeline de tarjetas
    with st.container():
        st.markdown('<div class="table-wrapper"><div class="table-title">📅 Calendario de eventos</div>', unsafe_allow_html=True)
        _timeline_chart(df)
        st.markdown("</div>", unsafe_allow_html=True)

    # Filtros + botón nuevo evento
    st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)

    f1, f2, f3, _, btn_col = st.columns([2, 1.5, 1.5, 0.5, 1.5])
    with f1:
        search = st.text_input("🔍 Buscar", placeholder="Evento, organizador, lugar…", label_visibility="collapsed")
    with f2:
        status_filter = st.multiselect(
            "Estado",
            options=STATUS_OPTIONS,
            default=[],
            placeholder="Todos los estados",
            label_visibility="collapsed",
        )
    with f3:
        year_options = ["Todos los años"]
        dated_df = df[df["Fecha"].notna()]
        if not dated_df.empty:
            years = sorted(pd.to_datetime(dated_df["Fecha"]).dt.year.unique(), reverse=True)
            year_options += [str(y) for y in years]
        year_filter = st.selectbox("Año", year_options, label_visibility="collapsed")
    with btn_col:
        if st.button("➕ Nuevo evento", type="primary", use_container_width=True):
            st.session_state["show_form"] = "new"
            st.rerun()

    # Aplicar filtros
    mask = pd.Series([True] * len(df), index=df.index)
    if search:
        q = search.lower()
        mask &= (
            df["Nombre del evento"].str.lower().str.contains(q, na=False) |
            df["Organizador"].str.lower().str.contains(q, na=False)       |
            df["Lugar / Modalidad"].str.lower().str.contains(q, na=False)
        )
    if status_filter:
        mask &= df["Estado"].isin(status_filter)
    if year_filter != "Todos los años":
        mask &= (
            pd.to_datetime(df["Fecha"], errors="coerce")
            .dt.year.astype("Int64").astype(str) == year_filter
        )

    filtered_indices = list(df[mask].index)

    # Tabla
    st.markdown(
        f"<div class='table-title'>📋 Eventos "
        f"<span style='font-weight:400;color:#64748b;'>({len(filtered_indices)} registros)</span></div>",
        unsafe_allow_html=True,
    )
    _render_table(df, filtered_indices)
    st.markdown("</div>", unsafe_allow_html=True)

    # Formulario de nuevo evento
    if st.session_state.get("show_form") == "new":
        st.markdown("---")
        st.markdown('<div class="form-panel">', unsafe_allow_html=True)
        _event_form(df)
        st.markdown("</div>", unsafe_allow_html=True)

    # Info de configuración
    with st.expander("ℹ️ Configuración de conexión a Google Sheets"):
        st.markdown("""
**Para habilitar escritura en Google Sheets**, agregá tus credenciales en `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "TU_PROYECTO"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "tu-cuenta@tu-proyecto.iam.gserviceaccount.com"
client_id = "..."
token_uri = "https://oauth2.googleapis.com/token"
```

Y compartí la hoja de cálculo con el `client_email` como **Editor**.  
Sin credenciales, la app opera en **modo lectura** (sin escritura).
        """)
