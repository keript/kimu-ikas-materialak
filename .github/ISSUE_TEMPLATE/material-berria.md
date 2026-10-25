---
name: Material berria
about: Añadir un material nuevo (asígnaselo a Copilot)
title: "Material berria: "
labels: material
---

## Material

- **Tema:**
- **Curso:**
- **Sección:** ortografia

## Contenido

<!-- Opción A: pega aquí el JSON que te ha dado Gemini/Claude (ya revisado por ti). -->
<!-- Opción B: describe el material y deja que Copilot lo redacte siguiendo prompts/material-berria.md. -->

```json

```

## Tareas para Copilot

- [ ] Crear `contenido/materiales/<id>.json` con el contenido de arriba, sin cambiar los textos en euskera.
- [ ] Si hay SVG nuevos, guardarlos en `contenido/ilustraciones/`.
- [ ] Dejar `"publicado": false` hasta que el autor lo revise.
- [ ] Ejecutar `python scripts/build.py` y confirmar que no hay errores.
- [ ] En el PR, listar las palabras o frases que convenga revisar.
