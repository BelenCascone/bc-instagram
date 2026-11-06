#!/bin/bash
# Uso: motor/historia_prep.sh <spec.json> <slug> [nombre]
# Renderiza una historia 1080x1920 a JPEG, la sube a media/<slug>/<nombre>.jpg y muestra la URL pública.
# Publicar después con la API (Zapier "Make API Mutating Request"):
#   POST https://graph.facebook.com/v21.0/17841476355267605/media  ?image_url=<URL>&media_type=STORIES  → id
#   POST https://graph.facebook.com/v21.0/17841476355267605/media_publish ?creation_id=<id>
set -e
SPEC=$1; SLUG=$2; N=${3:-historia}; R=$(cd "$(dirname "$0")/.." && pwd); OUT=$R/media/$SLUG; mkdir -p $OUT
cd $R/motor; [ -d node_modules ] || npm i --silent; [ -f iconos_retro.json ] || python3 iconos_retro.py
node render.js $SPEC /tmp/$N.png >/dev/null
python3 -c "from PIL import Image;Image.open('/tmp/$N.png').convert('RGB').save('$OUT/$N.jpg',quality=92)"
[ -n "$DRY" ] && { ls -la $OUT/$N.jpg; exit 0; }
cd $R && git pull -q --rebase; git add media/$SLUG/$N.jpg && git -c user.name="BC Informática" -c user.email="bc.informatica.pna@gmail.com" commit -qm "Historia $SLUG/$N" && git push -q origin HEAD
echo "https://raw.githubusercontent.com/BelenCascone/bc-instagram/main/media/$SLUG/$N.jpg"
