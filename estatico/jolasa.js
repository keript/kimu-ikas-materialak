(() => {
  const data = JSON.parse(document.getElementById("joko-datuak").textContent);
  const text = data.ui;
  const contarEvento = (path) => {
    if (window.goatcounter && typeof window.goatcounter.count === "function") {
      window.goatcounter.count({ path });
    }
  };
  const colors = ["#b93838", "#176b9a", "#26804e", "#7952a1"];
  const shapes = ["▲", "◆", "●", "■"];
  const names = {
    eu: ["Gorria", "Urdina", "Berdea", "Morea"],
    es: ["Rojo", "Azul", "Verde", "Morado"],
  }[document.documentElement.lang] || ["Gorria", "Urdina", "Berdea", "Morea"];

  const setup = document.getElementById("hasiera");
  const game = document.getElementById("jokoa");
  const final = document.getElementById("amaiera");
  const count = document.getElementById("talde-kopurua");
  const teamFields = document.getElementById("taldeak-konfiguratu");
  const durationField = document.getElementById("galderako-denbora");
  const startButton = document.getElementById("jolasa-hasi");
  const fullscreenButton = document.getElementById("pantaila-osoa");
  const questionCount = document.getElementById("galdera-kopurua");
  const timer = document.getElementById("denbora");
  const timerBar = document.getElementById("denbora-barra");
  const scoreBoard = document.getElementById("talde-markagailua");
  const questionText = document.getElementById("galdera");
  const questionImage = document.getElementById("galdera-irudia");
  const answers = document.getElementById("erantzunak");
  const status = document.getElementById("egoera");
  const revealButton = document.getElementById("erantzuna-erakutsi");
  const awardPanel = document.getElementById("puntuak-ematea");
  const teamAwards = document.getElementById("talde-puntuak");
  const noPointButton = document.getElementById("punturik-ez");
  const nextButton = document.getElementById("hurrengoa");
  const finalRanking = document.getElementById("azken-sailkapena");
  let teams = [];
  let questions = [];
  let questionIndex = 0;
  let chosen = null;
  let secondsLeft = 0;
  let duration = 0;
  let clock = null;
  let revealed = false;
  let awarded = false;
  let solo = false;
  let tries = 0;
  const soundBox = document.getElementById("soinua");
  let audio = null;

  // Sonido suave (sin archivos): acierto = dos notas que suben; fallo = una nota grave y corta.
  function beep(notes) {
    if (!soundBox || !soundBox.checked) return;
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      let t = audio.currentTime;
      notes.forEach(([freq, len]) => {
        const osc = audio.createOscillator();
        const gain = audio.createGain();
        osc.type = "sine";
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.0001, t);
        gain.gain.exponentialRampToValueAtTime(0.18, t + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + len);
        osc.connect(gain).connect(audio.destination);
        osc.start(t);
        osc.stop(t + len + 0.02);
        t += len * 0.8;
      });
    } catch (e) { /* sin sonido */ }
  }
  const soundOk = () => beep([[660, 0.16], [880, 0.28]]);
  const soundNo = () => beep([[260, 0.22]]);

  function pick(list) {
    return Array.isArray(list) ? list[Math.floor(Math.random() * list.length)] : list;
  }

  // Modo bakarka: se corrige al tocar. Tras un fallo, se quita una opción incorrecta (pista) y se prueba otra vez.
  function soloAnswer(index) {
    if (revealed) return;
    const question = questions[questionIndex];
    const button = answers.children[index];
    if (!button || button.disabled) return;
    tries += 1;
    if (index === question.correcta) {
      button.classList.add("is-correct");
      if (tries === 1) teams[0].score += 1;
      status.textContent = pick(text.well_done);
      soundOk();
      finishSolo();
      return;
    }
    button.classList.add("is-wrong");
    button.disabled = true;
    soundNo();
    const left = [...answers.children].filter((b, i) => !b.disabled && i !== question.correcta);
    if (tries >= 2 || left.length === 0) {
      answers.children[question.correcta].classList.add("is-correct");
      status.textContent = text.show_after;
      finishSolo();
      return;
    }
    const hide = pick(left);
    hide.disabled = true;
    hide.classList.add("is-hidden-hint");
    status.textContent = text.try_again;
  }

  function finishSolo() {
    revealed = true;
    awarded = true;
    stopClock();
    [...answers.children].forEach((b) => { b.disabled = true; });
    revealButton.hidden = true;
    awardPanel.hidden = false;
    teamAwards.replaceChildren();
    noPointButton.hidden = true;
    awardPanel.querySelector("p").hidden = true;
    nextButton.hidden = false;
    nextButton.focus();
    renderScoreboard();
  }

  function renderTeamFields() {
    teamFields.replaceChildren();
    for (let i = 0; i < Number(count.value); i += 1) {
      const row = document.createElement("div");
      row.className = "team-input";
      const name = document.createElement("input");
      name.className = "team-name";
      name.type = "text";
      name.maxLength = 24;
      name.value = `${i + 1}. ${names[i]}`;
      name.setAttribute("aria-label", `${text.team_name} ${i + 1}`);
      const color = document.createElement("input");
      color.className = "team-color";
      color.type = "color";
      color.value = colors[i];
      color.setAttribute("aria-label", `${text.team_name} ${i + 1}: ${text.teams}`);
      row.append(name, color);
      teamFields.append(row);
    }
  }

  function cleanText(value) {
    return String(value)
      .replace(/\*\*(.*?)\*\*/g, "$1")
      .replace(/_(.*?)_/g, "$1")
      .replace(/\{(.*?)\}/g, "$1");
  }

  function shuffle(items) {
    for (let i = items.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [items[i], items[j]] = [items[j], items[i]];
    }
    return items;
  }

  function shuffledQuestion(question) {
    const answersWithKeys = question.opciones.map((label, index) => ({
      label,
      correct: index === question.correcta,
    }));
    shuffle(answersWithKeys);
    return {
      ...question,
      opciones: answersWithKeys.map((answer) => answer.label),
      correcta: answersWithKeys.findIndex((answer) => answer.correct),
    };
  }

  function renderScoreboard() {
    scoreBoard.replaceChildren();
    teams.forEach((team) => {
      const chip = document.createElement("span");
      chip.className = "score-chip";
      chip.style.setProperty("--team-color", team.color);
      chip.textContent = `${team.name}: ${team.score}`;
      scoreBoard.append(chip);
    });
  }

  function stopClock() {
    if (clock !== null) {
      window.clearInterval(clock);
      clock = null;
    }
  }

  function showTimer() {
    timer.classList.toggle("urgent", duration > 0 && secondsLeft <= 5);
    timer.textContent = duration ? `${secondsLeft}` : text.no_time;
    timerBar.style.width = duration ? `${Math.max(0, secondsLeft / duration * 100)}%` : "100%";
  }

  function startClock() {
    stopClock();
    secondsLeft = duration;
    showTimer();
    if (!duration) return;
    clock = window.setInterval(() => {
      secondsLeft -= 1;
      showTimer();
      if (secondsLeft <= 0) {
        stopClock();
        status.textContent = text.time_up;
        if (solo) {
          answers.children[questions[questionIndex].correcta].classList.add("is-correct");
          finishSolo();
          status.textContent = text.show_after;
        } else revealAnswer();
      }
    }, 1000);
  }

  function selectAnswer(index) {
    if (revealed || index < 0 || index >= answers.children.length) return;
    chosen = index;
    [...answers.children].forEach((button, i) => {
      button.classList.toggle("selected", i === chosen);
      button.setAttribute("aria-pressed", i === chosen ? "true" : "false");
    });
  }

  function renderQuestion() {
    const question = questions[questionIndex];
    tries = 0;
    noPointButton.hidden = false;
    awardPanel.querySelector("p").hidden = false;
    chosen = null;
    revealed = false;
    awarded = false;
    questionCount.textContent = `${text.question} ${questionIndex + 1} / ${questions.length}`;
    questionText.textContent = cleanText(question.pregunta);
    if (question.imagen) {
      questionImage.src = `irudiak/${encodeURIComponent(question.imagen)}.svg`;
      questionImage.hidden = false;
    } else {
      questionImage.removeAttribute("src");
      questionImage.hidden = true;
    }
    answers.replaceChildren();
    question.opciones.forEach((label, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `answer answer-${index}`;
      button.setAttribute("aria-pressed", "false");
      button.setAttribute("aria-label", `${index + 1}: ${shapes[index]} ${cleanText(label)}`);
      const shape = document.createElement("span");
      shape.className = "answer-shape";
      shape.setAttribute("aria-hidden", "true");
      shape.textContent = shapes[index];
      const answerText = document.createElement("span");
      answerText.textContent = cleanText(label);
      const number = document.createElement("span");
      number.className = "answer-number";
      number.setAttribute("aria-hidden", "true");
      number.textContent = index + 1;
      button.append(shape, answerText, number);
      button.addEventListener("click", () => (solo ? soloAnswer(index) : selectAnswer(index)));
      answers.append(button);
    });
    status.textContent = "";
    revealButton.hidden = false;
    awardPanel.hidden = true;
    nextButton.hidden = true;
    renderScoreboard();
    startClock();
  }

  function revealAnswer() {
    if (revealed) return;
    if (solo) {
      answers.children[questions[questionIndex].correcta].classList.add("is-correct");
      status.textContent = text.show_after;
      finishSolo();
      return;
    }
    revealed = true;
    stopClock();
    const question = questions[questionIndex];
    [...answers.children].forEach((button, index) => {
      button.disabled = true;
      button.classList.toggle("is-correct", index === question.correcta);
      button.classList.toggle("is-wrong", chosen === index && index !== question.correcta);
    });
    revealButton.hidden = true;
    awardPanel.hidden = false;
    teamAwards.replaceChildren();
    teams.forEach((team, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "team-award";
      button.style.setProperty("--team-color", team.color);
      button.textContent = `${team.name} +1`;
      button.addEventListener("click", () => awardPoint(index));
      teamAwards.append(button);
    });
    status.textContent = text.correct;
    noPointButton.disabled = false;
  }

  function awardPoint(index) {
    if (awarded) return;
    teams[index].score += 1;
    awarded = true;
    status.textContent = `${teams[index].name}: +1 ${text.points}`;
    noPointButton.disabled = true;
    [...teamAwards.children].forEach((button) => { button.disabled = true; });
    nextButton.hidden = false;
    renderScoreboard();
  }

  function finishWithoutPoint() {
    if (awarded) return;
    awarded = true;
    noPointButton.disabled = true;
    [...teamAwards.children].forEach((button) => { button.disabled = true; });
    nextButton.hidden = false;
  }

  function showResults() {
    contarEvento(`jolasa-amaitu/${data.id}/galderak`);
    game.hidden = true;
    final.hidden = false;
    finalRanking.replaceChildren();
    [...teams]
      .sort((a, b) => b.score - a.score)
      .forEach((team, index) => {
        const row = document.createElement("li");
        row.style.setProperty("--team-color", team.color);
        const rank = document.createElement("span");
        rank.className = "podium-rank";
        rank.textContent = `${index + 1}.`;
        const name = document.createElement("span");
        name.textContent = team.name;
        const score = document.createElement("span");
        score.className = "podium-score";
        score.textContent = solo ? `${text.solo_result}: ${team.score} / ${questions.length}` : `${team.score} ${text.points}`;
        row.append(rank, name, score);
        finalRanking.append(row);
      });
  }

  function nextQuestion() {
    if (!revealed || !awarded) return;
    questionIndex += 1;
    if (questionIndex >= questions.length) {
      showResults();
      return;
    }
    renderQuestion();
  }

  function startGame() {
    stopClock();
    teams = [...teamFields.children].map((row, index) => ({
      name: row.querySelector(".team-name").value.trim() || `${index + 1}. ${names[index]}`,
      color: row.querySelector(".team-color").value,
      score: 0,
    }));
    questions = shuffle(data.preguntas.map(shuffledQuestion));
    questionIndex = 0;
    duration = Number(durationField.value);
    solo = teams.length === 1;
    setup.hidden = true;
    final.hidden = true;
    game.hidden = false;
    renderQuestion();
  }

  count.addEventListener("change", renderTeamFields);
  startButton.addEventListener("click", startGame);
  revealButton.addEventListener("click", revealAnswer);
  noPointButton.addEventListener("click", finishWithoutPoint);
  nextButton.addEventListener("click", nextQuestion);
  document.getElementById("berriz-hasi").addEventListener("click", () => {
    final.hidden = true;
    setup.hidden = false;
  });
  fullscreenButton.addEventListener("click", () => {
    if (document.fullscreenElement) {
      document.exitFullscreen?.();
    } else {
      document.documentElement.requestFullscreen?.().catch(() => {});
    }
  });

  document.addEventListener("keydown", (event) => {
    if (setup.hidden && !game.hidden && /^[1-4]$/.test(event.key)) {
      event.preventDefault();
      if (solo) soloAnswer(Number(event.key) - 1);
      else selectAnswer(Number(event.key) - 1);
      return;
    }
    if (event.code === "Space" && !game.hidden) {
      event.preventDefault();
      if (!revealed && solo) return;
      if (!revealed) revealAnswer();
      else {
        if (!awarded) finishWithoutPoint();
        nextQuestion();
      }
    }
  });

  renderTeamFields();
})();
