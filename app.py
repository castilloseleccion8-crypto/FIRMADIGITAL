"""Buscador de estado de trámite de Firma Digital ENCODE.

Cada persona ingresa su CUIL (o DNI) y ve el estado de su solicitud junto
con un instructivo de qué hacer según el paso en el que se encuentre.

El archivo de datos (Lista_Gral.xlsm) NO se guarda en el repositorio por
contener datos personales. Ver data/README.md para cómo ubicarlo, o usar
el panel de administración en la barra lateral para subirlo desde el
navegador.
"""

from __future__ import annotations

import html
import os
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from instructivos import ENCODE_PORTAL_URL, INSTRUCTIVOS, DEFAULT_INSTRUCTIVO, clasificar_estado

SHEET_NAME = "DATOS"
DATA_PATH = Path(os.environ.get("ENCODE_XLSM_PATH", "data/Lista_Gral.xlsm"))

COL_DNI = "DNI"
COL_SUCURSAL = "SUCURSAL"
COL_CUIL = "CUIL"
COL_BAJA = "BAJA"
COL_NOMBRE_COMPLETO = "Apellido y Nombre"
COL_CONTRASENA = "CONTRASEÑA ENCODE"
COL_PIN = "PIN"
COL_FECHA_SOLICITUD = "FECHA DE SOLICITUD"
COL_OBSERVACIONES = "OBSERVACIONES"
COL_ESTADO_ENCODE = "ESTADO ENCODE"

# Paleta de marca Castillo. Ajustá estos valores si tenés los códigos de
# color exactos del manual de marca.
NAVY = "#1B1464"
NAVY_DARK = "#100B3E"
GOLD = "#FDB714"
GOLD_DARK = "#C98A00"

# Estilo visual por categoría de estado (ver instructivos.py -> "color").
STATUS_STYLES = {
    "gray": {"card": "#8A8FA3", "badge_bg": "#EEF0F4", "badge_text": "#5B6072", "label": "Pendiente de inicio"},
    "blue": {"card": NAVY, "badge_bg": "#E8E7F5", "badge_text": NAVY, "label": "En proceso"},
    "orange": {"card": GOLD_DARK, "badge_bg": "#FFF3D6", "badge_text": "#8A5B00", "label": "Acción requerida"},
    "green": {"card": "#1E8E3E", "badge_bg": "#E6F4EA", "badge_text": "#1E8E3E", "label": "Completado"},
    "red": {"card": "#C5221F", "badge_bg": "#FCE8E6", "badge_text": "#C5221F", "label": "Atención"},
}

st.set_page_config(page_title="Estado Firma Digital ENCODE", layout="centered")


def inyectar_estilos() -> None:
    st.markdown(
        f"""
        <style>
        #MainMenu, footer, header {{ visibility: hidden; }}

        html, body, [class*="css"], .stApp {{
            font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        .stApp {{ background-color: #F4F5FA; }}
        .block-container {{ max-width: 760px; padding-top: 2rem; }}

        .cst-header {{
            background: linear-gradient(135deg, {NAVY} 0%, {NAVY_DARK} 100%);
            border-radius: 14px;
            padding: 30px 34px;
            margin-bottom: 26px;
            border-bottom: 4px solid {GOLD};
            box-shadow: 0 4px 14px rgba(27, 20, 100, 0.18);
        }}
        .cst-brand {{
            color: {GOLD};
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin: 0 0 8px 0;
        }}
        .cst-header h1 {{
            color: #FFFFFF;
            font-size: 25px;
            font-weight: 700;
            margin: 0 0 8px 0;
            line-height: 1.3;
        }}
        .cst-header p {{
            color: #D9D7EF;
            font-size: 14.5px;
            margin: 0;
            line-height: 1.5;
        }}

        div[data-testid="stTextInput"] input {{
            border-radius: 8px;
            border: 1px solid #D7D9E3;
            padding: 0.6rem 0.8rem;
        }}

        div.stButton > button {{
            background-color: {NAVY};
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.55rem 1.6rem;
        }}
        div.stButton > button:hover {{
            background-color: {GOLD};
            color: {NAVY_DARK};
        }}

        .cst-card {{
            background: #FFFFFF;
            border-radius: 14px;
            padding: 26px 30px;
            border-left: 6px solid var(--card-color, {NAVY});
            box-shadow: 0 1px 4px rgba(16, 11, 62, 0.08);
            margin-bottom: 22px;
        }}
        .cst-badge {{
            display: inline-block;
            font-size: 11.5px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 999px;
            background: var(--badge-bg, #EEE);
            color: var(--badge-text, #333);
            margin-bottom: 12px;
        }}
        .cst-card h2 {{ font-size: 20px; margin: 0 0 4px 0; color: #1F2430; }}
        .cst-card .cst-persona {{ color: #667085; font-size: 13.5px; margin: 0 0 14px 0; }}
        .cst-card .cst-resumen {{ font-size: 15px; color: #1F2430; margin: 0 0 6px 0; line-height: 1.5; }}
        .cst-card h3 {{
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #667085;
            margin: 18px 0 8px 0;
        }}
        .cst-card ul, .cst-card ol {{ margin: 0; padding-left: 22px; }}
        .cst-card li {{ margin-bottom: 8px; line-height: 1.5; font-size: 14.5px; color: #1F2430; }}

        .cst-warning {{
            background: #FFF3D6;
            border-left: 4px solid {GOLD_DARK};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            color: #6B4A00;
            margin-bottom: 18px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def solo_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def _limpiar_id(serie: pd.Series) -> pd.Series:
    numerico = pd.to_numeric(serie, errors="coerce").astype("Int64")
    return numerico.astype(str).replace({"<NA>": ""})


@st.cache_data(show_spinner="Cargando datos...")
def cargar_datos(ruta: str, _mtime: float) -> pd.DataFrame:
    df = pd.read_excel(ruta, sheet_name=SHEET_NAME, engine="openpyxl")
    df[COL_DNI] = _limpiar_id(df[COL_DNI])
    df[COL_CUIL] = _limpiar_id(df[COL_CUIL])
    return df


def buscar_persona(df: pd.DataFrame, consulta: str) -> pd.DataFrame:
    digitos = solo_digitos(consulta)
    if not digitos:
        return df.iloc[0:0]
    return df[(df[COL_CUIL] == digitos) | (df[COL_DNI] == digitos)]


def formatear_fecha(valor) -> str | None:
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y")
    return None


def mostrar_galeria(instructivo: dict) -> None:
    carpeta = instructivo.get("galeria")
    pdf_path = instructivo.get("pdf")
    if not carpeta and not pdf_path:
        return

    imagenes = sorted(Path(carpeta).glob("*.png")) if carpeta and Path(carpeta).is_dir() else []

    with st.expander("Ver el paso a paso con capturas de pantalla"):
        if pdf_path and Path(pdf_path).is_file():
            st.download_button(
                "Descargar guía en PDF",
                data=Path(pdf_path).read_bytes(),
                file_name=Path(pdf_path).name,
                mime="application/pdf",
            )
        for i, imagen in enumerate(imagenes, start=1):
            st.image(str(imagen), caption=f"Paso {i}", use_container_width=True)


def mostrar_resultado(fila: pd.Series) -> None:
    nombre = html.escape(str(fila.get(COL_NOMBRE_COMPLETO) or "—"))
    sucursal = html.escape(str(fila.get(COL_SUCURSAL) or "—"))
    estado_original = fila.get(COL_ESTADO_ENCODE)
    categoria = clasificar_estado(estado_original)
    instructivo = INSTRUCTIVOS.get(categoria, DEFAULT_INSTRUCTIVO)
    estilo = STATUS_STYLES.get(instructivo.get("color"), STATUS_STYLES["gray"])

    antes_html = ""
    if instructivo.get("antes"):
        items = "".join(f"<li>{html.escape(item, quote=False)}</li>" for item in instructivo["antes"])
        antes_html = f"<h3>Antes de empezar</h3><ul>{items}</ul>"

    pasos_html = ""
    if instructivo.get("pasos"):
        items = "".join(f"<li>{html.escape(paso, quote=False)}</li>" for paso in instructivo["pasos"])
        pasos_html = f"<h3>¿Qué tengo que hacer?</h3><ol>{items}</ol>"

    # Todo en una sola línea sin indentación: un salto de línea o espacios
    # sueltos dentro del bloque hacen que Streamlit lo interprete como
    # markdown (bloque de código) en lugar de HTML.
    tarjeta = (
        f'<div class="cst-card" style="--card-color:{estilo["card"]}">'
        f'<span class="cst-badge" style="--badge-bg:{estilo["badge_bg"]};--badge-text:{estilo["badge_text"]}">{estilo["label"]}</span>'
        f'<h2>{html.escape(instructivo["titulo"])}</h2>'
        f'<p class="cst-persona">{nombre} · {sucursal}</p>'
        f'<p class="cst-resumen">{html.escape(instructivo["resumen"])}</p>'
        f"{antes_html}{pasos_html}"
        f"</div>"
    )
    st.markdown(tarjeta, unsafe_allow_html=True)

    baja = fila.get(COL_BAJA)
    if baja and str(baja).strip().lower() not in ("no", "nan", ""):
        aviso = (
            '<div class="cst-warning">'
            f'El campo BAJA de esta persona figura como "{html.escape(str(baja))}". '
            "Si ya no trabajás en la empresa, este trámite puede no aplicar: consultá con RRHH."
            "</div>"
        )
        st.markdown(aviso, unsafe_allow_html=True)

    if ENCODE_PORTAL_URL:
        st.link_button("Ir al portal de ENCODE", ENCODE_PORTAL_URL)

    mostrar_galeria(instructivo)

    observaciones = fila.get(COL_OBSERVACIONES)
    fecha_solicitud = formatear_fecha(fila.get(COL_FECHA_SOLICITUD))

    detalles = []
    if fecha_solicitud:
        detalles.append(("Fecha de solicitud", fecha_solicitud))
    if isinstance(observaciones, str) and observaciones.strip():
        detalles.append(("Observaciones", observaciones.strip()))
    detalles.append(("Estado en el sistema", str(estado_original) if pd.notna(estado_original) else "—"))

    with st.expander("Detalle del sistema"):
        for etiqueta, valor in detalles:
            st.markdown(f"**{etiqueta}:** {valor}")

    usuario = fila.get(COL_DNI)
    contrasena = fila.get(COL_CONTRASENA)
    pin = fila.get(COL_PIN)
    if contrasena or pin:
        with st.expander("Mis credenciales para ingresar al portal de ENCODE"):
            st.caption("No las compartas con nadie. Si no las reconocés, avisá a RRHH.")
            st.markdown(f"**Usuario (DNI):** {usuario}")
            if contrasena:
                st.markdown(f"**Contraseña** (para iniciar sesión, con el punto al final): `{contrasena}`")
            if pin:
                st.markdown(f"**PIN** (para el PIN de seguridad, SIN el punto al final): `{pin}`")


def panel_administracion() -> None:
    with st.sidebar.expander("Panel de administración"):
        try:
            admin_password = st.secrets.get("admin_password", "")
        except Exception:
            admin_password = ""
        admin_password = admin_password or os.environ.get("ADMIN_PASSWORD", "")
        if not admin_password:
            st.caption(
                "Para habilitar la carga del Excel desde el navegador, "
                "definí `admin_password` en `.streamlit/secrets.toml` "
                "(o la variable de entorno ADMIN_PASSWORD)."
            )
            return

        clave_ingresada = st.text_input("Contraseña de administrador", type="password")
        if clave_ingresada != admin_password:
            if clave_ingresada:
                st.error("Contraseña incorrecta.")
            return

        st.success("Acceso concedido.")
        archivo = st.file_uploader("Subir nueva versión de Lista_Gral.xlsm", type=["xlsm", "xlsx"])
        if archivo is not None:
            DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            DATA_PATH.write_bytes(archivo.getvalue())
            st.cache_data.clear()
            st.success("Archivo actualizado. Recargando...")
            st.rerun()

        if DATA_PATH.exists() and st.button("Recargar datos (sin subir archivo nuevo)"):
            st.cache_data.clear()
            st.rerun()


def main() -> None:
    inyectar_estilos()

    st.markdown(
        '<div class="cst-header">'
        '<p class="cst-brand">Castillo · Desde 1924</p>'
        "<h1>Estado de mi Firma Digital ENCODE</h1>"
        "<p>Ingresá tu CUIL o DNI para ver en qué paso está tu trámite y qué tenés que hacer para continuarlo.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    panel_administracion()

    if not DATA_PATH.exists():
        st.error(
            f"No se encontró el archivo de datos en `{DATA_PATH}`. "
            "Pedile al administrador que lo suba desde el Panel de administración "
            "(barra lateral) o lo coloque en esa ruta en el servidor."
        )
        return

    mtime = DATA_PATH.stat().st_mtime
    df = cargar_datos(str(DATA_PATH), mtime)
    st.sidebar.caption(f"Datos actualizados: {datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')}")

    consulta = st.text_input("CUIL o DNI", placeholder="Ej: 20-38488471-8")
    buscar = st.button("Buscar", type="primary")

    if not (buscar or consulta):
        return

    digitos = solo_digitos(consulta)
    if not digitos:
        st.info("Escribí tu CUIL o DNI (solo números) y presioná Buscar.")
        return

    resultados = buscar_persona(df, consulta)

    if resultados.empty:
        st.error(
            "No encontramos ninguna solicitud con ese CUIL/DNI. "
            "Revisá que esté bien escrito o consultá con RRHH."
        )
        return

    for _, fila in resultados.iterrows():
        mostrar_resultado(fila)


if __name__ == "__main__":
    main()
