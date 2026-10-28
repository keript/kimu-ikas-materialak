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

  window.addEventListener("resize", ajustar);
  ajustar();
})();
