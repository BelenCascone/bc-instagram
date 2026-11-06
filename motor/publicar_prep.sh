#!/bin/bash
# Uso: motor/publicar_prep.sh <carpeta_specs> <slug>   (ej: /home/claude/specs/p1 2026-11-06-tiendas-clonadas)
# Renderiza los JSON (s1..sN) a JPEG, arma el reel si hay frames de reel, sube a media/<slug>/ y muestra las URLs públicas.
set -e
SPECS=$1; SLUG=$2; R=$(cd "$(dirname "$0")/.." && pwd); OUT=$R/media/$SLUG; mkdir -p $OUT
cd $R/motor; [ -d node_modules ] || npm i --silent; [ -f iconos_retro.json ] || python3 iconos_retro.py
for j in $(ls $SPECS/s*.json | sort -V); do b=$(basename $j .json); node render.js $j /tmp/$b.png >/dev/null; python3 -c "from PIL import Image;Image.open('/tmp/$b.png').convert('RGB').save('$OUT/$b.jpg',quality=92)"; done
if [ -f $SPECS/reel.txt ]; then # reel: frames s1..sN → video
  N=$(ls $SPECS/s*.json | wc -l); args=""; f=""; off=0; prev="0"
  for i in $(seq 1 $N); do d=$([ $i = 1 ] && echo 3 || echo 4); args="$args -loop 1 -t $d -i /tmp/s$i.png"; done
  tot=$(python3 -c "print(3+4*($N-1)-0.4*($N-1))")
  fc=""; o=2.6; last="[0]"
  for i in $(seq 1 $((N-1))); do lab="[v$i]"; fc="$fc$last[$i]xfade=transition=slideleft:duration=0.4:offset=$o$lab;"; last=$lab; o=$(python3 -c "print(round($o+3.6,1))"); done
  ffmpeg -y -loglevel error $args -f lavfi -t $tot -i anullsrc=r=44100:cl=stereo -filter_complex "${fc}${last}format=yuv420p[v]" -map "[v]" -map $N:a -c:v libx264 -preset veryfast -crf 20 -r 30 -c:a aac -shortest -movflags +faststart $OUT/reel.mp4
  rm -f $OUT/s*.jpg; cp /tmp/s1.png /tmp/cover.png; python3 -c "from PIL import Image;Image.open('/tmp/cover.png').convert('RGB').save('$OUT/portada.jpg',quality=92)"
fi
[ -n "$DRY" ] && { ls -la $OUT; exit 0; }
cd $R && git pull -q --rebase; git add media/$SLUG && git -c user.name="BC Informática" -c user.email="bc.informatica.pna@gmail.com" commit -qm "Publicación $SLUG" && git push -q origin HEAD
for f in $(ls $OUT | sort -V); do echo "https://raw.githubusercontent.com/BelenCascone/bc-instagram/main/media/$SLUG/$f"; done
