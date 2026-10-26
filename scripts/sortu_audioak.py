"""Entzumenak: genera los MP3 con Azure Speech (voces neuronales en euskera).

Lee las fichas con un bloque "entzun" (contenido/fitxak/*.json): el texto del audio es el
bloque "lectura" de la misma ficha (título + párrafos), o "testua" dentro del propio bloque.
Solo genera los audios que faltan en estatico/audioak/<audio>.mp3. Para rehacer uno, borra su mp3.

Variables de entorno (secrets de GitHub): AZURE_SPEECH_KEY, AZURE_SPEECH_REGION (p. ej. northeurope).
Uso local:  python scripts/sortu_audioak.py [--zerrenda]   (--zerrenda: solo lista lo que falta)
"""
import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
FITXAK = RAIZ / "contenido" / "fitxak"
SALIDA = RAIZ / "estatico" / "audioak"
AHOTSAK = {"emakumea": "eu-ES-AinhoaNeural", "gizona": "eu-ES-AnderNeural"}


def limpiar(t: str) -> str:
    """Quita el marcado de las fichas (**negrita**, _cursiva_, {X}, :icono:)."""
    t = re.sub(r":[a-z0-9-]{3,}:", "", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", t)
    return re.sub(r"[{}]", "", t).strip()


def audios_pendientes():
    for ruta in sorted(FITXAK.glob("*.json")):
        f = json.loads(ruta.read_text(encoding="utf-8"))
        bloques = [b for h in f.get("hojas", []) for b in h.get("bloques", [])]
        for b in bloques:
            if b.get("tipo") != "entzun":
                continue
            if b.get("testua"):
                partes = b["testua"] if isinstance(b["testua"], list) else [b["testua"]]
            else:
                lect = next((x for x in bloques if x.get("tipo") == "lectura"), None)
                if not lect:
                    print(f"⚠ {ruta.name}: bloque «entzun» sin «testua» ni «lectura»")
                    continue
                partes = [lect["titulo"]] + lect["parrafos"]
            yield b["audio"], [limpiar(p) for p in partes], b.get("ahotsa", "emakumea"), b.get("abiadura", "-10%")


def ssml(partes, voz, abiadura):
    cuerpo = '<break time="900ms"/>'.join(escape(p) for p in partes)
    return (f'<speak version="1.0" xml:lang="eu-ES" xmlns="http://www.w3.org/2001/10/synthesis">'
            f'<voice name="{voz}"><prosody rate="{abiadura}">{cuerpo}</prosody></voice></speak>')


def sintetizar(texto_ssml, destino):
    clave, region = os.environ["AZURE_SPEECH_KEY"], os.environ.get("AZURE_SPEECH_REGION", "northeurope")
    req = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=texto_ssml.encode("utf-8"),
        headers={"Ocp-Apim-Subscription-Key": clave, "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3", "User-Agent": "kimu"})
    with urllib.request.urlopen(req, timeout=120) as r:
        destino.write_bytes(r.read())


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    solo_lista = "--zerrenda" in sys.argv
    hechos = 0
    for audio, partes, ahotsa, abiadura in audios_pendientes():
        destino = SALIDA / f"{audio}.mp3"
        # Huella del texto: si el texto de la ficha cambia, el audio se vuelve a generar solo.
        texto = ssml(partes, AHOTSAK.get(ahotsa, ahotsa), abiadura)
        huella, marca = hashlib.sha1(texto.encode("utf-8")).hexdigest(), SALIDA / f"{audio}.sha1"
        if destino.exists():
            if not marca.exists():
                marca.write_text(huella + "\n")  # audios antiguos: se dan por buenos
            if marca.read_text().strip() == huella:
                continue
        print(f"→ {audio}.mp3 ({AHOTSAK.get(ahotsa, ahotsa)}, {sum(len(p.split()) for p in partes)} hitz)")
        if solo_lista:
            continue
        sintetizar(texto, destino)
        marca.write_text(huella + "\n")
        hechos += 1
    print(f"✓ {hechos} audio berri.")


if __name__ == "__main__":
    main()
