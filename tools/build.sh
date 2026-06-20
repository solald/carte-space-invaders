#!/bin/bash
# Régénère toutes les cartes de villes depuis world_invaders.json.
# Usage : bash tools/build.sh   (depuis la racine du repo)
set -e
cd "$(dirname "$0")/.."   # racine du repo

# Régénère aussi le logo (favicon + image de partage)
python3 tools/make_logo.py >/dev/null
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ -x "$CHROME" ]; then
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --window-size=1200,630 --screenshot="$PWD/og-image.png" "file://$PWD/og_card.html" 2>/dev/null
fi
rm -f og_card.html

# city_code | titre | région | fichier de sortie | centre lat,lng
python3 tools/build_city.py MARS "Marseille" "PACA"          carte-space-invaders-marseille.html 43.2895,5.378
python3 tools/build_city.py PA   "Paris"     "Île-de-France" carte-space-invaders-paris.html     48.8566,2.3522
python3 tools/build_city.py LDN  "Londres"   "Royaume-Uni"   carte-space-invaders-londres.html   51.5074,-0.1278

echo "OK — cartes régénérées."
