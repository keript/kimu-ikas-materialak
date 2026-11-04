(() => {
  const data = JSON.parse(document.getElementById("bingo-data").textContent);
  const hitzak = data.hitzak || [];
  const mota = data.mota || "definizioa";
  const kartoiak = data.kartoiak || [];
  const kartoiErrazak = data.kartoi_errazak || [];
  const words = new Map(hitzak.map((item) => [item.hitza, item]));
  const easyWords = new Set(data.erraza || []);
  const storageKey = `kimu-bingoa-${data.id}`;
  const generatedCards = data.kartoi_sortzaileak || {};
  const generatedCodes = Object.values(generatedCards).flatMap((cards) => Object.keys(cards));
  const firstGeneratedCard = Object.keys(generatedCards["4x4"] || {})[0]
    || Object.keys(generatedCards["3x3"] || {})[0]
    || "";
  const validCards = new Set([
    ...kartoiak.map((_, index) => String(index + 1)),
    ...kartoiErrazak.map((_, index) => `E${index + 1}`),
    ...generatedCodes,
  ]);
  const createState = () => ({
    called: [],
    easy: false,
    card: kartoiak.length ? "1" : firstGeneratedCard,
    markedByCard: {},
  });
  let state = createState();
  let currentWord = null;
  let activeMode = "caller";

  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
    if (saved && typeof saved === "object") {
      state = {
        called: Array.isArray(saved.called)
          ? [...new Set(saved.called.filter((word) => words.has(word)))]
          : [],
        easy: saved.easy === true,
        card: validCards.has(saved.card) ? saved.card : "1",
        markedByCard: {},
      };
      if (saved.markedByCard && typeof saved.markedByCard === "object") {
        Object.entries(saved.markedByCard).forEach(([id, marked]) => {
          if (validCards.has(id) && Array.isArray(marked)) {
            state.markedByCard[id] = [...new Set(marked.filter((word) => words.has(word)))];
          }
        });
      }
      currentWord = state.called[state.called.length - 1] || null;
      if (state.easy && currentWord && !easyWords.has(currentWord)) currentWord = null;
    }
  } catch {
    state = createState();
  }

  const persist = () => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(state));
    } catch {
      return;
    }
  };

  const boardFor = (id) => {
    if (generatedCards["3x3"]?.[id]) return generatedCards["3x3"][id];
    if (generatedCards["4x4"]?.[id]) return generatedCards["4x4"][id];
    if (/^E\d+$/.test(id)) return kartoiErrazak[Number(id.slice(1)) - 1];
    if (/^\d+$/.test(id)) return kartoiak[Number(id) - 1];
    return null;
  };

  const boardSize = (board) => Math.sqrt(board.length);

  const hasLine = (board, marked) => {
    const size = boardSize(board);
    const lines = [];
    for (let row = 0; row < size; row += 1) {
      lines.push(board.slice(row * size, (row + 1) * size));
    }
    for (let column = 0; column < size; column += 1) {
      lines.push(Array.from({ length: size }, (_, row) => board[row * size + column]));
    }
    lines.push(Array.from({ length: size }, (_, index) => board[index * size + index]));
    lines.push(Array.from({ length: size }, (_, index) => board[index * size + size - index - 1]));
    return lines.some((line) => line.every((word) => marked.has(word)));
  };

  const statusFor = (board, marked) => {
    if (board.every((word) => marked.has(word))) return "BINGO!";
    if (hasLine(board, marked)) return "LERROA!";
    return "Oraindik ez.";
  };

  const celebrate = () => {
    const success = document.getElementById("bingo-success");
    success.hidden = false;
    success.classList.remove("is-celebrating");
    void success.offsetWidth;
    success.classList.add("is-celebrating");
  };

  const setMode = (mode) => {
    activeMode = mode;
    document.querySelectorAll(".bingoa-mode").forEach((button) => {
      const selected = button.id === `mode-${mode}`;
      button.setAttribute("aria-pressed", String(selected));
      document.getElementById(button.getAttribute("aria-controls")).hidden = !selected;
    });
  };

  document.querySelectorAll(".bingoa-mode").forEach((button) => {
    button.addEventListener("click", () => setMode(button.id.replace("mode-", "")));
  });

  const calledList = document.getElementById("called-words");
  const definition = document.getElementById("definition");
  const callerLabel = document.getElementById("caller-label");
  const callerHelp = document.getElementById("caller-help");
  const firstLetter = document.getElementById("first-letter");
  const easyMode = document.getElementById("easy-mode");
  const callerStatus = document.getElementById("caller-status");

  const renderCalled = () => {
    calledList.replaceChildren(...state.called.map((word) => {
      const item = document.createElement("li");
      item.textContent = word;
      return item;
    }));
  };

  const renderDefinition = () => {
    const entry = currentWord ? words.get(currentWord) : null;
    callerLabel.textContent = mota === "argazkia"
      ? "Hitza"
      : mota === "eragiketa" ? "Eragiketa" : "Definizioa";
    callerHelp.textContent = mota === "argazkia"
      ? "Ikusi argazkia eta esan hitza."
      : mota === "eragiketa" ? "Ebatzi eragiketa eta esan emaitza." : "Irakurri definizioa eta asmatu hitza.";
    definition.replaceChildren();
    if (entry && mota === "argazkia") {
      if (entry.irudia) {
        const image = document.createElement("img");
        image.className = "bingoa-caller-photo";
        image.src = `irudiak-errealak/${encodeURIComponent(entry.irudia)}.jpg`;
        image.alt = "";
        image.addEventListener("error", () => image.remove(), { once: true });
        definition.append(image);
      }
      const word = document.createElement("span");
      word.className = "bingoa-caller-word";
      word.textContent = entry.hitza;
      definition.append(word);
    } else {
      definition.textContent = entry ? entry.definizioa : "Sakatu «Hurrengoa» hasteko.";
    }
    firstLetter.hidden = !(state.easy && entry);
    if (entry) firstLetter.querySelector("span").textContent = currentWord[0];
  };

  const nextWord = () => {
    const pool = state.easy ? hitzak.filter((entry) => easyWords.has(entry.hitza)) : hitzak;
    const remaining = pool.filter((entry) => !state.called.includes(entry.hitza));
    if (!remaining.length) {
      callerStatus.textContent = "Ez dago hitz gehiagorik modu honetan.";
      return;
    }
    const entry = remaining[Math.floor(Math.random() * remaining.length)];
    state.called.push(entry.hitza);
    currentWord = entry.hitza;
    callerStatus.textContent = "";
    renderDefinition();
    renderCalled();
    persist();
  };

  easyMode.checked = state.easy;
  easyMode.addEventListener("change", () => {
    state.easy = easyMode.checked;
    currentWord = null;
    callerStatus.textContent = "";
    renderDefinition();
    persist();
  });

  document.getElementById("next-word").addEventListener("click", nextWord);
  document.addEventListener("keydown", (event) => {
    if (
      event.code === "Space"
      && activeMode === "caller"
      && !event.repeat
      && !event.target.matches("button, input, select, textarea, a, [contenteditable='true']")
    ) {
      event.preventDefault();
      nextWord();
    }
  });

  document.getElementById("restart").addEventListener("click", () => {
    state = createState();
    currentWord = null;
    document.getElementById("bingo-success").hidden = true;
    document.getElementById("bingo-success").classList.remove("is-celebrating");
    easyMode.checked = false;
    callerStatus.textContent = "";
    document.getElementById("check-status").textContent = "";
    document.getElementById("check-card").value = "";
    document.getElementById("check-board").hidden = true;
    renderDefinition();
    renderCalled();
    document.getElementById("my-card").value = state.card;
    renderMyCard();
    persist();
  });

  const makeBoard = (board, marked, interactive, title) => {
    const wrap = document.createElement("div");
    const heading = document.createElement("h3");
    heading.className = "bingoa-board-title";
    heading.textContent = title;
    const grid = document.createElement("ol");
    grid.className = "bingoa-grid";
    if (board.length === 9) grid.classList.add("bingoa-grid-erraza");
    grid.style.setProperty("--board-size", String(boardSize(board)));
    board.forEach((word) => {
      const isMarked = marked.has(word);
      const item = document.createElement("li");
      const cell = document.createElement(interactive ? "button" : "div");
      cell.className = `bingoa-cell${isMarked ? " is-marked" : ""}`;
      const entry = words.get(word);
      if (mota === "argazkia" && entry?.irudia) {
        cell.classList.add("bingoa-cell-with-photo");
        const image = document.createElement("img");
        image.className = "bingoa-cell-photo";
        image.src = `irudiak-errealak/${encodeURIComponent(entry.irudia)}.jpg`;
        image.alt = "";
        image.addEventListener("error", () => {
          image.remove();
          cell.classList.remove("bingoa-cell-with-photo");
        }, { once: true });
        const label = document.createElement("span");
        label.className = "bingoa-cell-label";
        label.textContent = `${isMarked ? "✓ " : ""}${word}`;
        cell.append(image, label);
      } else {
        cell.textContent = `${isMarked ? "✓ " : ""}${word}`;
      }
      if (interactive) {
        cell.type = "button";
        cell.setAttribute("aria-pressed", String(isMarked));
        cell.setAttribute("aria-label", `${word}: ${isMarked ? "markatuta" : "markatu gabe"}`);
        cell.addEventListener("click", () => {
          const currentMarks = new Set(state.markedByCard[state.card] || []);
          if (currentMarks.has(word)) currentMarks.delete(word);
          else currentMarks.add(word);
          state.markedByCard[state.card] = [...currentMarks];
          persist();
          renderMyCard(true);
        });
      } else {
        item.setAttribute("aria-label", `${word}: ${isMarked ? "kantatuta" : "kantatu gabe"}`);
      }
      item.append(cell);
      grid.append(item);
    });
    wrap.append(heading, grid);
    return wrap;
  };

  const checkCardId = (value) => {
    const id = value.trim().toUpperCase().replace("X", "x");
    if (generatedCodes.includes(id)) return id;
    if (/^\d+$/.test(id)) {
      const number = Number(id);
      return number >= 1 && number <= kartoiak.length ? String(number) : null;
    }
    if (/^E\d+$/.test(id)) {
      const number = Number(id.slice(1));
      return number >= 1 && number <= kartoiErrazak.length ? `E${number}` : null;
    }
    return null;
  };

  document.getElementById("check-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const id = checkCardId(document.getElementById("check-card").value);
    const status = document.getElementById("check-status");
    const wrap = document.getElementById("check-board");
    wrap.replaceChildren();
    if (!id) {
      wrap.hidden = true;
      status.textContent = "Idatzi baliozko kartoi-zenbaki bat edo kode osoa.";
      return;
    }
    const board = boardFor(id);
    const marked = new Set(state.called);
    const result = statusFor(board, marked);
    status.textContent = `${id}: ${result}`;
    wrap.append(makeBoard(board, marked, false, `${id}. kartela`));
    wrap.hidden = false;
    if (result === "BINGO!") celebrate();
  });

  const myCard = document.getElementById("my-card");
  const myCode = document.getElementById("my-code");
  const myBoard = document.getElementById("my-board");
  const myCardStatus = document.getElementById("my-card-status");

  const renderMyCard = (checkForBingo = false) => {
    const board = boardFor(state.card);
    myCard.value = state.card;
    myCode.value = generatedCodes.includes(state.card) ? state.card : "";
    const marked = new Set((state.markedByCard[state.card] || []).filter((word) => board.includes(word)));
    myBoard.replaceChildren(makeBoard(board, marked, true, `${state.card}. kartela`));
    myCardStatus.textContent = statusFor(board, marked);
    if (checkForBingo && myCardStatus.textContent === "BINGO!") celebrate();
  };

  myCard.value = state.card;
  myCard.addEventListener("change", () => {
    state.card = myCard.value;
    persist();
    renderMyCard();
  });
  document.getElementById("my-code-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const id = checkCardId(myCode.value);
    if (!id) {
      myCardStatus.textContent = "Ez dut kode hori aurkitu. Egiaztatu eta saiatu berriro.";
      return;
    }
    state.card = id;
    persist();
    renderMyCard();
  });
  document.getElementById("clear-card").addEventListener("click", () => {
    state.markedByCard[state.card] = [];
    document.getElementById("bingo-success").hidden = true;
    renderMyCard();
    persist();
  });

  const queryCard = checkCardId(new URLSearchParams(window.location.search).get("card") || "");
  if (queryCard) {
    state.card = queryCard;
    activeMode = "card";
    setMode("card");
  }
  renderCalled();
  renderDefinition();
  renderMyCard();
})();
