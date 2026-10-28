// Ajusta las hojas A4 al ancho de la pantalla e imprime con o sin soluciones.
(function () {
  const marcos = [...document.querySelectorAll(".hoja-marco")];
  const MM = 96 / 25.4;

  function ajustar() {
    const ancho = document.querySelector(".hojas").clientWidth;
    marcos.forEach((marco) => {
      const hoja = marco.querySelector(".hoja");
      const natural = (hoja.classList.contains("horizontal") ? 297 : 210) * MM;
      marco.style.zoom = Math.min(1, ancho / natural);
    });
  }

  document.querySelectorAll("[data-imprimir]").forEach((boton) => {
    boton.addEventListener("click", () => {
      const conSoluciones = boton.dataset.imprimir === "todo";
      marcos.forEach((marco) => {
        marco.classList.toggle("oculta-impresion", !conSoluciones && marco.classList.contains("oculta-impresion-alumno"));
      });
      window.print();
    });
  });

  const iniciar = document.querySelector("[data-egin-pantailan]");
  const panel = document.querySelector("[data-pantaila-ariketak]");
  if (iniciar && panel) {
    const contenido = panel.querySelector("[data-ariketak-interaktiboak]");
    const botonCorregir = panel.querySelector("[data-zuzendu]");
    const botonSalir = panel.querySelector("[data-irten]");
    const botonImprimir = panel.querySelector("[data-inprimatu-erantzunak]");
    const batBanan = panel.querySelector("[data-bat-banan]");
    const anterior = panel.querySelector("[data-aurrekoa]");
    const siguiente = panel.querySelector("[data-hurrengoa]");
    const numeroEjercicio = panel.querySelector("[data-ariketa-zenbakia]");
    const resultado = panel.querySelector("[data-emaitza]");
    const storageKey = `kimu-erantzunak:${location.pathname}`;
    let respuestas = {};
    let criterios = [];
    let preparados = false;
    let indiceVisible = 0;
    let restaurarUno = false;

    try {
      const guardadas = JSON.parse(localStorage.getItem(storageKey) || "{}");
      respuestas = guardadas && typeof guardadas === "object" && !Array.isArray(guardadas) ? guardadas : {};
    } catch (_) {
      respuestas = {};
    }

    function guardar() {
      try {
        localStorage.setItem(storageKey, JSON.stringify(respuestas));
      } catch (_) {
        // El ejercicio continúa funcionando si el navegador bloquea el almacenamiento.
      }
    }

    function normalizar(valor) {
      return String(valor == null ? "" : valor)
        .toLocaleLowerCase()
        .replace(/(\d)\.(?=\d)/g, "$1")
        .replace(/[.!?;:,]+$/g, "")
        .replace(/\s+/g, "");
    }

    function listaSoluciones(solucion) {
      return Array.isArray(solucion) ? solucion : [solucion];
    }

    function respuestaItem(solucion, texto, indice, cantidad) {
      const soluciones = listaSoluciones(solucion);
      const etiqueta = String(texto).match(/^\s*([a-z]\))/i);
      let respuesta;
      if (etiqueta) {
        respuesta = soluciones.find((item) => String(item).trim().toLowerCase().startsWith(etiqueta[1].toLowerCase()));
      }
      if (respuesta == null && soluciones.length === cantidad) respuesta = soluciones[indice];
      if (respuesta == null && soluciones.length === 1) respuesta = soluciones[0];
      return respuesta == null ? null : String(respuesta).replace(/^\s*(?:[a-z]\)\s*|\d+[.)]\s+)/i, "").trim();
    }

    function respuestasHuecos(enunciado, respuesta) {
      if (respuesta == null) return [];
      const prompt = String(enunciado)
        .replace(/:[a-z0-9]+(?:-[a-z0-9]+)*:/gi, "")
        .replace(/_____|___|\[\s*\]/g, "\u0000")
        .replace(/^\s*(?:[a-z]\)\s*|\d+[.)]\s+)/i, "")
        .replace(/\*\*/g, "").replace(/[{}]/g, "");
      if (!prompt.includes("\u0000")) return [];
      const partes = normalizar(prompt).split("\u0000");
      const patron = new RegExp(partes.map((parte) => parte.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("(.+?)"));
      const match = normalizar(respuesta).match(patron);
      const cantidad = partes.length - 1;
      const ultimosNumeros = String(respuesta).split("=").pop().match(/\d+(?:\.\d+)*/g) || [];
      const usaPosiciones = /(?:M|E|H|B)\s*(?:\+|$)/i.test(enunciado);
      if (match && !(cantidad > 1 && !usaPosiciones && ultimosNumeros.length === cantidad)) return match.slice(1);
      return ultimosNumeros.length === cantidad ? ultimosNumeros : [];
    }

    function crearBoton(texto, clase) {
      const boton = document.createElement("button");
      boton.type = "button";
      boton.className = clase || "interactivo-boton";
      boton.textContent = texto;
      return boton;
    }

    function registrar(clave, esperado, leer, elemento, correctos) {
      if (esperado == null || String(esperado).trim() === "") return;
      criterios.push({ esperado, leer, elemento, correctos: correctos || [] });
    }

    function guardarValor(control, clave) {
      control.dataset.answerKey = clave;
      if (Object.prototype.hasOwnProperty.call(respuestas, clave)) control.value = respuestas[clave];
      control.addEventListener("input", () => {
        respuestas[clave] = control.value;
        guardar();
      });
    }

    function campoTexto(etiqueta, clave, expected, holder) {
      const input = document.createElement("input");
      input.type = "text";
      input.className = "pantaila-erantzuna";
      input.setAttribute("aria-label", etiqueta);
      guardarValor(input, clave);
      holder.replaceWith(input);
      if (expected != null) registrar(clave, expected, () => input.value, input);
      return input;
    }

    function areaTestua(etiqueta, clave, holder) {
      const area = document.createElement("textarea");
      area.className = "pantaila-testua";
      area.rows = 3;
      area.setAttribute("aria-label", etiqueta);
      guardarValor(area, clave);
      if (holder) holder.replaceWith(area);
      return area;
    }

    function aukeraTaldea(holder, options, expected, key, label) {
      const group = document.createElement("div");
      group.className = "pantaila-aukerak";
      let selected = respuestas[key] || "";
      const buttons = options.map((option) => {
        const button = crearBoton(option.text, "interaktibo-boton");
        button.setAttribute("aria-pressed", String(selected === option.value));
        button.addEventListener("click", () => {
          selected = option.value;
          respuestas[key] = selected;
          buttons.forEach((other) => other.setAttribute("aria-pressed", String(other === button)));
          guardar();
        });
        group.append(button);
        return button;
      });
      holder.replaceWith(group);
      if (expected != null) {
        const correct = options.filter((option) => normalizar(option.value) === normalizar(expected)
          || normalizar(expected).startsWith(`${normalizar(option.value)}(`));
        registrar(key, expected, () => selected, group, correct.map((option) => buttons[options.indexOf(option)]));
      }
      return group;
    }

    function parekatzeak(solution, left, right) {
      const map = {};
      listaSoluciones(solution).forEach((item, index) => {
        const value = String(item);
        const pair = value.match(/^\s*(.+?)\s*(?:→|->|:)\s*(.+?)\s*$/);
        if (pair) {
          const a = left.findIndex((text) => normalizar(text) === normalizar(pair[1]));
          if (a >= 0) {
            map[a] = pair[2].trim();
            return;
          }
        }
        const numbered = value.match(/^\s*(\d+)[.)]\s*(.+)$/);
        if (numbered) map[Number(numbered[1]) - 1] = numbered[2].trim();
        else if (left[index] != null) map[index] = value.trim();
      });
      return map;
    }

    function sailkapenIrtenbideak(solution, categories) {
      const text = Array.isArray(solution) ? solution.join(". ") : String(solution || "");
      const map = {};
      const chunks = text.matchAll(/(?:^|[.·]\s*)([^:.·]+?):\s*([^·]+?)(?=(?:[.·]\s+[^:.·]+?:)|[.·]?\s*$)/g);
      for (const [, category, words] of chunks) {
        const label = category.trim();
        const alignedCategory = categories.find((item) => normalizar(item) === normalizar(label)
          || normalizar(label).replace(/k$/, "") === normalizar(item)) || label;
        words.split(/[,;]|\s+eta\s+/i).forEach((word) => {
          if (word.trim()) map[normalizar(word)] = alignedCategory;
        });
      }
      return map;
    }

    function prestatuAriketa(source, index) {
      let ejercicio;
      try {
        ejercicio = JSON.parse(source.dataset.ejercicio);
      } catch (_) {
        return;
      }
      const card = source.cloneNode(true);
      card.classList.add("pantaila-ariketa");
      card.dataset.exerciseIndex = index;
      const body = card.querySelector(".ej-cuerpo");
      const prefix = `${index}:`;

      if (ejercicio.modo === "completar") {
        body.querySelectorAll(".frase").forEach((frase, itemIndex) => {
          let expected = respuestaItem(ejercicio.solucion, ejercicio.frases[itemIndex], itemIndex, ejercicio.frases.length);
          const holes = [...frase.querySelectorAll(".hueco")];
          if (!holes.length) {
            areaTestua(`Erantzuna ${itemIndex + 1}`, `${prefix}c${itemIndex}`, frase);
          } else {
            const fields = respuestasHuecos(ejercicio.frases[itemIndex], expected);
            holes.forEach((hole, blankIndex) => {
              let answer = fields[blankIndex] || (holes.length === 1 ? expected : null);
              if (!fields.length && holes.length > 1 && expected) {
                const parts = expected.split(/[;|]/).map((part) => part.trim());
                answer = parts.length === holes.length ? parts[blankIndex] : null;
              }
              campoTexto(`Erantzuna ${itemIndex + 1}`, `${prefix}c${itemIndex}-${blankIndex}`, answer, hole);
            });
          }
        });
      } else if (ejercicio.modo === "elegir") {
        body.querySelectorAll(".item-elegir").forEach((item, itemIndex) => {
          const prompt = item.querySelector(".frase");
          const expected = respuestaItem(ejercicio.solucion, ejercicio.items[itemIndex].texto, itemIndex, ejercicio.items.length);
          const holder = item.querySelector(".opciones");
          const options = [...holder.querySelectorAll(".opcion")].map((option, optionIndex) => ({
            text: option.textContent.trim(), value: option.textContent.trim(), index: optionIndex,
          }));
          aukeraTaldea(holder, options, expected, `${prefix}e${itemIndex}`, prompt.textContent.trim());
        });
      } else if (ejercicio.modo === "verdadero_falso") {
        const labels = ejercicio.etiquetas || (document.documentElement.lang === "es" ? ["VERDADERO", "FALSO"] : ["EGIA", "GEZURRA"]);
        const rows = [...body.querySelectorAll(".vf")].filter((row) => !row.querySelector(".vf-cab"));
        rows.forEach((row, itemIndex) => {
          const statement = row.querySelector("span");
          const expected = respuestaItem(ejercicio.solucion, ejercicio.items[itemIndex], itemIndex, ejercicio.items.length);
          const holder = document.createElement("span");
          row.replaceChildren(statement, holder);
          aukeraTaldea(holder, labels.map((text) => ({ text, value: text })), expected, `${prefix}v${itemIndex}`, statement.textContent.trim());
        });
      } else if (ejercicio.modo === "preguntas") {
        body.querySelectorAll(".pregunta").forEach((question, itemIndex) => {
          const lines = [...question.querySelectorAll(".linea")];
          areaTestua(`Erantzuna ${itemIndex + 1}`, `${prefix}p${itemIndex}`, lines[0]);
          lines.slice(1).forEach((line) => line.remove());
        });
      } else if (ejercicio.modo === "corregir") {
        body.querySelectorAll(".pregunta").forEach((question, itemIndex) => {
          const expected = respuestaItem(ejercicio.solucion, ejercicio.frases[itemIndex], itemIndex, ejercicio.frases.length);
          const answer = areaTestua(`Erantzuna ${itemIndex + 1}`, `${prefix}r${itemIndex}`, question.querySelector(".linea"));
          if (expected != null) registrar(`${prefix}r${itemIndex}`, expected, () => answer.value, answer);
        });
      } else if (ejercicio.modo === "lineas") {
        body.querySelectorAll(".linea").forEach((line, lineIndex) => {
          areaTestua(`Erantzuna ${lineIndex + 1}`, `${prefix}l${lineIndex}`, line);
        });
      } else if (ejercicio.modo === "relacionar") {
        const old = body.querySelector(".relacionar");
        const leftElements = [...old.querySelectorAll(".rel-izq")];
        const rightElements = [...old.querySelectorAll(".rel-der")];
        const left = leftElements.map((item) => item.textContent.trim());
        const right = rightElements.map((item) => item.textContent.trim());
        const expected = parekatzeak(ejercicio.solucion, left, right);
        const area = document.createElement("div");
        area.className = "pantaila-lotu";
        const pairList = document.createElement("div");
        pairList.className = "pantaila-lotu-zerrenda";
        const rightList = document.createElement("div");
        rightList.className = "pantaila-aukerak";
        let activeLeft = null;
        const assignments = respuestas[`${prefix}r`] || {};
        const rightOrder = right.map((_, rightIndex) => rightIndex);
        for (let i = rightOrder.length - 1; i > 0; i -= 1) {
          const j = Math.floor(Math.random() * (i + 1));
          [rightOrder[i], rightOrder[j]] = [rightOrder[j], rightOrder[i]];
        }
        const leftButtons = left.map((text, itemIndex) => {
          const row = document.createElement("div");
          row.className = "pantaila-parea";
          const button = crearBoton("", "interaktibo-boton");
          button.innerHTML = leftElements[itemIndex].innerHTML;
          button.setAttribute("aria-pressed", "false");
          const match = document.createElement("span");
          match.className = "pantaila-parea-erantzuna";
          if (Number.isInteger(assignments[itemIndex])) match.textContent = right[assignments[itemIndex]];
          button.addEventListener("click", () => {
            activeLeft = itemIndex;
            leftButtons.forEach((other) => other.setAttribute("aria-pressed", String(other === button)));
          });
          row.append(button, match);
          pairList.append(row);
          return button;
        });
        rightOrder.forEach((rightIndex) => {
          const text = right[rightIndex];
          const button = crearBoton("", "interaktibo-boton");
          button.innerHTML = rightElements[rightIndex].innerHTML;
          button.addEventListener("click", () => {
            if (activeLeft == null) return;
            Object.keys(assignments).forEach((assignedLeft) => {
              if (Number(assignedLeft) !== activeLeft && assignments[assignedLeft] === rightIndex) {
                delete assignments[assignedLeft];
                pairList.children[assignedLeft].querySelector(".pantaila-parea-erantzuna").textContent = "";
              }
            });
            assignments[activeLeft] = rightIndex;
            pairList.children[activeLeft].querySelector(".pantaila-parea-erantzuna").textContent = text;
            respuestas[`${prefix}r`] = assignments;
            leftButtons[activeLeft].setAttribute("aria-pressed", "false");
            activeLeft = null;
            guardar();
          });
          rightList.append(button);
        });
        area.append(pairList, rightList);
        old.replaceWith(area);
        left.forEach((text, itemIndex) => {
          if (expected[itemIndex] == null) return;
          registrar(`${prefix}r${itemIndex}`, expected[itemIndex],
            () => Number.isInteger(assignments[itemIndex]) ? right[assignments[itemIndex]] : "",
            leftButtons[itemIndex]);
        });
      } else if (ejercicio.modo === "clasificar") {
        const table = body.querySelector(".b-tabla");
        const words = [...body.querySelectorAll(".opciones .opcion")].map((word) => word.textContent.trim());
        const categories = [...table.querySelectorAll("thead th")].map((cell) => cell.textContent.trim());
        const expected = sailkapenIrtenbideak(ejercicio.solucion, categories);
        const assignments = respuestas[`${prefix}k`] || {};
        const area = document.createElement("div");
        area.className = "pantaila-sailkatu";
        let selectedWord = null;
        const wordButtons = words.map((word, wordIndex) => {
          const button = crearBoton(word, "interaktibo-boton");
          button.setAttribute("aria-pressed", "false");
          button.addEventListener("click", () => {
            selectedWord = wordIndex;
            wordButtons.forEach((other) => other.setAttribute("aria-pressed", String(other === button)));
          });
          area.append(button);
          return button;
        });
        const categoryArea = document.createElement("div");
        categoryArea.className = "pantaila-aukerak";
        categories.forEach((category) => {
          const button = crearBoton(category, "interaktibo-boton");
          button.addEventListener("click", () => {
            if (selectedWord == null) return;
            assignments[selectedWord] = category;
            wordButtons[selectedWord].dataset.category = category;
            wordButtons[selectedWord].setAttribute("aria-pressed", "false");
            wordButtons[selectedWord].classList.add("word-assigned");
            selectedWord = null;
            respuestas[`${prefix}k`] = assignments;
            guardar();
          });
          categoryArea.append(button);
        });
        area.append(categoryArea);
        body.querySelector(".opciones")?.replaceWith(area);
        table.replaceWith(document.createElement("div"));
        words.forEach((word, wordIndex) => {
          if (expected[normalizar(word)] == null) return;
          registrar(`${prefix}k${wordIndex}`, expected[normalizar(word)],
            () => assignments[wordIndex] || "", wordButtons[wordIndex]);
          if (assignments[wordIndex]) {
            wordButtons[wordIndex].dataset.category = assignments[wordIndex];
            wordButtons[wordIndex].classList.add("word-assigned");
          }
        });
      } else if (ejercicio.modo === "operaciones") {
        body.querySelectorAll(".op-item").forEach((item, itemIndex) => {
          const letter = `${"abcdefghijkl"[itemIndex]})`;
          const expected = respuestaItem(ejercicio.solucion, letter, itemIndex, ejercicio.items.length);
          const blanks = [...item.querySelectorAll(".op-res .hueco")];
          const inputs = blanks.map((blank, blankIndex) => {
            const input = document.createElement("input");
            input.type = "text";
            input.inputMode = "numeric";
            input.maxLength = 1;
            input.className = "pantaila-erantzuna zifra-erantzuna";
            input.setAttribute("aria-label", `Eragiketaren ${itemIndex + 1}. emaitzako ${blankIndex + 1}. zifra`);
            guardarValor(input, `${prefix}o${itemIndex}-${blankIndex}`);
            blank.replaceWith(input);
            return input;
          });
          if (expected != null && inputs.length) {
            registrar(`${prefix}o${itemIndex}`, expected,
              () => inputs.map((input) => input.value).join("").replace(/^0+/, "") || "0", item);
          }
        });
      } else {
        body.querySelectorAll(".hueco, .linea").forEach((holder, fieldIndex) => {
          areaTestua(`Erantzuna ${fieldIndex + 1}`, `${prefix}o${fieldIndex}`, holder);
        });
      }
      contenido.append(card);
    }

    function zuzendu() {
      let zuzen = 0;
      criterios.forEach((criterion) => {
        const correct = normalizar(criterion.leer()) === normalizar(criterion.esperado);
        if (correct) zuzen += 1;
        criterion.elemento.classList.toggle("erantzun-zuzen", correct);
        criterion.elemento.classList.toggle("erantzun-oker", !correct);
        criterion.correctos.forEach((button) => button.classList.add("erantzun-zuzen"));
        if (!correct && criterion.correctos.length) {
          const chosen = criterion.elemento.querySelector('[aria-pressed="true"]');
          if (chosen) chosen.classList.add("erantzun-oker");
        }
      });
      const total = criterios.length;
      resultado.textContent = total ? `${zuzen} / ${total}` : "";
    }

    function erakutsiBanaka() {
      const cards = [...contenido.querySelectorAll(".pantaila-ariketa")];
      cards.forEach((card, index) => { card.hidden = batBanan.checked && index !== indiceVisible; });
      anterior.hidden = !batBanan.checked;
      siguiente.hidden = !batBanan.checked;
      numeroEjercicio.textContent = batBanan.checked && cards.length ? `${indiceVisible + 1} / ${cards.length}` : "";
    }

    iniciar.addEventListener("click", () => {
      if (!preparados) {
        criterios = [];
        document.querySelectorAll(".hojas .b-ejercicio[data-ejercicio]").forEach((source, index) => prestatuAriketa(source, index));
        preparados = true;
      }
      document.body.classList.add("modo-pantaila");
      panel.hidden = false;
      indiceVisible = 0;
      erakutsiBanaka();
      panel.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    botonCorregir.addEventListener("click", zuzendu);
    botonSalir.addEventListener("click", () => {
      document.body.classList.remove("modo-pantaila");
      panel.hidden = true;
    });
    botonImprimir.addEventListener("click", () => {
      restaurarUno = batBanan.checked;
      batBanan.checked = false;
      erakutsiBanaka();
      document.body.classList.add("inprimatu-erantzunak");
      window.print();
    });
    batBanan.addEventListener("change", erakutsiBanaka);
    anterior.addEventListener("click", () => {
      indiceVisible = Math.max(0, indiceVisible - 1);
      erakutsiBanaka();
    });
    siguiente.addEventListener("click", () => {
      indiceVisible = Math.min(contenido.querySelectorAll(".pantaila-ariketa").length - 1, indiceVisible + 1);
      erakutsiBanaka();
    });
    window.addEventListener("afterprint", () => {
      document.body.classList.remove("inprimatu-erantzunak");
      batBanan.checked = restaurarUno;
      erakutsiBanaka();
    });
  }

  window.addEventListener("resize", ajustar);
  ajustar();
})();
