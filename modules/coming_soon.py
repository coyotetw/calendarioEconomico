"""modules/coming_soon.py — Placeholder for modules not yet implemented."""
import streamlit as st


def render(title: str = "Módulo", description: str = "Próximamente", key: str = "cs"):
    st.markdown(f"""
    <div class="page-header">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    <div class="coming-soon">
        <div class="icon">🚧</div>
        <h2>En construcción</h2>
        <p>{description}</p>
        <p style='font-size:0.85rem;margin-top:1.5rem;'>
            Este módulo está planificado como parte del Hub Financiero modular.<br>
            Contactá al administrador para habilitar esta sección.
        </p>
    </div>
    """, unsafe_allow_html=True)
