# Estadísticas sin cookies

1. Crea una cuenta gratuita en [GoatCounter](https://www.goatcounter.com/) y añade el sitio de Kimu.
2. Copia el código del sitio que aparece en su dirección: `https://<código>.goatcounter.com`.
3. En `scripts/build.py`, cambia `estatistikak = ""` por `estatistikak = "<código>"`. Vacío lo deja desactivado.
4. En los ajustes de GoatCounter, crea un token de API para consultar las estadísticas.
5. En GitHub, guarda el token como secreto del repositorio `GOATCOUNTER_TOKEN`. El parte diario mostrará las páginas y los juegos más usados de los últimos 7 días.

GoatCounter no usa cookies. Kimu registra páginas, impresiones y juegos terminados; no envía datos personales.
