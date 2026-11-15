import math, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 14.0
OUT = '/home/claude/reel/frames'
os.makedirs(OUT, exist_ok=True)
FD = '/usr/share/fonts/opentype/inter/'
def F(n, s): return ImageFont.truetype(FD + n, s)

CREMA = (251, 248, 230); GRAF = (18, 20, 18); VERDE = (27, 67, 50); LIMA = (198, 255, 0); SALVIA = (143, 158, 139)
LOGO = Image.open('/tmp/claude-tool-results/d9804e02-e2d6-5ca7-b44b-2c12b1f558ed/project-file-4c321d8f-e3d0-4b63-b849-28f8ae4ab617-logo_sobre_negro-3a6aa67a.png').convert('RGBA')

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def ease_io(x): x = clamp(x); return 3 * x * x - 2 * x * x * x

# ---------- background ----------
bg = Image.new('RGB', (W, H))
d = ImageDraw.Draw(bg)
for y in range(H):
    t = y / H
    c = tuple(int(VERDE[i] * (1 - t) + GRAF[i] * t) for i in range(3))
    d.line([(0, y), (W, y)], fill=c)
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([W - 520, -260, W + 260, 520], fill=LIMA + (70,))
glow = glow.filter(ImageFilter.GaussianBlur(160))
bg = Image.alpha_composite(bg.convert('RGBA'), glow)

# ---------- phone ----------
PW, PH, PX, PY = 820, 1780, (W - 820) // 2, 360
phone = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
pd = ImageDraw.Draw(phone)
pd.rounded_rectangle([0, 0, PW - 1, PH - 1], 120, fill=(10, 11, 10, 255), outline=(52, 56, 52, 255), width=6)
scr = Image.new('RGBA', (PW - 44, PH - 44))
sd = ImageDraw.Draw(scr)
for y in range(scr.height):
    t = y / scr.height
    c = (int(14 + 12 * (1 - t)), int(30 + 30 * (1 - t)), int(22 + 16 * (1 - t)), 255)
    sd.line([(0, y), (scr.width, y)], fill=c)
wg = Image.new('RGBA', scr.size, (0, 0, 0, 0))
ImageDraw.Draw(wg).ellipse([-200, 900, 500, 1600], fill=LIMA + (55,))
wg = wg.filter(ImageFilter.GaussianBlur(140))
scr = Image.alpha_composite(scr, wg)
mask = Image.new('L', scr.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, scr.width - 1, scr.height - 1], 98, fill=255)
phone.paste(scr, (22, 22), mask)
pd = ImageDraw.Draw(phone)
pd.rounded_rectangle([PW // 2 - 120, 50, PW // 2 + 120, 118], 34, fill=(0, 0, 0, 255))
def ctext(dr, cx, y, s, f, fill):
    w = dr.textlength(s, font=f); dr.text((cx - w / 2, y), s, font=f, fill=fill)
ctext(pd, PW / 2, 170, 'domingo, 15 de noviembre', F('Inter-Medium.otf', 34), CREMA + (210,))
ctext(pd, PW / 2, 210, '09:41', F('InterDisplay-SemiBold.otf', 190), CREMA + (245,))

# ---------- notification cards ----------
MSGS = ['Hola! ¿Hacen páginas web?',
        'Los vi en Google. ¿Atienden hoy?',
        '¿Me pueden arreglar la compu?',
        'Necesito un sistema de turnos',
        '¿Cuánto sale un sistema a medida?',
        '¿Dan clases de IA?']
CW, CH = 720, 148
def card(msg):
    pad = 30
    im = Image.new('RGBA', (CW + 2 * pad, CH + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + CW, pad + CH + 10], 38, fill=(0, 0, 0, 110))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(14)))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([pad, pad, pad + CW, pad + CH], 38, fill=CREMA + (242,))
    ix, iy = pad + 26, pad + 32
    dr.rounded_rectangle([ix, iy, ix + 84, iy + 84], 22, fill=LIMA + (255,))
    dr.ellipse([ix + 16, iy + 20, ix + 68, iy + 58], fill=GRAF + (255,))
    dr.polygon([(ix + 26, iy + 52), (ix + 20, iy + 68), (ix + 40, iy + 56)], fill=GRAF + (255,))
    tx = ix + 108
    dr.text((tx, pad + 30), 'Nuevo cliente', font=F('Inter-SemiBold.otf', 34), fill=GRAF + (255,))
    fa = F('Inter-Regular.otf', 28)
    dr.text((pad + CW - 30 - dr.textlength('ahora', font=fa), pad + 34), 'ahora', font=fa, fill=(110, 116, 108, 255))
    dr.text((tx, pad + 80), msg, font=F('Inter-Regular.otf', 31), fill=(45, 48, 45, 255))
    return im
CARDS = [card(m) for m in MSGS]
T0, STEP, GAP = 1.0, 0.85, 14
STACK_Y = PY + 470

def pill(text):
    f = F('Inter-SemiBold.otf', 32)
    w = int(ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(text, font=f)) + 70
    im = Image.new('RGBA', (w, 70), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([0, 0, w - 1, 69], 35, fill=LIMA + (255,))
    dr.text((35, 15), text, font=f, fill=GRAF + (255,))
    return im
PILL = pill('+ 9 mensajes nuevos')

def wrap_center(dr, lines, y0, size, lh, colors=None):
    y = y0
    for i, ln in enumerate(lines):
        segs = ln if isinstance(ln, list) else [(ln, CREMA)]
        f = F('InterDisplay-Bold.otf', size)
        tw = sum(dr.textlength(s, font=f) for s, _ in segs)
        x = (W - tw) / 2
        for s, c in segs:
            dr.text((x, y), s, font=f, fill=c); x += dr.textlength(s, font=f)
        y += lh

def paste_alpha(base, im, xy, a):
    if a <= 0: return
    if a < 1:
        im = im.copy(); al = im.split()[3].point(lambda p: int(p * a)); im.putalpha(al)
    base.alpha_composite(im, (int(xy[0]), int(xy[1])))

def scaled(im, s):
    if abs(s - 1) < 1e-3: return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)

n = int(DUR * FPS)
for k in range(n):
    t = k / FPS
    fr = bg.copy()
    # hook text
    dr = ImageDraw.Draw(fr)
    ha = ease_out((t - 0.1) / 0.5)
    if t < 8.2:
        hook = Image.new('RGBA', (W, 300), (0, 0, 0, 0))
        hd = ImageDraw.Draw(hook)
        f = F('InterDisplay-Bold.otf', 62)
        for i, s in enumerate(['Cuando tu negocio', 'aparece en Google…']):
            hd.text(((W - hd.textlength(s, font=f)) / 2, 100 + i * 76), s, font=f, fill=CREMA + (255,))
        paste_alpha(fr, hook, (0, int(30 * (1 - ha))), ha)
    # phone slide-up
    pe = ease_out(t / 0.8)
    py = PY + int((1 - pe) * 900)
    fr.alpha_composite(phone, (PX, py))
    # cards
    for i, c in enumerate(CARDS):
        ti = T0 + i * STEP
        if t < ti: continue
        p = (t - ti) / 0.4
        s = 0.86 + 0.14 * ease_back(p)
        a = ease_out(p)
        cs = scaled(c, s)
        cx = W / 2 - cs.width / 2
        cy = STACK_Y + (py - PY) + i * (CH + GAP) - 30 + (c.height - cs.height) / 2 + (1 - ease_out(p)) * 50
        paste_alpha(fr, cs, (cx, cy), a)
    tp = T0 + len(CARDS) * STEP + 0.2
    if t >= tp:
        p = (t - tp) / 0.4
        ps = scaled(PILL, 0.8 + 0.2 * ease_back(p))
        paste_alpha(fr, ps, (W / 2 - ps.width / 2, STACK_Y + len(CARDS) * (CH + GAP) + 10), ease_out(p))
    # overlay message
    if t >= 7.6:
        a = ease_out((t - 7.6) / 0.5)
        ov = Image.new('RGBA', (W, H), GRAF + (int(240 * a),))
        fr.alpha_composite(ov)
        if t < 10.3:
            ta = ease_out((t - 7.9) / 0.5) * (1 - ease_io((t - 9.9) / 0.4))
            tl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            td = ImageDraw.Draw(tl)
            wrap_center(td, ['Esto pasa cuando', [('tu negocio está ', CREMA), ('online.', LIMA)]], 800, 84, 104)
            paste_alpha(fr, tl, (0, int(40 * (1 - ease_out((t - 7.9) / 0.5)))), ta)
    # end card
    if t >= 10.2:
        a = ease_out((t - 10.2) / 0.5)
        ec = Image.new('RGBA', (W, H), GRAF + (255,))
        ed = ImageDraw.Draw(ec)
        lg = LOGO.resize((640, int(640 * LOGO.height / LOGO.width)))
        ls = ease_back((t - 10.4) / 0.6)
        lgs = scaled(lg, 0.8 + 0.2 * ls)
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        tmp.alpha_composite(lgs, (int(W / 2 - lgs.width / 2), int(620 - lgs.height / 2)))
        la = ease_out((t - 10.4) / 0.5)
        ec = Image.alpha_composite(ec, tmp if la >= 1 else Image.composite(tmp, Image.new('RGBA', (W, H), (0, 0, 0, 0)), tmp.split()[3].point(lambda p: int(p * la))))
        ed = ImageDraw.Draw(ec)
        ta = ease_out((t - 11.0) / 0.5)
        f1 = F('InterDisplay-Bold.otf', 72); f2 = F('Inter-Medium.otf', 40); f3 = F('Inter-SemiBold.otf', 34)
        txt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); xd = ImageDraw.Draw(txt)
        ctext(xd, W / 2, 900, 'Hagamos que te encuentren.', f1, CREMA + (255,))
        ctext(xd, W / 2, 1010, 'Presencia digital · Sistemas a medida', f2, SALVIA + (255,))
        ctext(xd, W / 2, 1066, 'Arreglo de PC · Clases de IA', f2, SALVIA + (255,))
        paste_alpha(ec, txt, (0, int(30 * (1 - ta))), ta)
        ba = ease_out((t - 11.6) / 0.5)
        btn = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(btn)
        bw = 560; bx = (W - bw) // 2; by = 1240
        bd.rounded_rectangle([bx, by, bx + bw, by + 120], 60, fill=LIMA + (255,))
        ctext(bd, W / 2 - 24, by + 34, 'Escribinos por DM', F('InterDisplay-Bold.otf', 46), GRAF + (255,))
        ax = W / 2 + 205 + 6 * math.sin(t * 6)
        bd.line([(ax, by + 38), (ax, by + 84)], fill=GRAF + (255,), width=8)
        bd.polygon([(ax - 18, by + 70), (ax + 18, by + 70), (ax, by + 92)], fill=GRAF + (255,))
        ctext(bd, W / 2, 1460, 'Sistemas a tu medida y a tu alcance.', F('Inter-Medium.otf', 38), CREMA + (230,))
        ctext(bd, W / 2, 1700, '@bc.informatica.pna', f3, LIMA + (255,))
        paste_alpha(ec, btn, (0, int(30 * (1 - ba))), ba)
        paste_alpha(fr, ec, (0, 0), a)
    fr.convert('RGB').save(f'{OUT}/f{k:04d}.png')

subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', f'{OUT}/f%04d.png',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', '/home/claude/reel/reel-notificaciones.mp4'], check=True)
print('ok')
