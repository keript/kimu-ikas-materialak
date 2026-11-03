(() => {
  const bingos = JSON.parse(document.getElementById("sortzaile-data").textContent);
  const gaia = document.getElementById("sortzaile-gaia");
  const kopurua = document.getElementById("sortzaile-kopurua");
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

  const sortuTaula = (kartoiak, tamaina) => {
    const taula = document.createElement("ol");
    taula.className = "bingoa-grid";
    if (tamaina === "3x3") taula.classList.add("bingoa-grid-erraza");
    taula.style.setProperty("--board-size", tamaina[0]);
    kartoiak.forEach((hitza) => {
      const gelaxka = document.createElement("li");
      gelaxka.className = "bingoa-cell";
      gelaxka.textContent = hitza;
      taula.append(gelaxka);
    });
    return taula;
  };

  const sortuKartela = (bingo, kodea, kartoiak, tamaina, inprimatzeko) => {
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
    kartela.append(burua, sortuTaula(kartoiak, tamaina));
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
    const zenbateko = Number(kopurua.value);
    if (!Number.isInteger(zenbateko) || zenbateko < 1 || zenbateko > 40) {
      egoera.textContent = "Aukeratu 1 eta 40 arteko zenbaki oso bat.";
      emaitzak.replaceChildren();
      inprimakia.replaceChildren();
      return;
    }
    const kartoiak = bingo.kartoi_sortzaileak[tamaina];
    const hautatuak = Object.entries(kartoiak).slice(0, zenbateko);
    emaitzak.replaceChildren();
    const inprimatzekoOrrialdeak = [];
    for (let hasiera = 0; hasiera < hautatuak.length; hasiera += 4) {
      const orria = document.createElement("section");
      orria.className = "inprimatzeko-orria";
      hautatuak.slice(hasiera, hasiera + 4).forEach(([kodea, hitzak]) => {
        const kartela = sortuKartela(bingo, kodea, hitzak, tamaina, true);
        orria.append(kartela);
        emaitzak.append(sortuKartela(bingo, kodea, hitzak, tamaina, false));
      });
      inprimatzekoOrrialdeak.push(orria);
    }
    const deitzaileOrria = document.createElement("section");
    deitzaileOrria.className = "deitzaile-orria";
    const deitzaileIzenburua = document.createElement("h2");
    deitzaileIzenburua.textContent = `${bingo.izenburua} · Deitzailea`;
    const deitzaileAzalpena = document.createElement("p");
    deitzaileAzalpena.textContent = "Moztu hitz bakoitza eta atera banan-banan.";
    const hitzZerrenda = document.createElement("ol");
    hitzZerrenda.className = "deitzaile-hitzak";
    const hitzErabilgarriak = tamaina === "3x3"
      ? bingo.hitzak.filter((item) => bingo.erraza.includes(item.hitza))
      : bingo.hitzak;
    hitzErabilgarriak.forEach((item) => {
      const hitzTxartela = document.createElement("li");
      hitzTxartela.textContent = item.hitza;
      hitzZerrenda.append(hitzTxartela);
    });
    deitzaileOrria.append(deitzaileIzenburua, deitzaileAzalpena, hitzZerrenda);
    inprimakia.replaceChildren(...inprimatzekoOrrialdeak, deitzaileOrria);
    egoera.textContent = `${hautatuak.length} kartoi sortu dira.`;
  };

  document.getElementById("sortu-kartoiak").addEventListener("click", sortu);
  document.getElementById("inprimatu-kartoiak").addEventListener("click", () => {
    sortu();
    if (inprimakia.childElementCount) window.print();
  });
  sortu();
})();
