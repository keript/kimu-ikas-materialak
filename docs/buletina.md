# Kimu buletina

**Desde el 2-11-2026 hay una sola lista de correo, en MailerLite** (cuenta kimumaterialak@gmail.com, plan gratis: hasta 250 suscriptores y 2.500 correos al mes).

- **Cómo se entra:** la página `irakurgaiak.html` tiene el formulario de MailerLite («Lina eta Kimu – deskarga», grupo «Kimu irakurgaiak»). Regala el cuento «Lina eta Kimu» a cambio del correo, con casilla de consentimiento y reCAPTCHA.
- **La caja de la lista** (`plantillas/_buletina.html`, en la portada y en cada ficha) ya no tiene formulario propio: es un botón que lleva a `irakurgaiak.html`. Así no se cargan scripts de terceros en toda la web. Para ocultarla, deja `buletina = ""` en `scripts/build.py`.
- **Correo de bienvenida:** automatización de MailerLite «Lina eta Kimu – deskarga Workflow», con el enlace a la carpeta de Drive «Kimu irakurgaiak – deskargak».
- **Boletín mensual:** se escribe y se envía como campaña de MailerLite al grupo «Kimu irakurgaiak». El flujo antiguo de Buttondown (`scripts/buletina.py`, `.github/workflows/buletina.yml`) queda en pausa (solo manual). Si se quiere automatizar el borrador mensual con MailerLite, hará falta su API key como secret de GitHub.
- **Privacidad:** `pribatutasuna.html`. No se guardan correos ni claves en este repositorio.
