# Kimu LH 1 — guía de estilo (6–7 años)

Complementa a [`estilo-materiales.md`](estilo-materiales.md). Todo lo de allí vale (NEAE, imágenes reales, A4, B/N, dos partes teoría/ariketak), con estos cambios para **1.º de Primaria**.

## Dónde va

- Áreas propias: `contenido/arloak/lh1-euskara.json`, `lh1-matematika.json`, `lh1-ingurunea.json` (`"maila": "LH 1"`). Se ven en `lh-1.html`.
- Mientras un área no tenga material está en `"estado": "preparando"`. Al publicar su primera sección, cambia a `"activo"` y rellena su `pagina` como las de LH 3.
- Secciones nuevas: `contenido/secciones/lh1-<tema>.json` con `"arlo": "lh1-…"`. Fichas: `"curso": "LH 1"` e id con prefijo `lh1-`.
- Matemáticas LH 1 usa los mismos colores de posición (H rojo, B azul) que LH 3: se aplican solos.

## Cómo es una ficha LH 1

- **Muy poco texto.** El alumnado aún no lee con soltura: enunciado de 2–5 palabras + **icono de la acción** (✏️ idatzi, ⭕ inguratu, 🔗 lotu, 🖍️ margotu, ✂️ moztu, 👂 entzun).
- **Letra muy grande**: hojas con `"tamano": "grande"` o `"egokitua": true`. Palabras para leer ≥ 24 pt.
- **Letra de imprenta** (confirmado por el autor, 26-10): minúscula escolar y mayúscula juntas cuando se presenta una letra (`A a`). Nunca letra ligada.
- **Una imagen = una palabra**, foto o ilustración realista, objeto entero y centrado, fondo blanco. Palabras frecuentes y concretas (etxea, ogia, ura…). Nada de abstractos.
- **Máximo 4 ítems por ejercicio** y **2–3 ejercicios por hoja**. Ejemplo resuelto siempre en el primer ítem.
- **Mucho espacio**: casillas de 1,5 cm, pauta doble (lerro bikoitzak) para escribir y trazar.
- **Estructura fija en toda la colección de letras** (el niño la reconoce):
  1. Teoría «Letra A»: la letra grande (mayúscula + minúscula), 4 imágenes que empiezan por ella, cómo se traza (flechas numeradas).
  2. Ariketak: ⭕ inguratu la letra entre otras · ✏️ trazatu (letra punteada en pauta doble) · 🔗 lotu irudia eta hasierako letra · silabak (cuando ya hay consonante) · ⭐ berrikusi con 2–3 casillas (Ezagutu dut · Trazatu dut · Irakurri dut).

## Euskera

- Batua, palabras del día a día del aula de 1.º. Sin artículos ni sufijos raros en las palabras de vocabulario: forma con artículo (`etxea`, `ogia`) como en clase.
- Las letras se presentan en el orden de clase: **bokalak (a, e, i, o, u) eta h**, luego una consonante por semana (m, p, l, s, t, n, d…). El autor puede cambiar el orden.

## Antes de publicar

- [ ] ¿Un niño de 6 años con NEAE sabe qué hacer solo con mirar los iconos?
- [ ] ¿Cada palabra tiene su imagen real o realista?
- [ ] ¿Cabe en A4, sin hojas medio vacías, y se entiende en blanco y negro?
