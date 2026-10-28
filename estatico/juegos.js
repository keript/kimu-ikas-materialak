// Motor común de los juegos de Kimu.
// No hace falta tocarlo para añadir materiales: los datos llegan desde
// contenido/materiales/<id>.json a través del bloque <script id="kimu-datos">.
(function () {
  const datos = JSON.parse(document.getElementById("kimu-datos").textContent);
  const illustrations = datos.ilustraciones;
  const juegos = Object.fromEntries(datos.juegos.map((juego) => [juego.id, juego]));
  const contarEvento = (path) => {
    if (window.goatcounter && typeof window.goatcounter.count === "function") {
      window.goatcounter.count({ path });
    }
  };

  function claseOpciones(tipo, prefijo) {
    if (tipo === "letra") return ` letter-${prefijo}`;
    if (tipo === "frase") return ` sentence-${prefijo}`;
    return "";
  }

  // Fichas imprimibles
  document.querySelectorAll("[data-worksheet-items]").forEach((container) => {
    const juego = juegos[container.dataset.worksheetItems];
    juego.preguntas.forEach((question, index) => {
      const item = document.createElement("section");
      item.className = "worksheet-item";
      item.setAttribute("aria-label", `${index + 1}. ariketa`);
      const image = document.createElement("div");
      image.innerHTML = illustrations[question.ilustracion];
      const choices = document.createElement("div");
      choices.className = `worksheet-choices${claseOpciones(juego.tipo, "worksheet")}`;
      question.opciones.forEach((option) => {
        const choice = document.createElement("span");
        choice.textContent = option;
        choices.append(choice);
      });
      item.append(image.firstElementChild, choices);
      container.append(item);
    });
  });

  // Juegos en pantalla
  document.querySelectorAll(".visual-activity").forEach((activity) => {
    const juego = juegos[activity.dataset.game];
    const questions = juego.preguntas;
    const picture = activity.querySelector(".game-picture");
    const prompt = activity.querySelector(".game-prompt");
    const step = activity.querySelector(".game-step");
    const stars = activity.querySelector(".game-stars");
    const options = [...activity.querySelectorAll(".game-choice")];
    const feedback = activity.querySelector(".game-feedback");
    const next = activity.querySelector(".game-next");
    const restart = activity.querySelector(".game-restart");
    let questionIndex = 0;
    let answered = false;

    function updateStars(completed) {
      stars.textContent = Array.from({ length: questions.length }, (_, index) => index < completed ? "⭐" : "☆").join(" ");
      stars.setAttribute("aria-label", `${completed} / ${questions.length} galdera eginda`);
    }

    function showQuestion() {
      const question = questions[questionIndex];
      answered = false;
      updateStars(questionIndex);
      picture.innerHTML = illustrations[question.ilustracion];
      prompt.textContent = question.pregunta;
      step.textContent = `${questionIndex + 1} / ${questions.length}`;
      feedback.textContent = "";
      next.hidden = true;
      restart.hidden = true;
      options.forEach((button, index) => {
        button.textContent = question.opciones[index];
        button.disabled = false;
        button.className = `game-choice${claseOpciones(juego.tipo, "choice")}`;
      });
    }

    options.forEach((button, index) => {
      button.addEventListener("click", () => {
        if (answered) return;
        const question = questions[questionIndex];
        options.forEach((option) => option.classList.remove("choice-wrong"));
        if (index !== question.correcta) {
          button.classList.add("choice-wrong");
          feedback.textContent = juego.error;
          return;
        }

        answered = true;
        updateStars(questionIndex + 1);
        button.classList.add("choice-right");
        options.forEach((option) => { option.disabled = true; });
        feedback.textContent = juego.acierto;
        if (questionIndex === questions.length - 1) {
          contarEvento(`jolasa-amaitu/${datos.material}/${juego.id}`);
          step.textContent = `${questions.length} / ${questions.length} · Amaituta!`;
          restart.hidden = false;
        } else {
          next.hidden = false;
        }
      });
    });

    next.addEventListener("click", () => {
      questionIndex += 1;
      showQuestion();
      options[0].focus();
    });

    restart.addEventListener("click", () => {
      questionIndex = 0;
      showQuestion();
      options[0].focus();
    });

    showQuestion();
  });

  // Descargar e imprimir fichas
  const standaloneStyles = `
    * { box-sizing: border-box; }
    body { margin: 0; padding: 20px; color: #20241f; background: #f7f7f2; font: 18px/1.5 Arial, sans-serif; }
    .worksheet-page { width: 100%; max-width: 760px; margin: 0 auto; padding: 28px; border: 3px solid #b8f36b; border-radius: 24px; background: #fff; }
    .worksheet-heading { display: flex; align-items: center; gap: 18px; padding-bottom: 16px; border-bottom: 3px solid #b8f36b; }
    .worksheet-heading > span { font-size: 48px; }
    .worksheet-heading > span svg { width: 52px; height: 52px; display: block; }
    .worksheet-heading p { margin: 0; color: #51584c; font-size: 14px; font-weight: 700; }
    .worksheet-heading h2 { margin: 3px 0; font-size: 30px; }
    .worksheet-name { margin: 16px 0; font-size: 16px; }
    .worksheet-name span { display: inline-block; width: 65%; border-bottom: 2px solid #c6ccbe; }
    .worksheet-items { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
    .worksheet-item { display: grid; grid-template-columns: 68px minmax(0, 1fr); align-items: center; gap: 8px; min-height: 0; margin: 0; padding: 8px; border: 2px solid #e1e5dc; border-radius: 14px; background: #f8faf4; page-break-inside: avoid; break-inside: avoid; }
    .worksheet-item svg { display: block; width: 64px; height: 64px; }
    .worksheet-choices { display: flex; justify-content: stretch; gap: 6px; }
    .worksheet-choices span { min-width: 0; flex: 1; padding: 8px 4px; border: 2px solid #d8ded0; border-radius: 12px; background: #fff; text-align: center; font-size: 20px; font-weight: 800; line-height: 1.2; }
    .worksheet-choices.letter-worksheet span { font-size: 36px; }
    .worksheet-choices.sentence-worksheet span { font-size: 16px; }
    .worksheet-footer { margin-top: 16px; color: #426b24; text-align: center; font-weight: 700; }
    .print-hint { max-width: 760px; margin: 14px auto; color: #51584c; font: 14px/1.5 Arial, sans-serif; }
    @page { size: A4 portrait; margin: 12mm; }
    @media print { body { padding: 0; background: #fff; } .worksheet-page { max-width: none; padding: 0; border: 0; } .print-hint { display: none; } }
    @media (max-width: 560px) { body { padding: 10px; } .worksheet-page { padding: 16px; } .worksheet-items { grid-template-columns: 1fr; } .worksheet-item { grid-template-columns: 68px minmax(0, 1fr); } .worksheet-choices span { padding: 9px 4px; } }
  `;

  document.querySelectorAll(".download-activity").forEach((button) => {
    button.addEventListener("click", () => {
      contarEvento("inprimatu");
      const worksheet = document.getElementById(button.dataset.worksheet);
      const title = worksheet.querySelector("h2").textContent;
      const file = `<!doctype html><html lang="eu"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Kimu — ${title}</title><style>${standaloneStyles}</style></head><body>${worksheet.outerHTML}<p class="print-hint">Inprimatzeko: ireki fitxa hau eta aukeratu “Inprimatu” edo “Gorde PDF gisa”.</p></body></html>`;
      const url = URL.createObjectURL(new Blob([file], { type: "text/html;charset=utf-8" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = `kimu-${datos.material}-${button.dataset.worksheet.replace("worksheet-", "")}.html`;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  });

  document.querySelectorAll(".print-activity").forEach((button) => {
    button.addEventListener("click", () => {
      contarEvento("inprimatu");
      document.querySelectorAll(".worksheet-page.is-printing").forEach((page) => page.classList.remove("is-printing"));
      document.getElementById(button.dataset.print).classList.add("is-printing");
      window.print();
    });
  });

  window.addEventListener("afterprint", () => {
    document.querySelectorAll(".worksheet-page.is-printing").forEach((page) => page.classList.remove("is-printing"));
  });
})();
