# Kimu — Marka-gida

Euskarazko materialak PT eta NEAErako. Guía de marca única para fichas, juegos, web, Instagram y boletín: todo lo de Kimu se tiene que reconocer sin leer el nombre.

> **v1 aprobada por Iker el 1-11-2026** (un solo verde, naranja #a8560c, Andika para LH 1 y dislexia, color por área). Sale de lo que ya existía en la web (`estatico/kimu.svg`, `area.css`, `fitxa.css`) y de `docs/estilo-materiales.md`.

## Esencia

- **Qué es:** herramienta real de aula, en euskera batua, pensada primero para alumnado NEAE. Si funciona para ellos, funciona para todos.
- **Personalidad:** cercana, clara, tranquila. Un brote que crece (*kimu* = brote).
- **Tres palabras:** argia (clara), lasaia (tranquila), erabilgarria (útil).

## Voz

- Euskera batua natural, frases cortas, una idea por frase, una acción por consigna («Idatzi zenbakia hitzez.», no «Begiratu eta idatzi…»).
- Con docentes y familias: de tú, directo, sin tecnicismos. En redes: «✕ esto falla / ✓ en Kimu ya está resuelto».
- Felicitar el esfuerzo, no el resultado: «Ondo egina!», «Primeran!», «Lortu duzu!».
- Nunca: infantilizar (LH 3 no es Haur Hezkuntza), prometer lo que la web no tiene, enseñar a fabricar el material.

## Colores

Cinco de marca + neutros. Los nombres son los tokens.

| Token | Hex | Uso |
|---|---|---|
| `berdea` | #2f7d3a | Principal: títulos, etiquetas de apartado, botón principal |
| `hostoa` | #b8f36b | Acento: resaltar, sombra de pegatina, foco. Encima siempre `tinta` |
| `gorputza` | #d9f7b0 | Relleno suave: «Gogoratu!», ejemplo resuelto |
| `laranja` | #a8560c | Segundo color: ⭐ niveles, «Erronka», «Berrikusi» |
| `tinta` | #20241f | Todo el texto y el trazo de las cajas |
| `papera` / `krema` | #ffffff / #f7f7f2 | Hoja de ficha / fondo de web e Instagram |

**Reglas:** en una ficha, como mucho `berdea` + `laranja` + un color de área. Nada depende solo del color (siempre texto o icono además). Todo se entiende impreso en blanco y negro. `enborra` (#3f7a22) es solo para la mascota.

**Código de área** (franja de cabecera y etiqueta de nivel): Euskara `arloa-euskara` #2563b0 · Matematika `arloa-matematika` #a8560c · Ingurunea `arloa-ingurunea` #12788a.

**Cambio respecto a lo actual:** el naranja pasa de #c46a12 a **#a8560c**, porque el antiguo no llega a 4,5:1 sobre blanco (3,9:1). En la web había varios verdes (#2f7d3a, #38a64a, #4f8a55): queda uno, `berdea`.

## Tipografía

- **Nunito** (títulos 900/800, consignas 700, texto 400). Licencia SIL OFL: uso comercial permitido, archivos en `estatico/fonts/`.
- **Andika** (SIL OFL, Google Fonts) solo para lectoescritura de **LH 1** (letra de imprenta con *a* y *g* de una sola panza) y para las **versiones dislexia**.
- Ficha: texto ≥ 18 px (≈13,5 pt), interlineado 1,5, alineado a la izquierda, nunca justificado ni en cursiva para leer. Números grandes.
- Prohibidas: fuentes «escolares» de uso personal (familia KG, Back to School…), Comic Sans y cualquier fuente sin licencia comercial.

## La mascota: Kimu

Un brote verde redondo con dos hojas. Es la cara de la marca (foto de perfil, favicon, portada) y la única «persona» de los materiales.

**Usos fijos:**
1. **Portada / cabecera:** pequeña, junto al título o al logo.
2. **Consigna:** a la izquierda de la consigna o dentro de «Gogoratu!», como quien explica.
3. **Felicitación:** al final, con «Ondo egina!» o en el aviso de acierto de los juegos.

**Normas:** siempre el SVG original (`estatico/kimu.svg`), sin deformar, sin cambiar colores ni añadirle ropa o accesorios de personajes con derechos. Tamaño mínimo 15 mm impreso / 32 px en pantalla. Sobre fondo claro (`papera`, `krema`, `gorputza`). Una vez por página como máximo, salvo en juegos.

**Logo (aprobado 1-11-2026),** mascota + «Kimu» en Nunito 900 color `tinta`, texto en trazos (no depende de la fuente). Tres versiones en `estatico/logoak/`:
- `kimu-logo-horizontala.svg`: web, cabecera de ficha, boletín.
- `kimu-logo-karratua.svg`: perfil de Instagram, icono de la web (círculo `gorputza`).
- `kimu-logo-zuribeltza.svg`: pie de ficha y cualquier impresión en blanco y negro.
No recolorear, no deformar, dejar alrededor un margen libre igual a la altura de la «i».

## Estructura fija de ficha (A4)

1. **Cabecera:** franja del color de área · título en pegatina (trazo `tinta` 2 px + sombra `pegatina`) · etiqueta de nivel en píldora («LH 3 · Mate») · Izena / Data.
2. **Consigna con la mascota:** Kimu + consigna en `agindua` + ejemplo resuelto sobre `gorputza`.
3. **Actividad:** ⭐ → ⭐⭐ → ⭐⭐⭐, una idea por caja, mucho espacio para escribir (líneas `lerroa`).
4. **Pie:** logo Kimu pequeño + «© Kimu · kimumaterialak» + número de página, en `oharra`.

Cajas fijas: **«Gogoratu!»** (relleno `gorputza`, con Kimu) y **«Berrikusi»** (borde `laranja`, checklist). Se ven en el componente *Kutxak*.

## Iconos e imágenes

- Iconos de acción en las consignas (idatzi, margotu, lotu, ebaki, irakurri), mismo grosor de trazo que la mascota (3,5 px a su escala), en `tinta`.
- Imágenes reales o realistas, una imagen = un concepto. Propias, generadas por Iker para Kimu o de bancos con licencia comercial (Pexels, Unsplash, Wikimedia CC0/CC BY).
- **ARASAAC (CC BY-NC-SA): nunca en material de pago.** Solo en gratuito, con atribución. Para lo de pago: iconos propios o Mulberry Symbols (CC BY-SA).
- Nunca personajes con derechos (anime, Disney, Nintendo…).

## Instagram y web

- Instagram: 1080 × 1350, fondo `krema`, titular grande en Nunito 900 (máx. 6 palabras), Kimu en una esquina, última diapositiva «Gorde 📌 · Doan, estekan».
- Web: tokens del tema `argia` / `iluna`; sombras `web-leuna` (la `pegatina` es solo para fichas).

## Licencias (antes de vender)

- Fuentes: Nunito y Andika, SIL OFL ✔︎.
- Canva: se puede vender un PDF final hecho con sus elementos, no plantillas editables ni elementos sueltos. Comprobar condiciones actuales antes de basar un producto en Canva.
- Imágenes y pictogramas: ver «Iconos e imágenes».

## Dónde se aplica

Una vez aprobada: `scripts/fitxa_pdf.py` (colores y fuente por defecto), `assets/jokoa-txantiloia.html`, `estatico/area.css` y `fitxa.css` de la web, plantillas de Instagram y del boletín.

## Tokens (copiar tal cual en CSS)

```css
:root{
  --berdea:#2f7d3a; --hostoa:#b8f36b; --gorputza:#d9f7b0; --laranja:#a8560c;
  --tinta:#20241f; --grisa:#5d6472; --papera:#ffffff; --krema:#f7f7f2; --lerroa:#c9ced6;
  --enborra:#3f7a22;
  --arloa-euskara:#2563b0; --arloa-matematika:#a8560c; --arloa-ingurunea:#12788a;
  --biribil-txiki:8px; --biribil-handi:16px; --pilula:999px;
  --pegatina:4px 4px 0 #b8f36b;            /* solo fichas */
  --web-leuna:0 2px 8px rgba(32,36,31,.10); /* web */
}
[data-theme="iluna"]{
  --berdea:#8fd14f; --gorputza:#293326; --laranja:#f0a35e; --tinta:#eef1e9; --grisa:#a0a99b;
  --papera:#202520; --krema:#171a17; --lerroa:#343b33;
  --arloa-euskara:#7fb0ec; --arloa-matematika:#f0a35e; --arloa-ingurunea:#6cc3d1;
}
```

Escala de texto: izenburua 32/36 · 900 · atala 20/26 · 800 · agindua 18/26 · 700 · fitxa-testua 18/27 · 400 · web-testua 16/24 · 400 · oharra 12/16 · 700 · irakurketa (Andika) 24/36 · 400.
Espacios: 4 · 8 · 16 · 24 · 40 px.

Referencia visual completa (privada de Iker): sistema de diseño «Kimu — Marka-gida» en claude.ai.
