"""Voz de Kimu para reels (Azure, eu-ES-AinhoaNeural, un poco más aguda y alegre).

Uso (GitHub Actions, workflow «Kimuren ahotsa»): TESTUA="..." IZENA="2026-11-reel-x" python scripts/kimu_ahotsa.py
Cada frase en una línea; entre líneas se deja una pausa corta. Sale en instagram/ahotsa/<IZENA>.mp3
"""
import os
from html import escape
from pathlib import Path
from sortu_audioak import sintetizar

lineas = [l.strip() for l in os.environ["TESTUA"].replace("\\n", "\n").splitlines() if l.strip()]
cuerpo = f'<break time="{os.environ.get("ETENA","200ms")}"/>'.join(escape(l) for l in lineas)
ssml = ('<speak version="1.0" xml:lang="eu-ES" xmlns="http://www.w3.org/2001/10/synthesis">'
        f'<voice name="{os.environ.get("AHOTSA","eu-ES-AinhoaNeural")}"><prosody rate="{os.environ.get("ABIADURA","+0%")}" pitch="{os.environ.get("TONUA","+0%")}">' + cuerpo + '</prosody></voice></speak>')
dest = Path("instagram/ahotsa") / f"{os.environ['IZENA']}.mp3"
dest.parent.mkdir(parents=True, exist_ok=True)
sintetizar(ssml, dest)
print("OK", dest, dest.stat().st_size)
