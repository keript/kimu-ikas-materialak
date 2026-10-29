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
      if (window.goatcounter && typeof window.goatcounter.count === "function") {
        window.goatcounter.count({ path: "inprimatu" });
      }
      marcos.forEach((marco) => {
        marco.classList.toggle("oculta-impresion", !conSoluciones && marco.classList.contains("oculta-impresion-alumno"));
      });
      window.print();
    });
  });

  const puntos = {
    1: [[50, 50]],
    2: [[28, 28], [72, 72]],
    3: [[28, 28], [50, 50], [72, 72]],
    4: [[28, 28], [72, 28], [28, 72], [72, 72]],
    5: [[28, 28], [72, 28], [50, 50], [28, 72], [72, 72]],
    6: [[28, 25], [72, 25], [28, 50], [72, 50], [28, 75], [72, 75]],
  };
  const svgNs = "http://www.w3.org/2000/svg";

  function actualizarDado(svg, valor) {
    svg.dataset.valor = String(valor);
    svg.setAttribute("aria-label", `${valor} puntu`);
    svg.querySelectorAll("circle").forEach((punto) => punto.remove());
    puntos[valor].forEach(([x, y]) => {
      const punto = document.createElementNS(svgNs, "circle");
      punto.setAttribute("cx", x);
      punto.setAttribute("cy", y);
      punto.setAttribute("r", "9");
      punto.setAttribute("fill", "currentColor");
      svg.append(punto);
    });
  }

  document.querySelectorAll("[data-dado-bota]").forEach((boton) => {
    boton.addEventListener("click", () => {
      boton.closest(".dados").querySelectorAll(".dado-fila").forEach((fila) => {
        const dadoak = [...fila.querySelectorAll(".dado")];
        const eragiketa = fila.querySelector(".op")?.textContent.trim();
        let balioak = dadoak.map(() => Math.floor(Math.random() * 6) + 1);
        if (eragiketa === "−") balioak.sort((a, b) => b - a);
        dadoak.forEach((dadoa, i) => actualizarDado(dadoa, balioak[i]));
        const emaitza = eragiketa === "×"
          ? balioak.reduce((a, b) => a * b, 1)
          : eragiketa === "−"
            ? balioak.slice(1).reduce((a, b) => a - b, balioak[0])
            : balioak.reduce((a, b) => a + b, 0);
        fila.querySelector(".dado-res").textContent = emaitza;
      });
    });
  });

  document.querySelectorAll("[data-dado-esaldia]").forEach((boton) => {
    boton.addEventListener("click", () => {
      const joko = boton.closest(".dado-esaldia");
      const hitzak = [...joko.querySelectorAll(".dado-kategoria")].map((kategoria) => {
        const aurpegiak = [...kategoria.querySelectorAll(".dado-aukerak span")];
        const hitza = aurpegiak[Math.floor(Math.random() * aurpegiak.length)].textContent;
        kategoria.querySelector(".dado-aurpegi").textContent = hitza;
        return hitza;
      });
      joko.querySelector(".dado-emaitza").textContent = `${hitzak.join(" ")}.`;
    });
  });

  document.querySelectorAll("[data-dado-kolorea]").forEach((boton) => {
    boton.addEventListener("click", () => {
      const joko = boton.closest(".dado-koloreak");
      const galderak = [...joko.querySelectorAll(".dado-kolore-galdera")];
      const galdera = galderak[Math.floor(Math.random() * galderak.length)];
      joko.querySelector(".dado-emaitza").textContent =
        `${galdera.querySelector("strong").textContent}: ${galdera.querySelector("span").textContent}`;
    });
  });

  window.addEventListener("resize", ajustar);
  ajustar();
})();
