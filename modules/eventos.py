"""
modules/eventos.py
──────────────────
Módulo de Eventos Financieros con CRUD completo.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
import plotly.graph_objects as go

from modules.data_connector import (
    load_eventos, append_evento, update_evento, delete_evento
)

STATUS_OPTIONS = ["Próximo", "✓ Realizado", "Cancelado", "En curso"]

STATUS_BADGE = {
    "✓ Realizado": ("badge-done",  "✓ Realizado"),
    "Próximo":     ("badge-next",  "Próximo"),
    "En curso":    ("badge-next",  "En curso"),
    "Cancelado":   ("badge-unknown", "Cancelado"),
}


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


def _timeline_chart(df: pd.DataFrame):
    dated = df[df["Fecha"].notna()].copy()
    if dated.empty:
        return
    dated["Fecha"] = pd.to_datetime(dated["Fecha"])
    dated = dated.sort_values("Fecha")

    color_map = {
        "✓ Realizado": "#059669",
        "Próximo":     "#0f6cbd",
        "En curso":    "#7c3aed",
        "Cancelado":   "#9ca3af",
    }
    dated["Color"]       = dated["Estado"].map(color_map).fillna("#9ca3af")
    dated["Fecha_str"]   = dated["Fecha"].dt.strftime("%d/%m/%Y")
    dated["Nombre_corto"] = dated["Nombre del evento"].str[:45] + "…"

    fig = go.Figure()
    for estado, group in dated.groupby("Estado"):
        fig.add_trace(go.Scatter(
            x=group["Fecha"],
            y=[estado] * len(group),
            mode="markers+text",
            marker=dict(size=16, color=color_map.get(estado, "#9ca3af"), symbol="circle"),
            text=group["Nombre_corto"],
            textposition="top center",
            textfont=dict(size=9),
            name=estado,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "📍 %{customdata[2]}<br>"
                "<extra></extra>"
            ),
            customdata=list(zip(
                group["Nombre del evento"],
                group["Fecha_str"],
                group["Lugar / Modalidad"].fillna("—"),
            )),
        ))

    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        font=dict(family="Inter, sans-serif"),
    )
    # use width='stretch' (replaces deprecated use_container_width=True)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def _render_table(df: pd.DataFrame, filtered_indices):
    """Render the events table with action buttons."""
    if df.empty:
        st.info("No hay eventos para mostrar con los filtros actuales.")
        return

    # Header
    cols = st.columns([1.2, 3.5, 2, 2, 1.3, 0.8, 0.8])
    headers = ["Fecha", "Evento", "Organizador", "Lugar", "Estado", "✏️", "🗑️"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")
    st.markdown("<hr style='margin:0.3rem 0 0.5rem;border-color:#e2e8f0'>", unsafe_allow_html=True)

    for display_i, real_i in enumerate(filtered_indices):
        row = df.iloc[real_i]
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.2, 3.5, 2, 2, 1.3, 0.8, 0.8])
        c1.markdown(f"<small>{_fmt_date(row['Fecha'])}</small>", unsafe_allow_html=True)
        c2.markdown(f"<small><b>{row['Nombre del evento']}</b></small>", unsafe_allow_html=True)
        c3.markdown(f"<small>{row['Organizador'] or '—'}</small>", unsafe_allow_html=True)
        c4.markdown(f"<small>{row['Lugar / Modalidad'] or '—'}</small>", unsafe_allow_html=True)
        c5.markdown(_badge(str(row["Estado"])), unsafe_allow_html=True)

        if c6.button("✏️", key=f"edit_{real_i}", help="Editar"):
            st.session_state["edit_idx"]  = real_i
            st.session_state["show_form"] = "edit"
            st.rerun()

        if c7.button("🗑️", key=f"del_{real_i}", help="Eliminar"):
            st.session_state["confirm_delete"] = real_i
            st.rerun()

    # Confirm delete dialog
    if "confirm_delete" in st.session_state:
        idx  = st.session_state["confirm_delete"]
        name = df.iloc[idx]["Nombre del evento"]
        st.warning(f"¿Eliminar **{name}**?")
        col_y, col_n = st.columns(2)
        if col_y.button("✅ Sí, eliminar", key="confirm_yes"):
            ok = delete_evento(idx)
            del st.session_state["confirm_delete"]
            if ok:
                st.success("Evento eliminado.")
            else:
                st.error("No se pudo eliminar (modo demo o sin credenciales).")
            st.rerun()
        if col_n.button("❌ Cancelar", key="confirm_no"):
            del st.session_state["confirm_delete"]
            st.rerun()


def _event_form(df: pd.DataFrame, mode: str = "new", idx: int = None):
    """Render create / edit form."""
    is_edit  = mode == "edit" and idx is not None
    existing = df.iloc[idx] if is_edit else None

    st.markdown(f"#### {'✏️ Editar evento' if is_edit else '➕ Nuevo evento'}")

    def _get(field, default=""):
        return existing[field] if is_edit and pd.notna(existing[field]) else default

    with st.form("event_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            raw_date = _get("Fecha")
            try:
                default_date = pd.Timestamp(raw_date).date() if raw_date and raw_date != "" else None
            except Exception:
                default_date = None
            fecha = st.date_input("📅 Fecha", value=default_date, format="DD/MM/YYYY")

        with col2:
            estado = st.selectbox(
                "🔖 Estado",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(_get("Estado", "Próximo"))
                      if _get("Estado", "Próximo") in STATUS_OPTIONS else 0,
            )

        nombre = st.text_input("📌 Nombre del evento *", value=_get("Nombre del evento"), max_chars=200)

        col3, col4 = st.columns(2)
        with col3:
            organizador = st.text_input("🏢 Organizador", value=_get("Organizador"), max_chars=120)
        with col4:
            lugar = st.text_input("📍 Lugar / Modalidad", value=_get("Lugar / Modalidad"), max_chars=120)

        enfoque  = st.text_area("🎯 Enfoque principal", value=_get("Enfoque principal"), height=80, max_chars=500)
        mas_info = st.text_input("🔗 Más info (URL o referencia)", value=_get("Más info"), max_chars=200)

        col_submit, col_cancel = st.columns([1, 3])
        submitted = col_submit.form_submit_button(
            "💾 Guardar" if is_edit else "➕ Agregar",
            type="primary",
            use_container_width=True,
        )
        cancelled = col_cancel.form_submit_button("Cancelar", use_container_width=False)

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

        if is_edit:
            ok  = update_evento(idx, row)
            msg = "Evento actualizado." if ok else "No se pudo actualizar (modo demo)."
        else:
            ok  = append_evento(row)
            msg = "Evento agregado." if ok else "No se pudo guardar (modo demo)."

        if ok:
            st.success(msg)
        else:
            st.warning(msg)

        st.session_state["show_form"] = None
        st.session_state["edit_idx"]  = None
        st.rerun()

    if cancelled:
        st.session_state["show_form"] = None
        st.session_state["edit_idx"]  = None
        st.rerun()


def render():
    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-header">
        <h1>📅 Eventos Financieros</h1>
        <p>Seguimiento de eventos del sector financiero, garantías y PyMEs · Fuente: Google Sheets</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load data ─────────────────────────────────────────────────────────────
    df = load_eventos()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    _kpis(df)

    # ── Timeline ──────────────────────────────────────────────────────────────
    with st.container():
        st.markdown('<div class="table-wrapper"><div class="table-title">📈 Línea de tiempo</div>', unsafe_allow_html=True)
        _timeline_chart(df)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Filters + Actions bar ─────────────────────────────────────────────────
    st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)

    f1, f2, f3, _, btn_col = st.columns([2, 1.5, 1.5, 0.5, 1.5])
    with f1:
        search = st.text_input("🔍 Buscar", placeholder="Evento, organizador, lugar…", label_visibility="collapsed")
    with f2:
        status_filter = st.multiselect(
            "Estado",
            options=STATUS_OPTIONS + [""],
            default=[],
            placeholder="Todos los estados",
            label_visibility="collapsed",
        )
    with f3:
        year_options = ["Todos los años"]
        dated = df[df["Fecha"].notna()]
        if not dated.empty:
            years = sorted(pd.to_datetime(dated["Fecha"]).dt.year.unique(), reverse=True)
            year_options += [str(y) for y in years]
        year_filter = st.selectbox("Año", year_options, label_visibility="collapsed")
    with btn_col:
        if st.button("➕ Nuevo evento", type="primary", use_container_width=True):
            st.session_state["show_form"] = "new"
            st.session_state["edit_idx"]  = None
            st.rerun()

    # ── Apply filters ─────────────────────────────────────────────────────────
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
        mask &= pd.to_datetime(df["Fecha"], errors="coerce").dt.year.astype("Int64").astype(str) == year_filter

    filtered_indices = list(df[mask].index)

    # ── Table ─────────────────────────────────────────────────────────────────
    st.markdown(
        f"<div class='table-title'>📋 Eventos "
        f"<span style='font-weight:400;color:#64748b;'>({len(filtered_indices)} registros)</span></div>",
        unsafe_allow_html=True,
    )
    _render_table(df, filtered_indices)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── CRUD Form ─────────────────────────────────────────────────────────────
    show_form = st.session_state.get("show_form")
    edit_idx  = st.session_state.get("edit_idx")

    if show_form:
        st.markdown("---")
        st.markdown('<div class="form-panel">', unsafe_allow_html=True)
        _event_form(df, mode=show_form, idx=edit_idx)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Credentials notice ────────────────────────────────────────────────────
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
Sin credenciales, la app opera en **modo demo** (lectura pública, sin escritura).
        """)
