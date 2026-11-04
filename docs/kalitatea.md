# Kimu 3.0 — receta de calidad (obligatoria)

Todo material nuevo o mejorado debe sacar **≥ 9,8/10** en `python scripts/kalitatea.py --solo <ids>`. El revisor automático lo exige antes de fusionar un PR. El medidor cuenta lo que se puede contar; el resto lo revisa el autor.

## Teoría (`lugar: teoria`)
0. **Fotos reales grandes, una idea por fila** (obligatorio desde el 1-11-2026): hoja principal como `biderketa-infografia`, ver [`docs/teoria-argazkiak.md`](teoria-argazkiak.md).
1. **Esquema principal visual**: una `tabla` (irudia → izena → zertarako) o una `ilustracion` etiquetada (imagen real con `scripts/irudi_etiketatuak.py`) o `pasos`.
2. **Una imagen por tarjeta/apartado** (real o realista; `estatico/irudiak`). Una idea por caja, **≤ 20 palabras**.
3. Caja **Gogoratu** con la idea clave en una frase.
4. **Mapa mental** (`mapa`) al final.
5. Ficha de **ariketak enlazada** (`relacionada`).

## Ariketak (`lugar: actividades`)
1. **Ejemplo resuelto** antes de empezar (`gogoratu`, `pasos` o campo `ejemplo`).
2. **Icono por ítem**: `:icono:` al principio de cada frase, ítem o palabra.
3. **Variedad**: al menos 4 modos distintos (relacionar, clasificar, elegir, verdadero_falso, completar, preguntas…), nunca 3 seguidos iguales.
4. **Dificultad** marcada ⭐ → ⭐⭐ → ⭐⭐⭐ en los enunciados.
5. **Juegos**: incluye `relacionar` y `clasificar` con soluciones en el formato de `docs/fichas.md` (salen Lotu y Sailkatu) y algún `elegir` o `verdadero_falso` (sale Galderak).
6. **Berrikusi** al final.

### Fichas enteramente adaptadas (`egokitua`)

Una ficha con `beharrak` y todas sus hojas marcadas `egokitua: true` usa una rúbrica específica: letra y espacio grandes, ejemplo y soluciones en cada ejercicio, apoyo visual por ítem y borrador con soluciones. También comprueba los requisitos del perfil (`agnh`, `dislexia` o `tea`).

En estas fichas de práctica repetida no se exigen cuatro modos ni minijuegos: añadirlos puede romper la instrucción constante, la carga limitada por hoja y la estructura predecible que necesita la adaptación. La rúbrica conserva el mínimo de 9,8/10 y muestra qué criterio adaptado falta.

## Kit de tema (Ingurunea y temas grandes)
Teoría + ariketak + **estazioak** (rincones manipulativos con pasaporte) + **12 txartelak** + **infografia** + **irakaslearen gida**. Ejemplo de referencia: el plan de *Zentzumenak* (issue #50): tabla órgano→sentido, mapa, «zaindu», sabores; juegos Lotu/Sailkatu/Memoria; rincones de tacto, olfato, gusto, oído y vista.

## Siempre
- NEAE primero: lectura fácil, letra grande, mucho espacio, nada que dependa solo del color.
- Euskera batua natural (nada de calcos); palabras dudosas listadas en el PR.
- Cabe en A4 y ninguna hoja medio vacía (`scripts/revisar_hojas.py`).
- Antes de terminar, ejecuta `python scripts/xuxen.py` y asegúrate de que no haya palabras desconocidas nuevas; añade nombres válidos a `docs/xuxen-hitzak.txt`.
- En los PR se revisan con Hunspell y la API de Xuxen solo los JSON cambiados: ortografía bloquea, gramática y estilo solo avisan; la API limita cada llamada a 5000 caracteres y espera 1 s.
- Si la API falla, el PR continúa con Hunspell; en `main` el resultado de Xuxen es solo un aviso y nunca bloquea la publicación.

## Reglas PT/AL que bloquean
Ver `docs/neae-irizpideak.md`. `kalitatea.py` baja a 6 (y por tanto bloquea la fusión) cualquier ficha con: ARASAAC, «kalabaza», lenguaje de diagnóstico, «Jarraipen Pertsonalizatua», o una hoja `egokitua` con más de 3 ítems por ejercicio o sin `ejemplo`. Las fichas generadas que fallen se listan al final del informe y se corrigen en su generador.
