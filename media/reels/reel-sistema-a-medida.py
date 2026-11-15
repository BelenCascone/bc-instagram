import math, os, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 14.0
OUT = '/home/claude/reel/frames_d'
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
FD = '/usr/share/fonts/opentype/inter/'
def F(n, s): return ImageFont.truetype(FD + n, s)
CREMA = (251, 248, 230); CREMA2 = (246, 241, 224); GRAF = (18, 20, 18); VERDE = (27, 67, 50)
LIMA = (198, 255, 0); SALVIA = (143, 158, 139)
LOGO = Image.open('/tmp/claude-tool-results/d9804e02-e2d6-5ca7-b44b-2c12b1f558ed/project-file-4c321d8f-e3d0-4b63-b849-28f8ae4ab617-logo_sobre_negro-3a6aa67a.png').convert('RGBA')

def clamp(x, a=0, b=1): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def eb(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def grad(c1, c2):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3)))
    return im.convert('RGBA')
def glow(base, box, col, a, blur):
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse(box, fill=col + (a,))
    return Image.alpha_composite(base, g.filter(ImageFilter.GaussianBlur(blur)))
BG_LIGHT = glow(grad(CREMA, CREMA2), [-300, -200, 700, 700], LIMA, 120, 200)
BG_DARK = glow(grad(VERDE, GRAF), [500, 1100, 1400, 2100], LIMA, 60, 220)

def chip(text, fill, col, size=40):
    f = F('Inter-SemiBold.otf', size)
    w = int(ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(text, font=f)) + 64
    h = size + 40
    im = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([15, 21, 15 + w, 21 + h], h // 2, fill=(0, 0, 0, 60))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([15, 15, 15 + w, 15 + h], h // 2, fill=fill + (255,))
    d.text((15 + 32, 15 + 18), text, font=f, fill=col + (255,))
    return im

def paste(fr, im, x, y, a=1.0, s=1.0, rot=0):
    if a <= 0: return
    if s != 1: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if a < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda p: int(p * a)))
    fr.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))

def ctext(d, y, s, f, c):
    d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=c)

def word(text, color, size, name='InterDisplay-Black.otf'):
    f = F(name, size); d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    bb = d.textbbox((0, 0), text, font=f)
    im = Image.new('RGBA', (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), text, font=f, fill=color)
    return im

# ---------- dashboard mock ----------
DW, DH = 940, 700
PTS = [0.30, 0.42, 0.38, 0.55, 0.50, 0.66, 0.62, 0.78, 0.74, 0.90]
def dashboard(chart_p=1.0, highlight=0.0, toast=0.0):
    pad = 30
    im = Image.new('RGBA', (DW + 2 * pad, DH + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 14, pad + DW, pad + DH + 14], 36, fill=(0, 0, 0, 90))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    X, Y = pad, pad
    d.rounded_rectangle([X, Y, X + DW, Y + DH], 36, fill=CREMA + (255,))
    # sidebar
    d.rounded_rectangle([X, Y, X + 190, Y + DH], 36, fill=GRAF + (255,))
    d.rectangle([X + 150, Y, X + 190, Y + DH], fill=GRAF + (255,))
    lg = LOGO.resize((120, int(120 * LOGO.height / LOGO.width)))
    im.alpha_composite(lg, (X + 35, Y + 34))
    items = ['Inicio', 'Turnos', 'Clientes', 'Stock', 'Reportes']
    fs = F('Inter-Medium.otf', 24)
    for i, s in enumerate(items):
        yy = Y + 130 + i * 62
        if i == 0: d.rounded_rectangle([X + 18, yy - 10, X + 172, yy + 36], 14, fill=LIMA + (255,))
        d.text((X + 36, yy), s, font=fs, fill=(GRAF if i == 0 else CREMA) + (255,))
    # header
    d.text((X + 225, Y + 34), 'Buen día', font=F('InterDisplay-Bold.otf', 38), fill=GRAF + (255,))
    d.text((X + 225, Y + 82), 'Así viene tu negocio hoy', font=F('Inter-Regular.otf', 22), fill=SALVIA + (255,))
    # stat cards
    stats = [('Turnos hoy', '18'), ('Clientes', '342'), ('Pedidos', '27')]
    cw = 215
    for i, (lab, val) in enumerate(stats):
        cx = X + 225 + i * (cw + 18); cy = Y + 140
        hl = highlight if i == 0 else 0
        fill = tuple(int(CREMA2[j] * (1 - hl) + LIMA[j] * hl) for j in range(3))
        d.rounded_rectangle([cx, cy, cx + cw, cy + 130], 22, fill=fill + (255,), outline=(226, 220, 200, 255), width=2)
        d.text((cx + 22, cy + 20), lab, font=F('Inter-Medium.otf', 22), fill=(90, 98, 88, 255))
        d.text((cx + 22, cy + 56), val, font=F('InterDisplay-Bold.otf', 52), fill=GRAF + (255,))
    # chart card
    gx, gy, gw, gh = X + 225, Y + 300, 440, 360
    d.rounded_rectangle([gx, gy, gx + gw, gy + gh], 22, fill=CREMA2 + (255,), outline=(226, 220, 200, 255), width=2)
    d.text((gx + 22, gy + 20), 'Ventas del mes', font=F('Inter-SemiBold.otf', 24), fill=GRAF + (255,))
    for k in range(4):
        yy = gy + 90 + k * 60; d.line([(gx + 22, yy), (gx + gw - 22, yy)], fill=(226, 220, 200, 255), width=2)
    pts = [(gx + 30 + i * (gw - 60) / (len(PTS) - 1), gy + gh - 40 - v * (gh - 140)) for i, v in enumerate(PTS)]
    nseg = (len(pts) - 1) * chart_p
    draw = [pts[0]]
    for i in range(1, len(pts)):
        if i <= nseg: draw.append(pts[i])
        else:
            f = nseg - (i - 1)
            if f > 0: draw.append((pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f))
            break
    if len(draw) > 1:
        poly = draw + [(draw[-1][0], gy + gh - 30), (draw[0][0], gy + gh - 30)]
        d.polygon(poly, fill=LIMA + (90,))
        d.line(draw, fill=VERDE + (255,), width=6, joint='curve')
        ex, ey = draw[-1]; d.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=VERDE + (255,))
    # donut card
    rx, ry, rw = gx + gw + 18, gy, 215
    d.rounded_rectangle([rx, ry, rx + rw, ry + gh], 22, fill=CREMA2 + (255,), outline=(226, 220, 200, 255), width=2)
    d.text((rx + 22, ry + 20), 'Agenda', font=F('Inter-SemiBold.otf', 24), fill=GRAF + (255,))
    cxx, cyy, r = rx + rw / 2, ry + 190, 70
    d.ellipse([cxx - r, cyy - r, cxx + r, cyy + r], outline=(226, 220, 200, 255), width=22)
    d.arc([cxx - r, cyy - r, cxx + r, cyy + r], -90, -90 + 360 * 0.78 * chart_p, fill=VERDE + (255,), width=22)
    pf = F('InterDisplay-Bold.otf', 34); s = f'{int(78 * chart_p)}%'
    d.text((cxx - d.textlength(s, font=pf) / 2, cyy - 22), s, font=pf, fill=GRAF + (255,))
    d.text((rx + 40, ry + 290), 'ocupada', font=F('Inter-Regular.otf', 22), fill=SALVIA + (255,))
    # toast
    if toast > 0:
        tw, th = 420, 86
        tx, ty = X + DW - tw - 30, Y + DH - th - 30 + (1 - eo(toast)) * 40
        tl = Image.new('RGBA', im.size, (0, 0, 0, 0)); td = ImageDraw.Draw(tl)
        td.rounded_rectangle([tx, ty, tx + tw, ty + th], 22, fill=GRAF + (int(245 * eo(toast)),))
        td.ellipse([tx + 22, ty + 22, tx + 64, ty + 64], fill=LIMA + (int(255 * eo(toast)),))
        td.line([(tx + 33, ty + 44), (tx + 41, ty + 52), (tx + 55, ty + 35)], fill=GRAF + (255,), width=5)
        td.text((tx + 82, ty + 26), 'Turno confirmado', font=F('Inter-SemiBold.otf', 28), fill=CREMA + (int(255 * eo(toast)),))
        im = Image.alpha_composite(im, tl)
    return im

def cursor():
    im = Image.new('RGBA', (60, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(4, 4), (4, 62), (18, 48), (30, 74), (40, 69), (28, 44), (48, 44)]
    d.polygon(pts, fill=GRAF + (255,), outline=CREMA + (255,))
    d.line(pts + [pts[0]], fill=CREMA + (255,), width=3)
    return im
CUR = cursor()

CHIPS = [('Turnos', 180, 520), ('Clientes', 860, 450), ('Stock', 150, 1380), ('Reportes', 880, 1300),
         ('Facturación', 300, 1600), ('Pedidos', 820, 1620)]
CHIP_IM = [chip(s, CREMA, GRAF) for s, _, _ in CHIPS]
CHIP_L = [chip(s, LIMA, GRAF, 46) for s in ['Turnos', 'Clientes', 'Stock', 'Ventas', 'Reportes', 'Lo que necesites']]
LOMEJ = word('¿Lo mejor?', GRAF, 150)
ESTA = word('Está hecho', CREMA, 150)
AMED = word('a tu medida.', LIMA, 150)

def frame(t):
    if t < 4.2:
        fr = BG_LIGHT.copy()
        # floating chips
        for i, (s, x, y) in enumerate(CHIPS):
            a = eo((t - 0.1 - i * 0.08) / 0.4)
            paste(fr, CHIP_IM[i], x + 10 * math.sin(t * 1.3 + i), y + 12 * math.cos(t * 1.1 + i), a * (1 - eo((t - 3.8) / 0.4)))
        if t < 1.5:
            p = eo(t / 0.4)
            paste(fr, LOMEJ, W / 2, 960 + (1 - p) * 80, p * (1 - eo((t - 1.2) / 0.3)))
        else:
            p = eo((t - 1.4) / 0.6)
            dash = dashboard(chart_p=eio((t - 1.8) / 1.6))
            paste(fr, dash, W / 2, 960 + (1 - p) * 600, p * (1 - eo((t - 3.9) / 0.3)), s=0.9 + 0.1 * p, rot=(1 - p) * 6)
    elif t < 7.6:
        fr = BG_DARK.copy()
        lt = t - 4.2
        if lt < 1.4:
            paste(fr, ESTA, W / 2, 860, eo(lt / 0.3), s=0.9 + 0.1 * eo(lt / 0.3))
            paste(fr, AMED, W / 2, 1040, eo((lt - 0.5) / 0.3), s=0.6 + 0.4 * eb((lt - 0.5) / 0.35))
        else:
            d = ImageDraw.Draw(fr)
            a = eo((lt - 1.4) / 0.3)
            f = F('InterDisplay-Bold.otf', 70)
            tl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ctext(ImageDraw.Draw(tl), 330, 'Con lo que tu', f, CREMA + (255,))
            ctext(ImageDraw.Draw(tl), 420, 'negocio necesita:', f, CREMA + (255,))
            paste(fr, tl, W / 2, H / 2, a)
            for i, c in enumerate(CHIP_L):
                ti = 1.6 + i * 0.25
                p = (lt - ti) / 0.35
                if p <= 0: continue
                paste(fr, c, W / 2, 680 + i * 160, eo(p), s=0.7 + 0.3 * eb(p))
    elif t < 10.6:
        fr = BG_LIGHT.copy()
        lt = t - 7.6
        d = ImageDraw.Draw(fr)
        f = F('InterDisplay-Bold.otf', 66)
        a = eo(lt / 0.4)
        tl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ctext(ImageDraw.Draw(tl), 330, 'Simple de usar.', f, GRAF + (255,))
        ctext(ImageDraw.Draw(tl), 412, 'Desde la compu o el celu.', F('Inter-Medium.otf', 44), VERDE + (255,))
        paste(fr, tl, W / 2, H / 2, a)
        hl = eo((lt - 1.3) / 0.2)
        dash = dashboard(1.0, highlight=hl, toast=(lt - 1.5) / 0.4 if lt > 1.5 else 0)
        S = 1.05
        paste(fr, dash, W / 2, 1060, a, s=S)
        # cursor path toward first stat card
        tx = W / 2 - DW * S / 2 + (225 + 30 + 100) * S
        ty = 1060 - (DH + 60) * S / 2 + (140 + 30 + 70) * S
        p = eio((lt - 0.4) / 0.9)
        cx = 980 + (tx - 980) * p; cy = 1700 + (ty - 1700) * p
        click = 0.85 if 1.3 < lt < 1.45 else 1.0
        if lt > 0.3: paste(fr, CUR, cx + 22, cy + 32, 1, s=click)
    else:
        fr = BG_DARK.copy()
        lt = t - 10.6
        lg = LOGO.resize((600, int(600 * LOGO.height / LOGO.width)))
        paste(fr, lg, W / 2, 640, eo(lt / 0.4), s=0.8 + 0.2 * eb(lt / 0.5))
        d = ImageDraw.Draw(fr)
        a = int(255 * eo((lt - 0.4) / 0.4))
        ctext(d, 880, 'Sistemas a tu medida', F('InterDisplay-Bold.otf', 72), CREMA + (a,))
        ctext(d, 970, 'y a tu alcance.', F('InterDisplay-Bold.otf', 72), LIMA + (a,))
        ctext(d, 1090, 'No hace falta ser una gran empresa.', F('Inter-Medium.otf', 38), SALVIA + (a,))
        b = eo((lt - 0.8) / 0.4); by = 1240 + (1 - b) * 40; bw = 560; bx = (W - bw) // 2
        d.rounded_rectangle([bx, by, bx + bw, by + 120], 60, fill=LIMA + (int(255 * b),))
        bf = F('InterDisplay-Bold.otf', 46); s = 'Escribinos por DM'
        d.text(((W - d.textlength(s, font=bf)) / 2 - 24, by + 34), s, font=bf, fill=GRAF + (int(255 * b),))
        if b > 0.5:
            ax = W / 2 + 205 + 6 * math.sin(t * 6)
            d.line([(ax, by + 38), (ax, by + 84)], fill=GRAF, width=8)
            d.polygon([(ax - 18, by + 70), (ax + 18, by + 70), (ax, by + 92)], fill=GRAF)
        ctext(d, 1700, '@bc.informatica.pna', F('Inter-SemiBold.otf', 34), LIMA + (a,))
    return fr

for k in range(int(DUR * FPS)):
    frame(k / FPS).convert('RGB').save(f'{OUT}/f{k:04d}.png')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', f'{OUT}/f%04d.png',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', '/home/claude/reel/reel-sistema-a-medida.mp4'], check=True)
print('ok')
