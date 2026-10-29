# Kimu buletina

Webguneak Buttondown-en harpidetzeko inprimakia erakusten du. Posta-helbideak Buttondown-era bidaltzen dira zuzenean; ez dira biltegiratzen kodean.

1. Sortu Buttondown kontua edo sartu [Kimu-ren kontuan](https://buttondown.com/kimu).
2. Aukeratu newsletterraren erabiltzaile-izena; Kimu-ren artxiboa [buttondown.com/kimu/archive](https://buttondown.com/kimu/archive) helbidean dago.
3. Ezarri `buletina = "kimu"` balioa `scripts/build.py` fitxategian. Buletina ezkutatzeko, utzi `buletina = ""`.
4. Exekutatu `python scripts/build.py` eta egiaztatu formularioa `index.html` eta fitxa-orri batean. Buttondown-en harpidetza-helbide estandarra `https://buttondown.com/api/emails/embed-subscribe/kimu` da.

Formularioak posta elektronikoa eta nahitaezko baimen-laukia eskatzen ditu. Webguneak `pribatutasuna.html` orrian azaltzen du datuen erabilera; ez gehitu API-gakorik edo harpidedunen daturik biltegira.
