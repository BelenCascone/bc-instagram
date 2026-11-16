"""Genera make/hoy/<fecha>.json desde calendario/*.json para el escenario de Make.
Solo entran los posts del feed con estado "pendiente" (foto, carrusel o reel).
Make lee cada día el archivo de la fecha de hoy y publica lo que dice."""
import json, glob, os, shutil

OUT = "make/hoy"
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
n = 0
for cal in sorted(glob.glob("calendario/*.json")):
    for it in json.load(open(cal)).get("feed", []):
        if it.get("estado") != "pendiente" or not it.get("fecha"):
            continue
        tipo, media = it["tipo"], it["media"]
        files = [{"media_type": "VIDEO", "video_url": u} if u.endswith(".mp4")
                 else {"media_type": "IMAGE", "image_url": u} for u in media]
        out = {"fecha": it["fecha"], "slug": it["slug"], "tipo": tipo,
               "caption": it["caption"], "image_url": media[0],
               "video_url": media[0] if tipo == "reel" else "", "files": files}
        json.dump(out, open(f"{OUT}/{it['fecha']}.json", "w"), ensure_ascii=False, indent=1)
        n += 1
print(n, "archivos")
