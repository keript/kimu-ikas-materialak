# Diseño de la web de Kimu: reglas para llegar al 10

Se aplica a **todo cambio visual de la web** (plantillas, CSS, `estatico/*.js`, páginas generadas). Para el contenido de las fichas A4 mandan `docs/estilo-materiales.md` y `docs/kalitatea.md`; si algo choca, gana la regla de las fichas.

Inspirado en las guías abiertas *Impeccable* (Paul Bakaus, Apache 2.0) y *UI/UX Pro Max* (Next Level Builder, MIT), resumidas y adaptadas a Kimu.

## Para quién es la web
Profes de PT y tutores de LH que buscan material **rápido**, a menudo desde el móvil o en la pizarra digital, y alumnado NEAE que juega en tablet o pizarra. La web es una **herramienta**, no un escaparate: claridad, constancia y precisión antes que efectos.

**Prueba de los 5 segundos:** en cada página, un profe encuentra sin pensar el curso, el área, «Inprimatu / Deskargatu» y «Jolastu».

## Comprobar siempre (en la página generada, no en el código)
1. **Contraste:** texto normal ≥ 4,5:1, texto grande ≥ 3:1. Sobre fondos de color, el texto secundario se tiñe del mismo tono; nunca gris sobre color ni gris sobre gris.
2. **Táctil:** botones y enlaces ≥ 44×44 px, con ≥ 8 px entre ellos (dedos pequeños, pizarra digital). Nada que funcione solo con hover.
3. **Móvil primero:** sin scroll horizontal a 360 px; nunca desactivar el zoom; la página aguanta texto al 200 %.
4. **Texto:** cuerpo ≥ 16 px en la web, interlineado ~1,5, líneas de 65–75 caracteres. Escalones de tamaño y peso claros entre títulos.
5. **Espaciado:** grupos apretados y separación generosa entre bloques; más espacio encima de un título que debajo.
6. **Estados:** hover, foco visible (nunca quitar el `outline`; hacerlo bonito con `--accent`), desactivado, cargando, vacío y error, todos diseñados.
7. **Detalles del navegador:** `::selection`, anillo de foco, `text-underline-offset` de los enlaces y barras de scroll propias con la paleta de Kimu. Es lo que hace que una web parezca hecha y no montada.
8. **Movimiento:** como mucho un gesto con sentido por página (p. ej., acierto en un juego), de 150–300 ms, con salida suave. No animar `width/height`. `prefers-reduced-motion` con una alternativa que siga mostrando el cambio, no un corte total.
9. **Rendimiento:** imágenes con `loading="lazy"`, `width` y `height` puestos (que nada salte al cargar) y WebP cuando se pueda.
10. **Textos de la interfaz:** en euskera; cada botón dice lo que hace («Deskargatu PDFa», «Hasi jolasten»), nunca «Klik egin hemen». Los errores dicen qué pasa y cómo arreglarlo.

## Evitar en la web
- Rejillas de tarjetas iguales (icono + título + texto) como única estructura de página. **Nunca tarjetas dentro de tarjetas.**
- Etiquetas pequeñas encima de un título (*eyebrow* o *kicker*): el título se basta solo.
- Números de sección (01, 02…) salvo que el orden importe.
- Texto con degradado, cristal o blur decorativo, bordes laterales de color de más de 1 px en tarjetas o avisos, y sombras duras desplazadas (`4px 4px 0`). Las sombras: desplazamiento pequeño y difuminado suave.
- **Emoji como iconos de la interfaz** (menús, botones, cabeceras): usa SVG de `estatico/irudiak` o `contenido/ilustraciones`, todos con el mismo grosor de trazo. (En las fichas para el alumnado sí se mantienen los iconos de acción que pide `estilo-materiales.md`.)
- Ventanas modales salvo que la tarea lo necesite de verdad.
- Colores en hexadecimal fuera de las variables de `estatico/area.css`.

## Cómo entregar un PR visual
1. Capturas de las páginas cambiadas a **360 px** y a **1280 px** (Playwright vale) en la descripción del PR.
2. Tabla de autoevaluación (0–4 por fila, objetivo **≥ 18/20**; si no llega, se mejora antes de pedir revisión):

| | 0–4 |
|---|---|
| Accesibilidad (contraste, foco, alt, teclado) | |
| Móvil y pizarra (táctil, 360 px, zoom) | |
| Rendimiento (imágenes, nada salta) | |
| Coherencia (variables, iconos, espaciado) | |
| Textos (euskera claro, botones con acción) | |

3. Si algo de esta guía choca con lo que pide el issue, gana el issue: explícalo en el PR.
