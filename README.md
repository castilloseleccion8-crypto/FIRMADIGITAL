# Estado Firma Digital ENCODE

App de Streamlit para que cada persona busque su **CUIL o DNI** y vea el
estado de su trámite de Firma Digital ENCODE, con un instructivo de qué
hacer según el paso en el que esté.

## Cómo funciona

- Lee la hoja `DATOS` de la planilla `Lista_Gral.xlsm` (la misma que ya
  se usa para el seguimiento interno).
- Busca la fila cuyo `CUIL` o `DNI` coincide con lo ingresado.
- Según el valor de la columna **ESTADO ENCODE**, clasifica el trámite
  en una de varias categorías (falta descargar, faltan claves, falta
  identificación, rechazada, revocado, etc.) y muestra el instructivo
  correspondiente, definido en `instructivos.py`.
- Los textos de cada instructivo son **editables sin tocar código**:
  todos están en `instructivos.py`. Revisalos y ajustalos al
  procedimiento real de ENCODE en tu empresa antes de publicar la app.

## Datos personales

El Excel real **no está en este repositorio** porque contiene DNI, CUIL,
nombres y hasta contraseñas del portal ENCODE de cada persona. Ver
[`data/README.md`](data/README.md) para cómo colocarlo al correr la app
(copiándolo a mano en el servidor, o subiéndolo desde el navegador con
el panel de administración).

## Cómo correrla localmente

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # opcional, para poder subir el Excel desde el navegador
# Colocá tu Lista_Gral.xlsm en data/Lista_Gral.xlsm
streamlit run app.py
```

La app va a estar disponible en `http://localhost:8501`.

## Actualizar los datos

Cuando actualices la planilla:

- Si corrés la app en un servidor propio: reemplazá `data/Lista_Gral.xlsm`
  por la versión nueva. La app detecta el cambio automáticamente (por la
  fecha de modificación del archivo).
- Si preferís no tocar el servidor: usá el panel de administración
  (barra lateral → "Panel de administración") con la contraseña que
  hayas configurado en `admin_password`.

## Dónde vive cada cosa

| Archivo | Qué contiene |
|---|---|
| `app.py` | La app de Streamlit: búsqueda, carga de datos, panel de administración. |
| `instructivos.py` | Clasificación de estados + textos de cada instructivo. Editable sin tocar `app.py`. |
| `data/` | Carpeta donde va el Excel real (no versionado). |
| `.streamlit/secrets.toml` | Contraseña de administrador (no versionado). |

## Nota sobre despliegue

Si vas a publicar esta app en un servicio como Streamlit Community Cloud
con el repositorio en modo **público**, recordá que el Excel no viaja
con el repo: vas a tener que subirlo por el panel de administración
cada vez que se reinicie el servicio, ya que el almacenamiento de esos
entornos gratuitos no es persistente. Para un uso más estable, se
recomienda correr la app en un servidor propio (o un plan con disco
persistente) donde `data/Lista_Gral.xlsm` se mantenga entre reinicios.
