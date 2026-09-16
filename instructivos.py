"""Instructivos mostrados según el valor de la columna 'ESTADO ENCODE'.

Este archivo es el único lugar que hace falta editar para ajustar los
textos de cada paso del trámite. No requiere tocar app.py.

IMPORTANTE: los pasos de cada instructivo son un punto de partida
razonable a partir de los estados que aparecen en la planilla. Repasalos
y ajustalos con el procedimiento real de ENCODE en tu empresa antes de
publicar la app a todo el personal.
"""

import unicodedata

# Completá esta URL con el link real al portal de ENCODE (o al mail/soporte
# que corresponda). Si la dejás vacía, la app simplemente no muestra el botón.
ENCODE_PORTAL_URL = ""


def _normalizar(texto: str) -> str:
    texto = "" if texto is None else str(texto)
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def clasificar_estado(estado_original: str) -> str:
    """Agrupa los distintos textos (y errores de tipeo) de la planilla
    en un número chico de categorías, cada una con su instructivo."""
    e = _normalizar(estado_original)

    if not e or e in ("#n/a", "nan", "none"):
        return "SIN_SOLICITUD"
    if "no se encuentra solicitud" in e:
        return "SIN_SOLICITUD"
    if "descargado" in e:
        return "COMPLETADO"
    if "enviado" in e:
        return "PENDIENTE_DESCARGA"
    if "rechaz" in e:
        return "RECHAZADA"
    if "revoc" in e:
        return "REVOCADO"
    if "alta nuevamente" in e or "proceso de nuevo" in e:
        return "REHACER"

    tiene_clave = "clave" in e
    tiene_identificacion = "identif" in e
    if tiene_clave and tiene_identificacion:
        return "CLAVES_E_IDENTIFICACION"
    if tiene_clave:
        return "FALTAN_CLAVES"
    if tiene_identificacion:
        return "FALTA_IDENTIFICACION"

    return "OTRO"


INSTRUCTIVOS = {
    "SIN_SOLICITUD": {
        "titulo": "Todavía no hay una solicitud cargada",
        "icono": "⚪",
        "color": "gray",
        "resumen": "No encontramos una solicitud de Firma Digital ENCODE iniciada para vos en el sistema.",
        "pasos": [
            "Comunicate con RRHH para confirmar que tu trámite de Firma Digital haya sido iniciado.",
            "Si ya lo solicitaste hace tiempo y seguís viendo este mensaje, puede ser un error de carga: avisá a RRHH para que lo revisen.",
        ],
    },
    "PENDIENTE_DESCARGA": {
        "titulo": "Solicitud enviada — falta descargar el certificado",
        "icono": "📨",
        "color": "blue",
        "resumen": "Tu solicitud fue aprobada y enviada. El último paso es descargar e instalar tu certificado.",
        "pasos": [
            "Revisá tu casilla de mail (y la carpeta de spam) buscando un correo de ENCODE con el link de descarga.",
            "Ingresá al portal de ENCODE con tu usuario y contraseña (los encontrás más abajo, en 'Mis credenciales').",
            "Seguí el asistente para descargar e instalar el certificado en tu equipo o celular.",
            "Una vez instalado, avisá a RRHH para que actualicen tu estado a 'Descargado'.",
        ],
    },
    "COMPLETADO": {
        "titulo": "Certificado descargado — trámite completo",
        "icono": "✅",
        "color": "green",
        "resumen": "¡Listo! Tu certificado de Firma Digital ya fue descargado e instalado.",
        "pasos": [
            "Verificá que podés firmar documentos con normalidad.",
            "Guardá tu usuario, contraseña y PIN en un lugar seguro: los vas a necesitar para renovar o reinstalar el certificado más adelante.",
            "Si necesitás instalarlo en otro equipo, contactate con RRHH o el administrador de ENCODE.",
        ],
    },
    "FALTAN_CLAVES": {
        "titulo": "Falta definir tus claves de seguridad",
        "icono": "🔑",
        "color": "orange",
        "resumen": "Tu solicitud está en curso pero falta que definas las claves de seguridad en el portal de ENCODE.",
        "pasos": [
            "Ingresá al portal de ENCODE con el usuario y contraseña que figuran en 'Mis credenciales'.",
            "Buscá el paso 'Definición de claves de seguridad' (a veces llamado 'PIN' o 'clave de firma').",
            "Usá el PIN que te asignamos (lo encontrás más abajo) o generá uno nuevo si el sistema te lo pide.",
            "Confirmá y guardá los cambios. Si el sistema te da un error, avisá a RRHH.",
        ],
    },
    "FALTA_IDENTIFICACION": {
        "titulo": "Falta completar la validación de identidad",
        "icono": "🪪",
        "color": "orange",
        "resumen": "Tu solicitud está en curso pero falta validar tu identidad (foto de DNI y selfie).",
        "pasos": [
            "Ingresá al portal de ENCODE con tu usuario y contraseña.",
            "Tené a mano tu DNI físico, último ejemplar vigente (frente y dorso).",
            "Completá la validación con buena luz, sin gorra ni lentes de sol, siguiendo las indicaciones en pantalla.",
            "Si la app te rechaza las fotos varias veces, contactá a RRHH para que revisen el estado de tu DNI en el sistema.",
        ],
    },
    "CLAVES_E_IDENTIFICACION": {
        "titulo": "Falta identificarte y definir tus claves",
        "icono": "⚠️",
        "color": "orange",
        "resumen": "Tu solicitud está en curso: todavía faltan dos pasos, validar tu identidad y definir tus claves de seguridad.",
        "pasos": [
            "Ingresá al portal de ENCODE con el usuario y contraseña de 'Mis credenciales'.",
            "Completá primero la validación de identidad con tu DNI físico (último ejemplar) y una selfie con buena luz.",
            "Luego completá la definición de claves de seguridad, usando el PIN indicado más abajo.",
            "Si algún paso te da error, avisá a RRHH para que revisen tu solicitud.",
        ],
    },
    "RECHAZADA": {
        "titulo": "Solicitud rechazada",
        "icono": "❌",
        "color": "red",
        "resumen": "Tu solicitud fue rechazada. Revisá el motivo y volvé a iniciar el trámite.",
        "pasos": [
            "Fijate si hay un motivo en 'Observaciones' más abajo.",
            "El rechazo suele deberse a un DNI vencido, ilegible o mal cargado: tené a mano tu último ejemplar vigente.",
            "Comunicate con RRHH para que reinicien tu solicitud con los datos corregidos.",
        ],
    },
    "REVOCADO": {
        "titulo": "Certificado revocado",
        "icono": "🚫",
        "color": "red",
        "resumen": "Tu certificado fue revocado y ya no es válido para firmar.",
        "pasos": [
            "Comunicate con RRHH o el administrador de ENCODE para conocer el motivo de la revocación.",
            "Vas a tener que iniciar un nuevo trámite de Firma Digital desde cero.",
        ],
    },
    "REHACER": {
        "titulo": "Hay que rehacer el trámite",
        "icono": "🔁",
        "color": "orange",
        "resumen": "El sistema indica que tenés que volver a iniciar el alta, generalmente por un problema con el DNI presentado.",
        "pasos": [
            "Conseguí tu último ejemplar de DNI vigente (que no esté vencido ni dañado).",
            "Llevalo a RRHH para que vuelvan a cargar tu solicitud de alta en ENCODE.",
            "Una vez reingresada, tu estado va a pasar a 'Enviado' y vas a poder seguir el trámite desde acá.",
        ],
    },
    "OTRO": {
        "titulo": "Estado a revisar con RRHH",
        "icono": "❓",
        "color": "gray",
        "resumen": "Tu solicitud tiene un estado que no pudimos clasificar automáticamente.",
        "pasos": [
            "Comunicate con RRHH y contales el estado exacto que ves más abajo, en 'Detalle del sistema'.",
        ],
    },
}

DEFAULT_INSTRUCTIVO = INSTRUCTIVOS["OTRO"]
