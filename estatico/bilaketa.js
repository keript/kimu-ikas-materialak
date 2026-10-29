(() => {
  const root = document.querySelector("[data-bilaketa]");
  if (!root) return;

  const form = root.querySelector(".bilaketa-form");
  const query = root.querySelector('input[type="search"]');
  const filters = [...root.querySelectorAll("[data-iragazkia]")];
  const results = root.querySelector(".bilaketa-emaitzak");
  const message = root.querySelector("[data-emaitza-mezua]");
  const list = root.querySelector("[data-emaitza-zerrenda]");
  const needs = {
    agnh: "AGNH / arreta",
    dislexia: "Dislexia",
    tea: "TEA",
    "euskara-berria": "Euskara berria",
  };

  const normalize = (value) => String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();

  const showResults = (resources) => {
    const terms = normalize(query.value).split(/\s+/).filter(Boolean);
    const selected = Object.fromEntries(filters.map((filter) => [filter.dataset.iragazkia, filter.value]));
    if (!terms.length && !Object.values(selected).some(Boolean)) {
      results.hidden = true;
      return;
    }
    const found = resources.filter((resource) => {
      const searchable = normalize([
        resource.id,
        resource.titulo,
        resource.area,
        resource.curso,
        resource.tipo,
        ...(resource.beharrak || []),
        ...(resource.palabras_clave || []),
      ].join(" "));
      return terms.every((term) => searchable.includes(term))
        && (!selected.curso || resource.curso === selected.curso)
        && (!selected.area || resource.area === selected.area)
        && (!selected.beharrak || (resource.beharrak || []).includes(selected.beharrak));
    });
    const matches = found.slice(0, 30);

    list.replaceChildren();
    message.textContent = found.length
      ? `${found.length} emaitza${found.length > 30 ? " · lehen 30ak" : ""}`
      : "Ez da emaitzarik aurkitu.";
    for (const resource of matches) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = `${encodeURIComponent(resource.id)}.html`;
      link.textContent = `${resource.titulo} · ${[resource.area, resource.curso].filter(Boolean).join(" · ")}`;
      item.append(link);
      list.append(item);
    }
    results.hidden = false;
  };

  fetch("bilaketa.json")
    .then((response) => {
      if (!response.ok) throw new Error("bilaketa.json");
      return response.json();
    })
    .then((resources) => {
      const options = {
        curso: [...new Set(resources.map((resource) => resource.curso).filter(Boolean))].sort(),
        area: [...new Set(resources.map((resource) => resource.area).filter(Boolean))].sort(),
        beharrak: [...new Set(resources.flatMap((resource) => resource.beharrak || []))].sort(),
      };
      for (const filter of filters) {
        for (const value of options[filter.dataset.iragazkia] || []) {
          const option = document.createElement("option");
          option.value = value;
          option.textContent = filter.dataset.iragazkia === "beharrak" ? (needs[value] || value) : value;
          filter.append(option);
        }
      }
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        showResults(resources);
      });
      query.addEventListener("input", () => showResults(resources));
      filters.forEach((filter) => filter.addEventListener("change", () => showResults(resources)));
    })
    .catch(() => {
      form.addEventListener("submit", (event) => event.preventDefault());
      message.textContent = "Bilaketa ezin izan da kargatu. Saiatu orria berriro kargatzen.";
      results.hidden = false;
    });
})();
