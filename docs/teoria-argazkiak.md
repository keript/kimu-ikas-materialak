# Teoría con fotos reales (estándar Kimu, 1-11-2026)

**Toda explicación y teoría de Kimu se hace así.** Modelo: `contenido/fitxak/biderketa-infografia.json`
(hoja «Biderketa zer da?»). Lo decidió Iker: es lo que mejor funciona con alumnado NEAE, y si funciona
para ellos funciona para todos.

## Cómo es la hoja principal

- **Una idea por fila**: bloque `tarjetas` con `"columnas": 1` → foto grande a la izquierda (112 mm),
  texto a la derecha. 3–4 filas por hoja como máximo + `gogoratu` al final.
- Cada tarjeta: `"foto": true`, `"imagen": "<id-de-la-foto>"`, `"ikonoa": "<emoji de estatico/irudiak>"`
  (se ve mientras la foto no exista), `titulo`, `grande` (la operación, palabra o regla en grande:
  «3 × 4 = 12», «hatza», «TS»), `texto` (una línea de apoyo: la suma, la sílaba…), `pie` (qué se ve en la foto).
- `"tamano": "grande"` en la hoja. El resto de hojas (reglas, tabla, mapa mental) siguen como siempre.
- Lo que la foto enseña tiene que coincidir **exactamente** con el texto (3 saskis × 4 sagar = 12 manzanas que se ven).

## Las fotos

1. Añade un grupo de 4 en `contenido/irudiak/hiztegia-irudiak.json` (`id`, `izena`, `hitzak` id→texto, `edukia`
   en inglés). Al llegar a `main` se abre solo el issue «🖼️ Irudia: …» con la orden para Gemini.
2. Ejecuta `python scripts/foto_irudia.py` para crear los marcadores de `estatico/irudiak/<id>.svg` (los pide la validación).
3. Iker genera la foto, la sube al issue y GitHub la corta, la guarda en `estatico/irudiak-errealak/` y publica.
   Hasta entonces la ficha enseña el `ikonoa` (nunca «irudia laster»).

**Cómo escribir `edukia` para que Gemini no se equivoque contando** (lo hemos comprobado):
- *taken from directly above*, *plain white background*, *no text*;
- *one single layer, no item hidden or overlapping*;
- cantidades pequeñas y en formas fáciles: «2 by 2 square», «small triangle», «like the five on a dice»,
  «three rows of four»;
- di el total: «twelve apples in total».
Iker **cuenta siempre** antes de subirla; si una sale mal, se repite solo esa.

## Lo que mide `kalitatea.py`

Teoría: ≥ 2 tarjetas con `"foto": true` (1 punto de 10). Sin ellas, la ficha no llega a 9,8.
Infografías, guías del profesor y rincones tienen su propio formato y no se miden.
