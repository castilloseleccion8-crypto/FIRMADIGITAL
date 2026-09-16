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
        "resumen": "Todavía no iniciaste tu solicitud de Firma Digital ENCODE. Seguí esta guía para darte de alta.",
        "antes": [
            "Tené a mano tu último DNI físico vigente.",
            "Descargá la app Google Authenticator en tu celular antes de empezar.",
            "Durante el proceso van a llegarte mails de ENCODE: ignoralos, no hace falta que hagas nada con ellos.",
            "Cualquier duda, escribí por mensaje privado al celular de RRHH.",
        ],
        "pasos": [
            "Entrá a https://pki.encodesa.com.ar/Solicitudes/Paso2.aspx y hacé click en \"Comenzar\".",
            "Completá tus datos personales: Tipo de certificado \"Persona Física\", Tipo de uso \"Particular\", y cargá tu mail y celular PERSONALES (no los de la empresa).",
            "Provincia: Córdoba. Localidad: Córdoba. El resto de los campos dejalos tal cual están.",
            "Forma de pago: \"Transferencia\" y click en \"Aceptar\".",
            "En la sección \"Pago de aranceles\" hacé click en \"Siguiente\": no tenés que pagar nada.",
            "Seleccioná la opción \"Telemática\".",
            "Click en \"Siguiente\" para empezar la verificación de identidad y dale permiso a la página para acceder a tu ubicación.",
            "En \"Acuerdo con suscriptores\" hacé click en \"Siguiente\".",
            "Marcá las dos casillas (\"Aceptar Términos y condiciones\" y \"Aceptar consentimiento informado\") y click en \"Siguiente\".",
            "Elegí \"Documento Nacional de Identidad\".",
            "Seguí los pasos de verificación biométrica: dale permiso a la cámara y a la ubicación, fotografiá tu DNI y sacate una selfie sin anteojos ni gorra, con buena luz y a cara descubierta.",
            "Si tus datos están correctos, en \"Generación de claves\" hacé click en \"Generar claves\".",
            "En la pantalla de Encustody (\"Registrar Usuario\") dejá los datos tal cual están y hacé click en \"Registrar Usuario\".",
            "En el campo \"Password\" pegá tu Contraseña ENCODE (la encontrás más abajo, en 'Mis credenciales', con el punto al final) y hacé click en \"Registrar\".",
            "Volvé a iniciar sesión usando esa misma Contraseña ENCODE.",
            "Se va a abrir una pantalla para configurar Google Authenticator. Importante: el escaneo del código QR es personal, no se puede usar la app de otra persona. Sacale una captura de pantalla a ese código QR y enviásela a RRHH (o a quien te esté ayudando) para que lo escaneen por vos.",
            "Esa persona abre Google Authenticator en su celular, toca \"Comenzar\" → continúa con su cuenta de Google → \"Agregar un código\" → \"Escanear un código QR\", y escanea la captura que le mandaste.",
            "Le va a aparecer un código de 6 dígitos: pedíselo y cargalo en \"Código de identificación\", después tocá \"Enviar\".",
            "En \"Crear PIN de Seguridad\" ingresá tu PIN (lo encontrás más abajo, en 'Mis credenciales', SIN el punto al final) y tildá \"Información importante sobre tu PIN\".",
            "Cuando te vuelva a pedir la clave, ingresá otra vez ese mismo PIN (sin el punto) y hacé click en \"Enviar\".",
            "Cuando veas la pantalla \"Gracias por elegirnos\", tu solicitud quedó enviada. Avisale a RRHH que terminaste el proceso.",
        ],
    },
    "PENDIENTE_DESCARGA": {
        "titulo": "Solicitud enviada — falta descargar el certificado",
        "icono": "📨",
        "color": "blue",
        "resumen": "Tu solicitud fue aprobada. El último paso es descargar e instalar tu certificado.",
        "pasos": [
            "Entrá a www.encodesa.com.ar",
            "Andá a \"Autogestión del Certificado\" y hacé click en \"Descargar\".",
            "En el sector \"Persona Física\" ingresá tu CUIL y el código captcha que aparece en la imagen, y hacé click en \"Buscar\".",
            "En la tabla de resultados, buscá tu nombre y hacé click en el ícono de la columna \"Descargar\".",
            "En la ventana que se abre, hacé click en \"Interactuar con el Servicio de Custodia\".",
            "Ingresá con usuario (tu CUIL) y la Contraseña ENCODE (la encontrás más abajo, en 'Mis credenciales', con el punto al final) y hacé click en \"Iniciar sesión\".",
            "Ingresá la clave OTP: el código de 6 dígitos que te muestra la app que configuraste (Google Authenticator o FreeOTP) y hacé click en \"Iniciar sesión\".",
            "Seleccioná tu \"Alias de Certificado\" y hacé click en \"Instalar Certificado\".",
            "Hacé click en \"Firmar Acuerdo\".",
            "Volvé a colocar tu PIN de Seguridad (el mismo de siempre, SIN el punto al final) y confirmá.",
            "Cuando veas \"Certificado instalado\", hacé click en \"Cerrar\". Avisale a RRHH que terminaste.",
        ],
    },
    "COMPLETADO": {
        "titulo": "Trámite completo",
        "icono": "✅",
        "color": "green",
        "resumen": "¡Listo! Tu certificado de Firma Digital ya fue descargado e instalado. No tenés que hacer nada más.",
        "pasos": [
            "No hay ninguna acción pendiente de tu parte.",
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
        "resumen": "Tu solicitud fue rechazada.",
        "pasos": [
            "Consultá con RRHH el motivo del rechazo.",
        ],
    },
    "REVOCADO": {
        "titulo": "Certificado revocado",
        "icono": "🚫",
        "color": "red",
        "resumen": "Tu certificado fue revocado y ya no es válido para firmar.",
        "pasos": [
            "Consultá con RRHH el motivo de la revocación.",
        ],
    },
    "REHACER": {
        "titulo": "Hay que rehacer el trámite",
        "icono": "🔁",
        "color": "orange",
        "resumen": "El sistema indica que tenés que volver a hacer el trámite desde cero, con los mismos pasos que si nunca hubieras iniciado una solicitud.",
        "pasos": [],
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

# "Rehacer el trámite" sigue exactamente la misma guía que "Sin solicitud".
INSTRUCTIVOS["REHACER"]["antes"] = INSTRUCTIVOS["SIN_SOLICITUD"]["antes"]
INSTRUCTIVOS["REHACER"]["pasos"] = INSTRUCTIVOS["SIN_SOLICITUD"]["pasos"]

DEFAULT_INSTRUCTIVO = INSTRUCTIVOS["OTRO"]
