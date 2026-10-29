"""Comprueba el diseño móvil de las páginas generadas con Playwright."""
import argparse
import sys
from urllib.parse import quote

from playwright.sync_api import sync_playwright


JS_REVISION = """() => {
  const oculto = (e) => {
    const estilo = getComputedStyle(e);
    const caja = e.getBoundingClientRect();
    return estilo.display === "none" || estilo.visibility === "hidden" ||
      estilo.clipPath !== "none" || estilo.clip !== "auto" ||
      caja.width === 0 || caja.height === 0;
  };
  const interactivos = [...document.querySelectorAll(
    'button, input[type="button"], input[type="submit"], input[type="reset"], select, summary'
  )].filter((e) => !oculto(e)).map((e) => {
    const caja = e.getBoundingClientRect();
    return {texto: (e.innerText || e.getAttribute("aria-label") || e.value || e.tagName).trim(),
      ancho: Math.round(caja.width), alto: Math.round(caja.height)};
  }).filter((e) => e.ancho < 44 || e.alto < 44);
  const textoCortado = [...document.querySelectorAll("body *")].filter((e) => {
    if (!e.textContent.trim() || oculto(e)) return false;
    const estilo = getComputedStyle(e);
    const recortado = ["hidden", "clip"].includes(estilo.overflowX) ||
      ["hidden", "clip"].includes(estilo.overflowY) || estilo.textOverflow === "ellipsis";
    return recortado && (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1);
  }).map((e) => `${e.tagName.toLowerCase()}.${String(e.className || "").replaceAll(" ", ".")}`);
  return {
    ancho: document.documentElement.scrollWidth,
    viewport: window.innerWidth,
    interactivos,
    textoCortado: [...new Set(textoCortado)].slice(0, 10)
  };
}"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="URL base del servidor local")
    parser.add_argument("--pages", nargs="+", required=True, help="Páginas HTML relativas al sitio")
    parser.add_argument("--width", type=int, default=390)
    args = parser.parse_args()

    problemas = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(viewport={"width": args.width, "height": 844})
        for ruta in args.pages:
            url = f"{args.base_url.rstrip('/')}/{quote(ruta)}"
            try:
                pagina.goto(url, wait_until="networkidle", timeout=30000)
                resultado = pagina.evaluate(JS_REVISION)
            except Exception as e:  # noqa: BLE001
                problemas.append(f"{ruta}: no se pudo comprobar ({str(e)[:160]})")
                continue
            if resultado["ancho"] > resultado["viewport"]:
                problemas.append(
                    f"{ruta}: scroll horizontal ({resultado['ancho']} px en viewport de {resultado['viewport']} px)"
                )
            for boton in resultado["interactivos"]:
                problemas.append(
                    f"{ruta}: control táctil menor de 44×44 px ({boton['texto']}: "
                    f"{boton['ancho']}×{boton['alto']} px)"
                )
            for elemento in resultado["textoCortado"]:
                problemas.append(f"{ruta}: texto cortado en {elemento}")
            print(f"{ruta}: {resultado['viewport']} px · sin desbordamiento ni texto cortado")
        navegador.close()

    if problemas:
        print("\n".join(problemas))
        print(f"\n✗ {len(problemas)} problema(s) en móvil.")
        sys.exit(1)
    print(f"✓ Revisadas {len(args.pages)} páginas a {args.width} px.")


if __name__ == "__main__":
    main()
