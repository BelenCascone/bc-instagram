import math, os, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OUT = '/home/claude/reel/frames_n'
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
FD = '/usr/share/fonts/opentype/inter/'
def F(n, s): return ImageFont.truetype(FD + n, s)
CREMA = (251, 248, 230); GRAF = (18, 20, 18); LIMA = (198, 255, 0); SALVIA = (143, 158, 139)
LOGO = Image.open('/tmp/claude-tool-results/d9804e02-e2d6-5ca7-b44b-2c12b1f558ed/project-file-4c321d8f-e3d0-4b63-b849-28f8ae4ab617-logo_sobre_negro-3a6aa67a.png').convert('RGBA')
BLACK = 'InterDisplay-Black.otf'

def clamp(x, a=0, b=1): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eb(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def fit_font(text, maxw, start, name=BLACK):
    s = start
    d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    while s > 20 and d.textlength(text, font=F(name, s)) > maxw: s -= 4
    return F(name, s)

def big_word(text, color, maxw=960, start=300, name=BLACK):
    f = fit_font(text, maxw, start, name)
    d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    bb = d.textbbox((0, 0), text, font=f)
    im = Image.new('RGBA', (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), text, font=f, fill=color)
    return im

def center(fr, im, dx=0, dy=0, s=1.0):
    if s != 1: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    fr.alpha_composite(im, (int(W / 2 - im.width / 2 + dx), int(H / 2 - im.height / 2 + dy)))

# scenes: (start, end, fn)
NOT = big_word('NOTICIA', CREMA, 1500, 420).rotate(90, expand=True)
AG = big_word('AGENTES DE IA', GRAF, 960, 200)
AMED = big_word('A MEDIDA', LIMA)
PARA = big_word('PARA TU', CREMA)
NEG = big_word('NEGOCIO', LIMA)
TASKS = [big_word(s, GRAF, 900, 120, 'InterDisplay-Bold.otf') for s in ['Responde mensajes', 'Agenda turnos', 'Arma presupuestos', 'Ordena tu día']]
YTE = big_word('Y TE ENSEÑAMOS', CREMA, 960, 200)
AUS = big_word('A USARLOS', LIMA)

def scene(t):
    fr = Image.new('RGBA', (W, H), GRAF + (255,))
    if t < 1.0:                       # NOTICIA vertical, slides up
        p = eo(t / 0.35)
        center(fr, NOT, dy=(1 - p) * 700 - t * 60)
    elif t < 2.2:                     # lima + agentes de IA stacked scrolling
        fr = Image.new('RGBA', (W, H), LIMA + (255,))
        lt = t - 1.0
        rowh = AG.height + 30
        off = (lt * 900) % rowh
        y = -rowh + off
        i = 0
        while y < H:
            p = eo((lt - i * 0.04) / 0.25)
            fr.alpha_composite(AG, (int(W / 2 - AG.width / 2 + (1 - p) * (W if i % 2 else -W)), int(y)))
            y += rowh; i += 1
    elif t < 2.9:
        center(fr, AMED, s=0.6 + 0.4 * eb((t - 2.2) / 0.3))
    elif t < 3.5:
        center(fr, PARA, dy=(1 - eo((t - 2.9) / 0.2)) * 200)
    elif t < 4.3:
        center(fr, NEG, s=1.25 - 0.25 * eo((t - 3.5) / 0.25))
    elif t < 6.7:                     # tasks on lima, each 0.6s
        fr = Image.new('RGBA', (W, H), LIMA + (255,))
        lt = t - 4.3; i = min(3, int(lt / 0.6)); p = eo((lt - i * 0.6) / 0.2)
        d = ImageDraw.Draw(fr)
        hf = F('InterDisplay-Bold.otf', 46)
        s = 'Un agente de IA que…'
        d.text(((W - d.textlength(s, font=hf)) / 2, 700), s, font=hf, fill=GRAF)
        center(fr, TASKS[i], dy=(1 - p) * 120 + 40)
        # progress dots
        for j in range(4):
            cx = W / 2 - 75 + j * 50
            d.ellipse([cx - 10, 1180, cx + 10, 1200], fill=GRAF if j <= i else (120, 150, 0))
    elif t < 7.5:
        center(fr, YTE, s=0.85 + 0.15 * eo((t - 6.7) / 0.3))
    elif t < 8.4:
        center(fr, AUS, s=0.6 + 0.4 * eb((t - 7.5) / 0.3))
    else:                             # end card
        lt = t - 8.4
        lg = LOGO.resize((600, int(600 * LOGO.height / LOGO.width)))
        s = 0.8 + 0.2 * eb(lt / 0.5)
        lgs = lg.resize((int(lg.width * s), int(lg.height * s)))
        fr.alpha_composite(lgs, (int(W / 2 - lgs.width / 2), int(640 - lgs.height / 2)))
        d = ImageDraw.Draw(fr)
        a = eo((lt - 0.4) / 0.4)
        f1 = F('InterDisplay-Bold.otf', 64); f2 = F('Inter-Medium.otf', 40)
        def ct(y, s, f, c):
            d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=c + (int(255 * a),))
        ct(900, 'Agentes de IA a medida', f1, CREMA)
        ct(990, 'para tu profesión o emprendimiento', f2, SALVIA)
        b = eo((lt - 0.8) / 0.4)
        bw, by = 560, 1180
        bx = (W - bw) // 2
        d.rounded_rectangle([bx, by + (1 - b) * 40, bx + bw, by + 120 + (1 - b) * 40], 60, fill=LIMA + (int(255 * b),))
        bf = F('InterDisplay-Bold.otf', 46)
        s = 'Escribinos por DM'
        d.text(((W - d.textlength(s, font=bf)) / 2 - 24, by + 34 + (1 - b) * 40), s, font=bf, fill=GRAF + (int(255 * b),))
        ax = W / 2 + 205 + 6 * math.sin(t * 6)
        if b > 0.5:
            d.line([(ax, by + 38), (ax, by + 84)], fill=GRAF, width=8)
            d.polygon([(ax - 18, by + 70), (ax + 18, by + 70), (ax, by + 92)], fill=GRAF)
        ct(1700, '@bc.informatica.pna', F('Inter-SemiBold.otf', 34), LIMA)
    return fr

DUR = 11.5
for k in range(int(DUR * FPS)):
    scene(k / FPS).convert('RGB').save(f'{OUT}/f{k:04d}.png')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', f'{OUT}/f%04d.png',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', '/home/claude/reel/reel-noticia-agentes.mp4'], check=True)
print('ok')
