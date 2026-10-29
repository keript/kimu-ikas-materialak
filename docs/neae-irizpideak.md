# Criterios PT/AL para los materiales NEAE de Kimu

Guía de especialista en **Pedagogia Terapeutikoa (PT)** y **Entzumena eta Hizkuntza (AL)** para crear o adaptar materiales. Complementa `docs/estilo-materiales.md` y la sección NEAE de `.github/copilot-instructions.md`. Si algo choca, mandan esas dos, salvo en lo que aquí se marca como **obligatorio**.

## Idioma y términos
- Todo el material va en **euskera batua** sencillo: frases cortas, vocabulario frecuente, **una instrucción por línea**, imperativos claros (*Irakurri, Lotu, Margotu, Idatzi, Inguratu, Zenbatu*).
- Siglas correctas (no inventar otras): **BHLP** (= NEAE), **HPB** (= NEE), **JPP = Jarduera Plan Pertsonalizatua**, **BCE** (ACI), **IDU** (= DUA). Perfiles: **AGNH** (TDAH), **TEA/AEN**, **dislexia**, **diskalkulia**, **HGN** (trastorno del desarrollo del lenguaje), **dislaliak**, **euskara L2 / ikasle etorri berria**.
- **Nunca lenguaje de diagnóstico** en el material ni en las descripciones: «zailtasunak», «behar dituen laguntzak», no «ikasle dislexikoa» ni «gaixotasuna». Persona primero: «dislexia duen ikaslea».
- Notas para la familia: en **euskera + castellano** (muchas familias no hablan euskera). Lenguaje claro, empezar por lo positivo, 2–3 ideas fáciles para casa.

## Principios obligatorios
1. **Fortalezas e intereses primero** (IDU 7): temas cercanos y motivadores, éxito en el primer ejercicio.
2. **Ejemplo resuelto** antes de cada tipo de ejercicio nuevo.
3. **Graduar** de lo concreto a lo abstracto (manipulativo → imagen → símbolo) y de menos a más (Bloom: gogoratu → ulertu → aplikatu). ⭐ → ⭐⭐ → ⭐⭐⭐.
4. **Imprimible en blanco y negro** con lo que hay en un aula normal (sin depender del color; el color ayuda, no informa solo).
5. Sesiones reales de **30–50 min**: una ficha = 10–15 min de trabajo.
6. **Gutxieneko helburua** de cada ficha egokitua: una línea en la guía docente o en `descripcion_meta` con lo mínimo que debe lograr el alumno.
7. **Pictogramas: no ARASAAC** (licencia no comercial). Usar `estatico/irudiak` o imágenes reales con licencia libre.

## Adaptación por perfil (qué cambia en la ficha)

### AGNH
- Máx. **3 ítems por ejercicio**, un ejercicio por bloque visual; casillas «eginda ✓».
- Pasos numerados (1-2-3) con icono; checklist de inicio y cierre.
- Nota opcional de tiempo («⏱️ 5 min») y de movimiento al terminar.
- Evaluación: cada pregunta en su recuadro, valorar contenido y no la limpieza.

### TEA
- **Misma estructura en todas las hojas**, instrucción siempre en el mismo sitio y con las mismas palabras.
- Marcas **HASI / BUKATU**; primer ítem hecho como modelo.
- Lenguaje **literal**: sin ironía, metáforas ni dobles sentidos (si aparecen, explicarlos).
- Sin decoración ni elementos de relleno; imágenes reales y nítidas.

### Dislexia
- Letra sans-serif grande (plantilla `egokitua`), interlineado amplio, textos cortos (máx. 3–4 frases por bloque).
- Vocabulario anticipado con imagen; palabras clave destacadas **con moderación**.
- Respuesta oral, de señalar o de rodear como alternativa a escribir.
- No penalizar ortografía cuando no es el objetivo.

### Diskalkulia
- Manipulativos y su dibujo (bloques M·E·H·B, recta numérica, monedas reales).
- Tabla de pasos («Irakurri · Pentsatu · Egin · Berrikusi»).
- Separar comprensión del problema y cálculo; espacio amplio para operar, números bien alineados.

### HGN / AL (lenguaje)
- Vocabulario por **campos semánticos**, con imagen real.
- **Modelos de frase** para completar («… nahi dut», «… -k … egiten du»), trabajo de marcas de caso (-k, -ri, -n, -ra…).
- Narración con **secuencias de 3–4 imágenes**.
- Consignas breves, concretas, de una en una.

### Dislaliak / fonemas (AL)
- Secuencia por fonema: **aislado → sílaba → palabra (inicio / medio / final) → frase → habla libre**.
- Juegos de praxias y respiración como apoyo, siempre en formato lúdico.
- Una ficha = un fonema; imágenes cuyo nombre contenga el fonema en la posición trabajada.

### Euskara L2 / incorporación tardía
- **Vocabulario de supervivencia** primero (aula, escuela, necesidades) con glosario visual.
- Modelos de frase útiles: «… nahi dut», «… behar dut», «Ez dut ulertzen», «Lagunduko didazu?».
- Respetar la lengua 1 (IDU 2.3): hueco opcional para escribir la palabra en su lengua.

### LH 1 sin lectoescritura
- Orden: **conciencia fonológica** (rimas, palmadas silábicas, sonido inicial) → vocales → consonantes frecuentes (m, p, t, l, s, n…) → sílabas abiertas → palabras cortas → frases cortas.
- Primero **solo mayúsculas**, después parejas mayúscula-minúscula (A-a). Nada de letra ligada hasta afianzar.
- Rutinas cortas y multisensoriales (repasar, recortar, plastilina): fichas breves para 10–15 min diarios.

## Al entregar (en el PR)
Para cada ficha adaptada, una tabla breve:

| Zer aldatu da | Zergatik | IDU jarraibidea |
|---|---|---|
| Testua 3 esalditara murriztu | irakurketa-ulermena | 2.2 |

Pautas IDU por número: **Inplikazioa** 7 (interesak), 8 (ahalegina eta iraunkortasuna), 9 (gaitasun emozionala) · **Irudikapena** 1 (pertzepzioa), 2 (hizkuntza eta sinboloak), 3 (ezagutza eraikitzea) · **Ekintza eta adierazpena** 4 (interakzioa), 5 (adierazpena), 6 (funtzio exekutiboak).

## Lista de control
- [ ] Euskara correcto y al nivel del alumno; una instrucción por línea.
- [ ] Ejemplo resuelto y graduación ⭐ → ⭐⭐⭐.
- [ ] Adaptaciones del perfil aplicadas (sección de arriba).
- [ ] Sin lenguaje de diagnóstico; siglas correctas.
- [ ] Funciona en blanco y negro; sin ARASAAC.
- [ ] Gutxieneko helburua indicado.
- [ ] Nota para la familia en euskera y castellano (si la ficha la lleva).
- [ ] Tabla «Zer aldatu | Zergatik | IDU» en el PR.
