# Carpeta de datos

Esta carpeta está vacía a propósito: el Excel real (`Lista_Gral.xlsm`)
contiene datos personales (DNI, CUIL, nombres, e incluso contraseñas del
portal ENCODE) y **no se sube al repositorio** (está en `.gitignore`).

## Cómo cargar los datos

Elegí una de estas dos opciones:

1. **Copiar el archivo a mano** en el servidor donde corre la app, con
   exactamente este nombre y ubicación:

   ```
   data/Lista_Gral.xlsm
   ```

   Cada vez que actualices la planilla, reemplazá el archivo acá (o subí
   una nueva versión) y en la app tocá "Recargar datos" en el panel de
   administración, o simplemente esperá: los datos se refrescan solos
   cuando cambia la fecha de modificación del archivo.

2. **Subirlo desde el navegador**, usando el "Panel de administración"
   en la barra lateral de la app. Para habilitarlo, definí una
   contraseña de administrador (ver `.streamlit/secrets.toml.example`).

La hoja que la app lee es `DATOS`, con las columnas tal cual figuran en
la planilla original (`CUIL`, `DNI`, `SUCURSAL`, `ESTADO ENCODE`, etc.).
Si cambiás nombres de columnas en el Excel, actualizá las constantes al
principio de `app.py`.
