import streamlit as st

st.set_page_config(
    page_title="Hub Financiero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Shared styles (imported by all modules) ──────────────────────────────────
def inject_styles():
    st.markdown("""
    <style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stRadio label {
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.2s;
        display: block;
    }
    [data-testid="stSidebar"] .stRadio label:hover { background: #334155; }

    /* ── Main background ── */
    .main { background: #f8fafc; }
    .block-container { padding: 2rem 2.5rem; }

    /* ── Page header ── */
    .page-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f6cbd 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 20px rgba(15,108,189,0.3);
    }
    .page-header h1 { font-size: 1.8rem; font-weight: 700; margin: 0; color: white; }
    .page-header p  { margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.95rem; color: white; }

    /* ── KPI Cards ── */
    .kpi-grid { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 140px;
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid;
    }
    .kpi-card.blue  { border-color: #0f6cbd; }
    .kpi-card.green { border-color: #059669; }
    .kpi-card.amber { border-color: #d97706; }
    .kpi-card.gray  { border-color: #6b7280; }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #0f172a; }
    .kpi-label { font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.2rem; }

    /* ── Data table wrapper ── */
    .table-wrapper {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .table-title {
        font-size: 1rem; font-weight: 600; color: #0f172a;
        margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;
    }

    /* ── Status badges ── */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-done    { background: #d1fae5; color: #065f46; }
    .badge-next    { background: #dbeafe; color: #1e40af; }
    .badge-unknown { background: #f1f5f9; color: #475569; }

    /* ── Form panel ── */
    .form-panel {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        padding: 1.5rem;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }

    /* ── Divider ── */
    hr { border-color: #e2e8f0; }

    /* ── Coming soon banner ── */
    .coming-soon {
        background: white;
        border-radius: 16px;
        padding: 4rem 2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        color: #94a3b8;
    }
    .coming-soon .icon { font-size: 3rem; }
    .coming-soon h2 { color: #334155; margin: 1rem 0 0.5rem; }
    </style>
    """, unsafe_allow_html=True)


def sidebar_nav():
    with st.sidebar:
        st.markdown("""
        <div style='padding:1.5rem 1rem 1rem;'>
            <div style='font-size:1.5rem;font-weight:700;letter-spacing:-0.5px;'>
                💼 Hub Financiero
            </div>
            <div style='font-size:0.75rem;opacity:0.6;margin-top:0.2rem;'>Panel de gestión</div>
        </div>
        <hr style='border-color:#334155;margin:0 1rem 1rem;'>
        """, unsafe_allow_html=True)

        modules = {
            "📅  Eventos Financieros": "eventos",
            "📜  Marco Normativo":     "normativa",
            "💳  Líneas de Crédito":   "credito",
            "🗓️  Calendario Propio":    "calendario",
            "🗺️  Mapa de Actores":      "actores",
        }

        choice = st.radio(
            "Módulos",
            list(modules.keys()),
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='padding:0 1rem;font-size:0.7rem;opacity:0.5;'>
            v1.0 · Datos sincronizados con Google Sheets
        </div>
        """, unsafe_allow_html=True)

    return modules[choice]


def main():
    inject_styles()
    page = sidebar_nav()

    if page == "eventos":
        from modules.eventos import render
        render()
    elif page == "credito":
        from modules.coming_soon import render
        render("💳 Líneas de Crédito", "Próximamente podrás gestionar líneas de crédito y sus tasas de interés.", "credito")
    elif page == "normativa":
        from modules.normativa import render
    elif page == "calendario":
        from modules.coming_soon import render
        render("🗓️ Calendario Propio", "Aquí irá el calendario de eventos propios que tenés que atender.", "calendario")
    elif page == "actores":
        from modules.coming_soon import render
        render("🗺️ Mapa de Actores", "Visualizá el ecosistema de actores del sector financiero.", "actores")


# Streamlit Cloud ejecuta el script completo — no usa __main__
main()
