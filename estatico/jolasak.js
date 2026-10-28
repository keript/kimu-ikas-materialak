// Kimu · minijokoak (lotu, sailkatu, memoria, margotu). Pensados para NEAE: tocar y tocar (sin arrastrar),
// botones grandes, sin tiempo, refuerzo inmediato y pista después de dos fallos.
(() => {
  const data = JSON.parse(document.getElementById("joko-datuak").textContent);
  const $ = (id) => document.getElementById(id);
  const contarEvento = (path) => {
    if (window.goatcounter && typeof window.goatcounter.count === "function") {
      window.goatcounter.count({ path });
    }
  };
  const hasiera = $("hasiera"), mini = $("minijokoa"), eremua = $("mini-eremua");
  const egoera = $("mini-egoera"), aurrerapena = $("mini-aurrerapena");
  const izenburua = $("mini-izenburua"), argibidea = $("mini-argibidea"), amaiera = $("mini-amaiera");
  const config = $("galderak-config");
  const ONDO = ["Oso ondo!", "Bikain!", "Hori da!", "Zuzena!"];
  let modua = null, indizea = 0, audio = null;

  function beep(notes) {
    const box = $("soinua");
    if (box && !box.checked) return;
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      let t = audio.currentTime;
      notes.forEach(([freq, len]) => {
        const o = audio.createOscillator(), g = audio.createGain();
        o.type = "sine"; o.frequency.value = freq;
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(0.18, t + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t + len);
        o.connect(g).connect(audio.destination); o.start(t); o.stop(t + len + 0.02);
        t += len * 0.8;
      });
    } catch (e) { /* sin sonido */ }
  }
  const ondo = () => beep([[660, 0.16], [880, 0.28]]);
  const gaizki = () => beep([[260, 0.22]]);
  const amaitu = () => beep([[523, 0.15], [659, 0.15], [784, 0.15], [1047, 0.35]]);
  const pick = (l) => l[Math.floor(Math.random() * l.length)];
  const nahastu = (l) => { const a = [...l]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

  // Contenido de una tarjeta: imagen (si hay) + palabra.
  function edukia(p, handia) {
    const frag = document.createDocumentFragment();
    if (p.img) {
      const im = document.createElement("img");
      im.src = `irudiak/${encodeURIComponent(p.img)}.svg`; im.alt = p.txt || ""; im.className = handia ? "mini-irudi handia" : "mini-irudi";
      frag.append(im);
    }
    if (p.txt) {
      const s = document.createElement("span"); s.textContent = p.txt; frag.append(s);
    }
    return frag;
  }

  function hasi(m) {
    modua = m; indizea = 0;
    if (m === "galderak") { config.hidden = false; config.scrollIntoView({ behavior: "smooth" }); return; }
    hasiera.hidden = true; mini.hidden = false; amaiera.hidden = true;
    marraztu();
  }

  function marraztu() {
    eremua.replaceChildren(); egoera.textContent = ""; amaiera.hidden = true; eremua.hidden = false;
    if (modua === "lotu") lotu(data.lotu[indizea % data.lotu.length]);
    if (modua === "sailkatu") sailkatu(data.sailkatu[indizea % data.sailkatu.length]);
    if (modua === "memoria") memoria(data.memoria);
    if (modua === "margotu") margotu(data.margotu[indizea % data.margotu.length]);
  }

  function bukatu() {
    contarEvento(`jolasa-amaitu/${data.id}/${modua}`);
    amaitu();
    egoera.textContent = "";
    amaiera.hidden = false;
    const hurrengoa = (modua === "lotu" && data.lotu.length > 1) || (modua === "sailkatu" && data.sailkatu.length > 1) || (modua === "margotu" && data.margotu.length > 1);
    $("mini-berriro").textContent = hurrengoa ? "Hurrengoa →" : "Berriro";
    $("mini-berriro").focus();
  }

  // ---------- LOTU: tocar uno de la izquierda y luego su pareja ----------
  function lotu(multzoa) {
    izenburua.textContent = "🔗 Lotu";
    argibidea.textContent = "Ukitu ezkerreko bat. Gero, ukitu bere bikotea.";
    const pares = multzoa.pares.map((p, i) => ({ a: p[0], b: p[1], i }));
    let aukeratua = null, eginak = 0;
    const akatsak = {};
    const ezk = document.createElement("div"), esk = document.createElement("div");
    ezk.className = "lotu-zutabea"; esk.className = "lotu-zutabea";
    const botoia = (p, alde) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "mini-txartela"; b.dataset.i = p.i;
      b.append(edukia(alde === "a" ? p.a : p.b, false));
      return b;
    };
    const eguneratu = () => { aurrerapena.textContent = `${eginak} / ${pares.length}`; };
    pares.forEach((p) => {
      const b = botoia(p, "a");
      b.addEventListener("click", () => {
        if (b.disabled) return;
        ezk.querySelectorAll(".aukeratua").forEach((x) => x.classList.remove("aukeratua"));
        esk.querySelectorAll(".pista").forEach((x) => x.classList.remove("pista"));
        aukeratua = p; b.classList.add("aukeratua");
        egoera.textContent = "Orain, ukitu bere bikotea.";
      });
      ezk.append(b);
    });
    nahastu(pares).forEach((p) => {
      const b = botoia(p, "b");
      b.addEventListener("click", () => {
        if (b.disabled) return;
        if (!aukeratua) { egoera.textContent = "Lehenengo, ukitu ezkerreko bat."; return; }
        if (p.i === aukeratua.i) {
          const a = ezk.querySelector(`[data-i="${p.i}"]`);
          [a, b].forEach((x) => { x.classList.remove("aukeratua", "pista"); x.classList.add("eginda"); x.disabled = true; });
          eginak += 1; aukeratua = null; ondo(); egoera.textContent = pick(ONDO); eguneratu();
          if (eginak === pares.length) bukatu();
        } else {
          gaizki(); b.classList.add("okerra"); setTimeout(() => b.classList.remove("okerra"), 450);
          akatsak[aukeratua.i] = (akatsak[aukeratua.i] || 0) + 1;
          if (akatsak[aukeratua.i] >= 2) {
            esk.querySelector(`[data-i="${aukeratua.i}"]`).classList.add("pista");
            egoera.textContent = "Begiratu: distiratzen ari dena da.";
          } else egoera.textContent = "Ia-ia! Saiatu berriro.";
        }
      });
      esk.append(b);
    });
    const tabla = document.createElement("div"); tabla.className = "lotu-taula"; tabla.append(ezk, esk);
    eremua.append(tabla); eguneratu();
  }

  // ---------- SAILKATU: una palabra cada vez, tocar su grupo ----------
  function sailkatu(multzoa) {
    izenburua.textContent = "🗂️ Sailkatu";
    argibidea.textContent = "Begiratu hitza. Ukitu bere taldea.";
    const items = nahastu(multzoa.items);
    let k = 0, akatsak = 0;
    const erdia = document.createElement("div"); erdia.className = "sailkatu-hitza";
    const taldeak = document.createElement("div"); taldeak.className = "sailkatu-taldeak";
    taldeak.style.setProperty("--zutabeak", Math.min(multzoa.columnas.length, 3));
    const kutxak = multzoa.columnas.map((c, ci) => {
      const kutxa = document.createElement("button");
      kutxa.type = "button"; kutxa.className = "sailkatu-taldea";
      const izena = document.createElement("strong"); izena.textContent = c;
      const barrua = document.createElement("div"); barrua.className = "sailkatu-barrua";
      kutxa.append(izena, barrua);
      kutxa.addEventListener("click", () => erantzun(ci, kutxa, barrua));
      taldeak.append(kutxa);
      return kutxa;
    });
    const erakutsi = () => {
      erdia.replaceChildren(edukia(items[k][0], true));
      aurrerapena.textContent = `${k} / ${items.length}`;
      akatsak = 0; kutxak.forEach((x) => x.classList.remove("pista"));
    };
    function erantzun(ci, kutxa, barrua) {
      if (k >= items.length) return;
      const zuzena = items[k][1];
      if (ci === zuzena) {
        const txip = document.createElement("span"); txip.className = "sailkatu-txip"; txip.append(edukia(items[k][0], false));
        barrua.append(txip); ondo(); egoera.textContent = pick(ONDO);
        k += 1;
        if (k === items.length) { aurrerapena.textContent = `${k} / ${items.length}`; erdia.replaceChildren(); kutxak.forEach((x) => (x.disabled = true)); bukatu(); }
        else erakutsi();
      } else {
        gaizki(); kutxa.classList.add("okerra"); setTimeout(() => kutxa.classList.remove("okerra"), 450);
        akatsak += 1;
        if (akatsak >= 2) { kutxak[zuzena].classList.add("pista"); egoera.textContent = "Begiratu: distiratzen ari dena da."; }
        else egoera.textContent = "Ia-ia! Saiatu berriro.";
      }
    }
    eremua.append(erdia, taldeak); erakutsi();
  }

  // ---------- MARGOTU: tocar una casilla, resolver la operación y elegir el color del resultado ----------
  function margotu(marrazkia) {
    izenburua.textContent = "🖍️ Margotu zenbakien arabera";
    argibidea.textContent = marrazkia.enunciado || "Egin eragiketa eta margotu laukia emaitzaren kolorearekin";
    const koloreak = [...marrazkia.leyenda].sort((a, b) => a.n - b.n);
    const kolorea = (n) => koloreak.find((k) => k.n === n);
    const ilun = (hex) => { const v = parseInt(hex.slice(1), 16); return ((v >> 16) * 299 + ((v >> 8) & 255) * 587 + (v & 255) * 114) / 1000 < 150; };
    let guztira = 0, eginak = 0, aukeratua = null, akatsak = 0;
    const sareta = document.createElement("div"); sareta.className = "margotu-sareta";
    sareta.style.setProperty("--zutabeak", marrazkia.filas[0].length);
    const panela = document.createElement("div"); panela.className = "margotu-panela";
    const eragiketa = document.createElement("p"); eragiketa.className = "margotu-eragiketa";
    eragiketa.textContent = "Ukitu lauki bat";
    const botoiak = document.createElement("div"); botoiak.className = "margotu-botoiak";
    const eguneratu = () => { aurrerapena.textContent = `${eginak} / ${guztira}`; };
    const hautatu = (b, c) => {
      sareta.querySelectorAll(".aukeratua").forEach((x) => x.classList.remove("aukeratua"));
      botoiak.querySelectorAll(".pista").forEach((x) => x.classList.remove("pista"));
      aukeratua = { b, c }; akatsak = 0;
      b.classList.add("aukeratua");
      eragiketa.textContent = `${c.op} = ?`;
      botoiak.querySelectorAll("button").forEach((x) => (x.disabled = false));
      egoera.textContent = "Egin eragiketa eta ukitu emaitzaren kolorea.";
    };
    marrazkia.filas.forEach((fila) => fila.forEach((c) => {
      if (!c) { const hutsa = document.createElement("span"); hutsa.className = "margotu-hutsa"; sareta.append(hutsa); return; }
      guztira += 1;
      const b = document.createElement("button");
      b.type = "button"; b.className = "margotu-laukia"; b.textContent = c.op;
      if (c.op.length > 4) b.classList.add("luzea");
      b.setAttribute("aria-label", `${c.op}`);
      b.addEventListener("click", () => { if (!b.disabled) hautatu(b, c); });
      sareta.append(b);
    }));
    koloreak.forEach((k) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "margotu-kolorea"; b.dataset.n = k.n;
      const lagina = document.createElement("span"); lagina.className = "margotu-lagina"; lagina.textContent = k.marka;
      lagina.style.setProperty("--mc", k.color);
      const zenb = document.createElement("strong"); zenb.textContent = k.n;
      const izena = document.createElement("span"); izena.textContent = k.nombre;
      b.append(zenb, lagina, izena);
      b.addEventListener("click", () => {
        if (!aukeratua) { egoera.textContent = "Lehenengo, ukitu lauki bat."; return; }
        if (aukeratua.c.n === k.n) {
          const l = kolorea(k.n), lauki = aukeratua.b;
          lauki.disabled = true; lauki.classList.remove("aukeratua"); lauki.classList.add("margotuta");
          lauki.style.setProperty("--mc", l.color); lauki.classList.toggle("ilun", ilun(l.color));
          lauki.textContent = l.marka; lauki.setAttribute("aria-label", `${aukeratua.c.op} = ${k.n}: ${l.nombre}`);
          botoiak.querySelectorAll(".pista").forEach((x) => x.classList.remove("pista"));
          aukeratua = null; eginak += 1; ondo(); egoera.textContent = pick(ONDO); eguneratu();
          eragiketa.textContent = "Ukitu lauki bat";
          if (eginak === guztira) { sareta.classList.add("osatua"); botoiak.querySelectorAll("button").forEach((x) => (x.disabled = true)); bukatu(); }
        } else {
          gaizki(); b.classList.add("okerra"); setTimeout(() => b.classList.remove("okerra"), 450);
          akatsak += 1;
          if (akatsak >= 2) {
            botoiak.querySelector(`[data-n="${aukeratua.c.n}"]`).classList.add("pista");
            egoera.textContent = "Begiratu: distiratzen ari dena da.";
          } else egoera.textContent = "Ia-ia! Egin eragiketa berriro.";
        }
      });
      botoiak.append(b);
    });
    panela.append(eragiketa, botoiak);
    eremua.append(sareta, panela); eguneratu();
  }

  // ---------- MEMORIA: imagen ↔ palabra, con vista previa al empezar ----------
  function memoria(bikoteak) {
    izenburua.textContent = "🃏 Memoria";
    argibidea.textContent = "Begiratu ondo 4 segundoz. Gero, aurkitu irudia eta bere hitza.";
    const zenbat = Math.min(bikoteak.length, 6);
    const aukera = nahastu(bikoteak).slice(0, zenbat);
    const txartelak = nahastu(aukera.flatMap(([img, hitza], i) => [{ i, p: { img } }, { i, p: { txt: hitza } }]));
    const sareta = document.createElement("div"); sareta.className = "memoria-sareta";
    let irekiak = [], eginak = 0, blokeatuta = true;
    const eguneratu = () => { aurrerapena.textContent = `${eginak} / ${zenbat}`; };
    const botoiak = txartelak.map((t) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "memoria-txartela agerian";
      const aurrea = document.createElement("span"); aurrea.className = "memoria-aurrea"; aurrea.append(edukia(t.p, false));
      const atzea = document.createElement("span"); atzea.className = "memoria-atzea"; atzea.textContent = "?";
      b.append(aurrea, atzea);
      b.addEventListener("click", () => {
        if (blokeatuta || b.classList.contains("agerian")) return;
        b.classList.add("agerian"); irekiak.push([b, t]);
        if (irekiak.length < 2) return;
        const [[b1, t1], [b2, t2]] = irekiak; irekiak = [];
        if (t1.i === t2.i) {
          [b1, b2].forEach((x) => { x.classList.add("eginda"); x.disabled = true; });
          eginak += 1; ondo(); egoera.textContent = pick(ONDO); eguneratu();
          if (eginak === zenbat) bukatu();
        } else {
          gaizki(); blokeatuta = true; egoera.textContent = "Ez dira bikotea. Gogoratu non dauden!";
          setTimeout(() => { b1.classList.remove("agerian"); b2.classList.remove("agerian"); blokeatuta = false; }, 1300);
        }
      });
      sareta.append(b);
      return b;
    });
    eremua.append(sareta); eguneratu();
    egoera.textContent = "Begiratu ondo…";
    setTimeout(() => { botoiak.forEach((b) => b.classList.remove("agerian")); blokeatuta = false; egoera.textContent = "Orain zuk! Ukitu bi txartel."; }, 4000);
  }

  document.querySelectorAll(".modo-card").forEach((b) => b.addEventListener("click", () => hasi(b.dataset.modo)));
  $("mini-atzera").addEventListener("click", () => { mini.hidden = true; hasiera.hidden = false; });
  $("mini-beste").addEventListener("click", () => { mini.hidden = true; hasiera.hidden = false; });
  $("mini-berriro").addEventListener("click", () => {
    if (modua !== "memoria") indizea += 1;
    marraztu();
  });
})();
