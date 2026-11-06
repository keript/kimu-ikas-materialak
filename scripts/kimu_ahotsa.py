"""Voz de Kimu para reels (Azure, eu-ES-AinhoaNeural, un poco más aguda y alegre).

Uso (GitHub Actions, workflow «Kimuren ahotsa»): TESTUA="..." IZENA="2026-11-reel-x" python scripts/kimu_ahotsa.py
Cada frase en una línea; entre líneas se deja una pausa corta. Sale en instagram/ahotsa/<IZENA>.mp3
"""
import os
from html import escape
from pathlib import Path
from sortu_audioak import sintetizar

lineas = [l.strip() for l in os.environ["TESTUA"].replace("\\n", "\n").splitlines() if l.strip()]
if os.environ.get("NATURALA"):
    # Variar ritmo, tono y pausas entre frases: suena menos a robot.
    R = ["-6%", "-2%", "+3%", "-4%", "+1%", "-3%"]; P = ["+2%", "-1%", "+3%", "0%", "-2%", "+1%"]
    B = ["300ms", "220ms", "380ms", "260ms", "330ms", "240ms"]
    cuerpo = "".join(f'<prosody rate="{R[i % 6]}" pitch="{P[i % 6]}">{escape(l)}</prosody>'
                     + (f'<break time="{B[i % 6]}"/>' if i < len(lineas) - 1 else "") for i, l in enumerate(lineas))
else:
    cuerpo = f'<break time="{os.environ.get("ETENA","200ms")}"/>'.join(escape(l) for l in lineas)
ssml = ('<speak version="1.0" xml:lang="eu-ES" xmlns="http://www.w3.org/2001/10/synthesis">'
        f'<voice name="{os.environ.get("AHOTSA","eu-ES-AinhoaNeural")}"><prosody rate="{os.environ.get("ABIADURA","+0%")}" pitch="{os.environ.get("TONUA","+0%")}">' + cuerpo + '</prosody></voice></speak>')
dest = Path("instagram/ahotsa") / f"{os.environ['IZENA']}.mp3"
dest.parent.mkdir(parents=True, exist_ok=True)
sintetizar(ssml, dest)
print("OK", dest, dest.stat().st_size)
