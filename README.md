# Hub Financiero · Streamlit App

Aplicación modular de gestión financiera conectada a Google Sheets.

## Módulos incluidos
| Módulo | Estado | Descripción |
|---|---|---|
| 📅 Eventos Financieros | ✅ Activo | CRUD completo · línea de tiempo · filtros |
| 💳 Líneas de Crédito | 🚧 Planificado | Tasas, plazos, condiciones |
| 🗓️ Calendario Propio | 🚧 Planificado | Eventos internos del equipo |
| 🗺️ Mapa de Actores | 🚧 Planificado | Ecosistema de stakeholders |

## Instalación rápida

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configuración de Google Sheets

1. Creá un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitá **Google Sheets API** y **Google Drive API**
3. Creá una **Cuenta de servicio** → descargá el JSON
4. Copiá `.streamlit/secrets.toml.template` → `.streamlit/secrets.toml`
5. Pegá los valores del JSON en el archivo
6. Compartí la hoja con el `client_email` como **Editor**

## Deploy en Streamlit Community Cloud

1. Subí el repo a GitHub
2. En [share.streamlit.io](https://share.streamlit.io) → New app → seleccioná `app.py`
3. En **Secrets** pegá el contenido de tu `secrets.toml`
4. Deploy 🚀

## Estructura del proyecto

```
financial_hub/
├── app.py                     # Entrada principal + navegación
├── requirements.txt
├── .streamlit/
│   ├── config.toml            # Tema visual
│   └── secrets.toml           # Credenciales GCP (no commitear)
└── modules/
    ├── __init__.py
    ├── data_connector.py      # Lógica Google Sheets (CRUD)
    ├── eventos.py             # Módulo Eventos Financieros
    └── coming_soon.py         # Placeholder para módulos futuros
```

## Cómo agregar un nuevo módulo

1. Creá `modules/mi_modulo.py` con una función `render()`
2. En `app.py`, agregá la entrada al dict `modules` en `sidebar_nav()`
3. Agregá el `elif` correspondiente en `main()`
4. El módulo hereda automáticamente el tema y estilos globales
