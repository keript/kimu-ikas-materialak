(() => {
  const bingos = JSON.parse(document.getElementById("sortzaile-data").textContent);
  const gaia = document.getElementById("sortzaile-gaia");
  const kopurua = document.getElementById("sortzaile-kopurua");
  const argazkiAukerak = document.getElementById("sortzaile-argazki-aukerak");
  const argazkiekin = document.getElementById("sortzaile-argazkiekin");
  const argazkiAukera = document.getElementById("sortzaile-argazki-aukera");
  const kartoianAukerak = document.getElementById("sortzaile-kartoian-aukerak");
  const emaitzak = document.getElementById("sortzaile-emaitzak");
  const inprimakia = document.getElementById("sortzaile-inprimakia");
  const egoera = document.getElementById("sortzaile-egoera");

  bingos.forEach((bingo) => {
    const aukera = document.createElement("option");
    aukera.value = bingo.id;
    aukera.textContent = bingo.izenburua;
    gaia.append(aukera);
  });

  const aukeratutakoBingoa = () => bingos.find((bingo) => bingo.id === gaia.value);
  const aukeratutakoTamaina = () => document.querySelector('input[name="tamaina"]:checked').value;
  const argazkiakDaude = (bingo) => bingo.hitzak.some((item) => item.irudia);
  const aukeratutakoArgazkiModua = () => document.querySelector('input[name="argazki-modua"]:checked')?.value || "A";
  const kartoiModua = (kodea) => kodea.match(/-(A|B|H)-\d{4}$/)?.[1] || "A";

  const eguneratuArgazkiAukerak = () => {
    const bingo = aukeratutakoBingoa();
    const erabilgarri = bingo && argazkiakDaude(bingo);
    const argazkiBingoa = erabilgarri && bingo.mota === "argazkia";
    argazkiAukerak.hidden = !erabilgarri || argazkiBingoa;
    kartoianAukerak.hidden = !argazkiBingoa;
    argazkiekin.checked = Boolean(erabilgarri);
    argazkiAukera.textContent = "Argazkiekin";
  };

  const sortuTaula = (bingo, kartoiak, tamaina, argazkiakErabili, modua = "A") => {
    const taula = document.createElement("ol");
    taula.className = "bingoa-grid";
    if (tamaina === "3x3") taula.classList.add("bingoa-grid-erraza");
    taula.style.setProperty("--board-size", tamaina[0]);
    kartoiak.forEach((hitza) => {
      const gelaxka = document.createElement("li");
      gelaxka.className = "bingoa-cell";
      const item = bingo.hitzak.find((sarrera) => sarrera.hitza === hitza);
      if (argazkiakErabili && item?.irudia) {
        gelaxka.classList.add(modua === "B" ? "bingoa-cell-photo-only" : "bingoa-cell-with-photo");
        const irudia = document.createElement("img");
        irudia.className = "bingoa-cell-photo";
        irudia.src = `irudiak-errealak/${encodeURIComponent(item.irudia)}.jpg`;
        irudia.alt = modua === "B" ? hitza : "";
        irudia.addEventListener("error", () => {
          irudia.remove();
          gelaxka.classList.remove("bingoa-cell-with-photo", "bingoa-cell-photo-only");
          gelaxka.textContent = hitza;
        }, { once: true });
        if (modua === "B") {
          gelaxka.append(irudia);
        } else {
          const etiketa = document.createElement("span");
          etiketa.className = "bingoa-cell-label";
          etiketa.textContent = hitza;
          gelaxka.append(irudia, etiketa);
        }
      } else {
        if (modua === "H") gelaxka.classList.add("bingoa-cell-word-only");
        gelaxka.textContent = hitza;
      }
      taula.append(gelaxka);
    });
    return taula;
  };

  const sortuKartela = (bingo, kodea, kartoiak, tamaina, inprimatzeko, argazkiakErabili) => {
    const kartela = document.createElement("article");
    kartela.className = `sortzaile-kartela${inprimatzeko ? " inprimatzeko-kartela" : ""}`;
    const burua = document.createElement("header");
    if (inprimatzeko) {
      const logoa = document.createElement("img");
      logoa.src = "logoak/kimu-logo-zuribeltza.svg";
      logoa.width = 110;
      logoa.height = 34;
      logoa.alt = "Kimu";
      burua.append(logoa);
    }
    const izenburua = document.createElement("h2");
    izenburua.textContent = bingo.izenburua;
    const kode = document.createElement("p");
    kode.className = "sortzaile-kodea";
    kode.textContent = kodea;
    burua.append(izenburua, kode);
    kartela.append(burua, sortuTaula(bingo, kartoiak, tamaina, argazkiakErabili, kartoiModua(kodea)));
    if (inprimatzeko) {
      const oina = document.createElement("p");
      oina.className = "sortzaile-copyright";
      oina.textContent = "© Kimu";
      kartela.append(oina);
    } else {
      const ireki = document.createElement("a");
      ireki.className = "sortzaile-ireki";
      ireki.href = `${encodeURIComponent(bingo.id)}.html?card=${encodeURIComponent(kodea)}`;
      ireki.textContent = "Ireki nire kartoa";
      kartela.append(ireki);
    }
    return kartela;
  };

  const sortu = () => {
    const bingo = aukeratutakoBingoa();
    const tamaina = aukeratutakoTamaina();
    const argazkiModua = bingo.mota === "argazkia" ? aukeratutakoArgazkiModua() : "";
    const argazkiakErabili = bingo.mota === "argazkia"
      ? argazkiModua !== "H" && argazkiakDaude(bingo)
      : argazkiekin.checked && argazkiakDaude(bingo);
    const zenbateko = Number(kopurua.value);
    if (!Number.isInteger(zenbateko) || zenbateko < 1 || zenbateko > 40) {
      egoera.textContent = "Aukeratu 1 eta 40 arteko zenbaki oso bat.";
      emaitzak.replaceChildren();
      inprimakia.replaceChildren();
      return;
    }
    const kartoiak = bingo.kartoi_sortzaileak[tamaina];
    const hautatuak = Object.entries(kartoiak)
      .filter(([kodea]) => !argazkiModua || kartoiModua(kodea) === argazkiModua)
      .slice(0, zenbateko);
    emaitzak.replaceChildren();
    const inprimatzekoOrrialdeak = [];
    const argazkiakKartoiak = argazkiakErabili && argazkiModua !== "H";
    const kartoiKopuruaOrriko = argazkiakKartoiak && tamaina === "4x4" ? 2 : 4;
    for (let hasiera = 0; hasiera < hautatuak.length; hasiera += kartoiKopuruaOrriko) {
      const orria = document.createElement("section");
      orria.className = "inprimatzeko-orria";
      if (argazkiakKartoiak && tamaina === "4x4") orria.classList.add("inprimatzeko-orria-4x4-argazkiduna");
      hautatuak.slice(hasiera, hasiera + kartoiKopuruaOrriko).forEach(([kodea, hitzak]) => {
        const kartela = sortuKartela(bingo, kodea, hitzak, tamaina, true, argazkiakErabili);
        orria.append(kartela);
        emaitzak.append(sortuKartela(bingo, kodea, hitzak, tamaina, false, argazkiakErabili));
      });
      inprimatzekoOrrialdeak.push(orria);
    }
    const deitzaileOrria = document.createElement("section");
    const deitzaileArgazkiak = bingo.mota === "argazkia"
      ? argazkiModua !== "B"
      : argazkiakErabili;
    deitzaileOrria.className = `deitzaile-orria${deitzaileArgazkiak ? " deitzaile-orria-argazkiduna" : ""}`;
    const deitzaileIzenburua = document.createElement("h2");
    deitzaileIzenburua.textContent = `${bingo.izenburua} · Deitzailea`;
    const deitzaileAzalpena = document.createElement("p");
    deitzaileAzalpena.textContent = bingo.mota === "eragiketa"
      ? "Moztu eragiketa bakoitza eta atera banan-banan."
      : bingo.mota === "argazkia"
        ? argazkiModua === "B" ? "Moztu hitz bakoitza eta atera banan-banan."
          : argazkiModua === "H" ? "Moztu argazki bakoitza eta atera banan-banan."
            : "Moztu argazki bakoitza eta hitza irakurri."
        : argazkiakErabili ? "Moztu argazki bakoitza eta atera banan-banan." : "Moztu hitz bakoitza eta atera banan-banan.";
    const hitzZerrenda = document.createElement("ol");
    hitzZerrenda.className = "deitzaile-hitzak";
    const hitzErabilgarriak = tamaina === "3x3"
      ? bingo.hitzak.filter((item) => bingo.erraza.includes(item.hitza))
      : bingo.hitzak;
    hitzErabilgarriak.forEach((item) => {
      const hitzTxartela = document.createElement("li");
      const erakutsiArgazkia = bingo.mota === "argazkia"
        ? (argazkiModua === "A" || argazkiModua === "H") && item.irudia
        : argazkiakErabili && item.irudia;
      if (erakutsiArgazkia) {
        hitzTxartela.className = "deitzaile-hitz-txartela";
        const irudia = document.createElement("img");
        irudia.className = "deitzaile-hitz-argazkia";
        irudia.src = `irudiak-errealak/${encodeURIComponent(item.irudia)}.jpg`;
        irudia.alt = argazkiModua === "H" ? item.hitza : "";
        irudia.addEventListener("error", () => {
          if (argazkiModua === "H") hitzTxartela.textContent = item.hitza;
          else irudia.remove();
        }, { once: true });
        hitzTxartela.append(irudia);
        if (argazkiModua === "A" || bingo.mota !== "argazkia") {
          const hitza = document.createElement("span");
          hitza.textContent = item.hitza;
          hitzTxartela.append(hitza);
        }
      } else {
        hitzTxartela.textContent = bingo.mota === "eragiketa" ? item.definizioa : item.hitza;
      }
      hitzZerrenda.append(hitzTxartela);
    });
    deitzaileOrria.append(deitzaileIzenburua, deitzaileAzalpena, hitzZerrenda);
    inprimakia.replaceChildren(...inprimatzekoOrrialdeak, deitzaileOrria);
    egoera.textContent = `${hautatuak.length} kartoi sortu dira.`;
  };

  document.getElementById("sortu-kartoiak").addEventListener("click", sortu);
  gaia.addEventListener("change", () => {
    eguneratuArgazkiAukerak();
    sortu();
  });
  document.querySelectorAll('input[name="argazki-modua"]').forEach((input) => {
    input.addEventListener("change", sortu);
  });
  argazkiekin.addEventListener("change", () => {
    argazkiAukera.textContent = argazkiekin.checked ? "Argazkiekin" : "Argazkirik gabe";
    sortu();
  });
  document.getElementById("inprimatu-kartoiak").addEventListener("click", () => {
    sortu();
    if (inprimakia.childElementCount) window.print();
  });
  eguneratuArgazkiAukerak();
  sortu();
})();
