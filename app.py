"""Buscador de estado de trámite de Firma Digital ENCODE.

Cada persona ingresa su CUIL (o DNI) y ve el estado de su solicitud junto
con un instructivo de qué hacer según el paso en el que se encuentre.

El archivo de datos (Lista_Gral.xlsm) NO se guarda en el repositorio por
contener datos personales. Ver data/README.md para cómo ubicarlo, o usar
el panel de administración en la barra lateral para subirlo desde el
navegador.
"""

from __future__ import annotations

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

st.set_page_config(page_title="Estado Firma Digital ENCODE", page_icon="🔏", layout="centered")


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


def mostrar_resultado(fila: pd.Series) -> None:
    nombre = fila.get(COL_NOMBRE_COMPLETO) or "—"
    sucursal = fila.get(COL_SUCURSAL) or "—"
    estado_original = fila.get(COL_ESTADO_ENCODE)
    categoria = clasificar_estado(estado_original)
    instructivo = INSTRUCTIVOS.get(categoria, DEFAULT_INSTRUCTIVO)

    st.subheader(f"{instructivo['icono']} {instructivo['titulo']}")
    st.caption(f"{nombre} · {sucursal}")
    st.write(instructivo["resumen"])

    baja = fila.get(COL_BAJA)
    if baja and str(baja).strip().lower() not in ("no", "nan", ""):
        st.warning(
            f"El campo BAJA de esta persona figura como '{baja}'. "
            "Si ya no trabajás en la empresa, este trámite puede no aplicar: consultá con RRHH."
        )

    st.markdown("**¿Qué tengo que hacer?**")
    for i, paso in enumerate(instructivo["pasos"], start=1):
        st.markdown(f"{i}. {paso}")

    if ENCODE_PORTAL_URL:
        st.link_button("Ir al portal de ENCODE", ENCODE_PORTAL_URL)

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
                st.markdown(f"**Contraseña:** `{contrasena}`")
            if pin:
                st.markdown(f"**PIN:** `{pin}`")


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
    st.title("🔏 Estado de mi Firma Digital ENCODE")
    st.write(
        "Ingresá tu **CUIL** (o DNI) para ver en qué paso está tu trámite "
        "y qué tenés que hacer para continuarlo."
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
        st.divider()


if __name__ == "__main__":
    main()
