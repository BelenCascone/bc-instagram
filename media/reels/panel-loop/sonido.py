"""Banda sonora sincronizada para reel-panel-loop.mp4 (15 s, 120 BPM, loop).
Todo sintetizado: sin derechos de terceros. Uso: python3 sonido_panel.py salida.wav"""
import sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile

SR = 48000
DUR = 15.0
TAIL = 2.0                      # se renderiza de más y la cola vuelve al principio (loop sin corte)
N = int((DUR + TAIL) * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)


def hz(n):  # nota MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def env(n, a, d, sus=0.0, rel=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    e = e * (sus + (1 - sus) * np.exp(-np.maximum(t - a, 0) / d))
    if rel:
        e *= np.clip((n / SR - t) / rel, 0, 1)
    return e


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i < 0:
        sig = sig[-i:]; i = 0
    j = min(N, i + len(sig))
    if j <= i:
        return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)


def tone(f, dur, shape='sine', ph=0.0):
    t = np.arange(int(dur * SR)) / SR
    if callable(f):
        phase = 2 * np.pi * np.cumsum(f(t)) / SR
    else:
        phase = 2 * np.pi * f * t
    phase = phase + ph
    if shape == 'sine':
        return np.sin(phase)
    if shape == 'tri':
        return 2 / np.pi * np.arcsin(np.sin(phase))
    if shape == 'saw':
        return 2 * ((phase / (2 * np.pi)) % 1) - 1


# ---------------- instrumentos ----------------
def kick(gain=1.0):
    d = 0.45
    f = lambda t: 45 + 110 * np.exp(-t * 28)
    s = tone(f, d) * env(int(d * SR), 0.002, 0.16)
    click = hp(rng.standard_normal(int(0.004 * SR)), 2000) * 0.25
    s[: len(click)] += click
    return s * gain


def hat(gain=1.0, d=0.05):
    s = hp(rng.standard_normal(int(d * SR)), 7000, 4) * env(int(d * SR), 0.001, d / 4)
    return s * gain


def pluck(n, d=0.5, bright=4000):
    f = hz(n)
    s = (tone(f, d, 'tri') + 0.35 * tone(2 * f, d) + 0.12 * tone(3 * f, d, 'tri'))
    s = lp(s, bright) * env(int(d * SR), 0.003, d / 4)
    return s


def bell(n, d=1.2):
    f = hz(n)
    s = tone(f, d) + 0.5 * tone(f * 2.76, d) * np.exp(-np.arange(int(d * SR)) / SR * 9) + 0.25 * tone(f * 5.4, d) * np.exp(-np.arange(int(d * SR)) / SR * 16)
    return s * env(int(d * SR), 0.002, d / 3.5)


def pad(notes, dur, cutoff=1400, a=0.6, rel=0.8):
    n = int(dur * SR); s = np.zeros(n)
    for k, m in enumerate(notes):
        for det in (-0.08, 0.08):
            s += tone(hz(m + det), dur, 'saw', ph=rng.uniform(0, 6.28))
    s = lp(s / (2 * len(notes)), cutoff, 2)
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.clip((dur - t) / rel, 0, 1)
    return s * e


def noise_sweep(dur, f0, f1, q=0.35):
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        p = i / n; fc = f0 * (f1 / f0) ** p
        lo, hi = max(40, fc * (1 - q)), min(SR / 2 - 100, fc * (1 + q))
        out[i:i + blk] = bp(x[max(0, i - 2048):i + blk], lo, hi)[-len(x[i:i + blk]):]
    return out


def sub_boom(gain=1.0):
    d = 1.2
    s = tone(lambda t: 38 + 40 * np.exp(-t * 6), d) * env(int(d * SR), 0.005, 0.35)
    return s * gain


# ---------------- música (Am · F · G · Am · C) ----------------
BEAT = 0.5
chords = [  # (inicio, fin, notas del pad, raíz del bajo)
    (0.0, 3.0, [57, 60, 64, 67, 71], 45),    # Am9
    (3.0, 6.0, [53, 57, 60, 64, 67], 41),    # Fmaj9
    (6.0, 8.5, [55, 59, 62, 64], 43),        # G6
    (8.5, 10.5, [57, 60, 64, 67], 45),       # Am7
    (10.5, 12.0, [53, 57, 60, 64], 41),      # Fmaj7
    (12.0, 15.0, [48, 55, 59, 62, 64], 36),  # Cmaj9 (cierre luminoso)
    (15.0, 17.0, [57, 60, 64, 67, 71], 45),  # vuelve a Am para el loop
]
for t0, t1, notes, root in chords:
    cut = 900 if t0 < 3 else (1300 if t0 < 12 else 1700)
    if t0 >= 15:
        cut = 900
    add(pad(notes, t1 - t0 + 0.8, cutoff=cut, a=0.35, rel=0.8), t0 - 0.1, gain=0.20)

# bajo en corcheas (de 3.0 a 12.0), con "sidechain" del bombo
for t0, t1, notes, root in chords:
    if t0 < 3.0 or t0 >= 12.0:
        continue
    t = t0
    while t < t1 - 1e-6:
        off = (round(t / 0.25) % 2) == 1
        n = root + (12 if off and (round(t / 0.5) % 4 == 3) else 0)
        d = 0.22
        s = lp(tone(hz(n), d, 'saw') + tone(hz(n - 12), d), 380) * env(int(d * SR), 0.004, 0.09)
        add(s, t + (0.03 if not off else 0.0), gain=0.32 if off else 0.18)
        t += 0.25

# bombo + hats (entra con el gráfico, sigue el latido del punto 8.5-12)
for k in range(int(3.0 / BEAT), int(12.0 / BEAT)):
    t = k * BEAT
    if 6.0 <= t < 6.5:          # hueco para el "golpe" de la expansión
        continue
    add(kick(), t, gain=0.85 if t >= 8.5 else 0.7)
    add(hat(0.18), t + 0.25, pan=0.25)
    if t >= 8.5:
        add(hat(0.08, 0.03), t + 0.125, pan=-0.3); add(hat(0.08, 0.03), t + 0.375, pan=0.3)

# arpegio en semicorcheas mientras giran los anillos
arp = {8.5: [69, 72, 76, 79, 81, 79, 76, 72], 10.5: [65, 69, 72, 76, 77, 76, 72, 69]}
for t0, seq in arp.items():
    span = 2.0 if t0 == 8.5 else 1.5
    for i in range(int(span / 0.125)):
        add(pluck(seq[i % 8], 0.3, 3500), t0 + i * 0.125, gain=0.11, pan=0.35 * np.sin(i * 0.9))

# ---------------- efectos sincronizados con la animación ----------------
# 0.95 clic del mouse
c = hp(rng.standard_normal(int(0.012 * SR)), 2500) * env(int(0.012 * SR), 0.0005, 0.003)
add(c, 0.95, 0.55); add(c * 0.6, 1.06, 0.55)
# 1.0 el switch se apaga (blip que baja)
add(tone(lambda t: 900 - 500 * np.minimum(t / 0.12, 1), 0.16) * env(int(0.16 * SR), 0.002, 0.05), 1.0, 0.22)
# 1.02-1.4 "Tu negocio sin" se cae: tics que bajan
for i in range(14):
    f = 2400 - i * 120
    s = tone(f, 0.05) * env(int(0.05 * SR), 0.001, 0.012)
    add(s, 1.02 + i * 0.018 + 0.12, 0.07, pan=-0.6 + i * 0.09)
# 1.3-2.0 el punto viaja en arco hasta la i: barrido suave hacia arriba
add(noise_sweep(0.7, 600, 3000) * env(int(0.7 * SR), 0.35, 0.2, rel=0.2), 1.3, 0.10)
# 2.0 rebote sobre la i: "boing"
add(tone(lambda t: 520 + 180 * np.exp(-t * 14) * np.cos(t * 40), 0.35) * env(int(0.35 * SR), 0.002, 0.1), 2.0, 0.22)
add(pluck(76, 0.5), 2.0, 0.18)
# 2.5 "sistema" se cae + golpe grave
for i in range(7):
    s = tone(1800 - i * 150, 0.06) * env(int(0.06 * SR), 0.001, 0.015)
    add(s, 2.5 + i * 0.03 + 0.15, 0.07, pan=-0.4 + i * 0.13)
add(sub_boom(0.45), 2.85)
# 3.0-5.5 el gráfico sube: barrido tonal que acompaña la curva
add(tone(lambda t: 220 * 2 ** (np.minimum(t / 2.5, 1) * 1.5), 2.6, 'tri') * env(int(2.6 * SR), 0.6, 9, rel=0.4), 3.0, 0.035)
# 4.5 aparece "+40%": campanita
add(bell(88), 4.5, 0.20); add(bell(84), 4.56, 0.12, pan=0.3)
# 5.5-6.0 el punto dispara al centro: whoosh
add(noise_sweep(0.55, 400, 6000) * env(int(0.55 * SR), 0.45, 0.1, rel=0.08), 5.45, 0.22)
# 6.0-6.5 se expande y llena la pantalla: riser + impacto
add(noise_sweep(0.5, 1500, 9000) * env(int(0.5 * SR), 0.45, 1, rel=0.03), 6.0, 0.16)
add(sub_boom(0.8), 6.45); add(kick(0.9), 6.45)
crash = hp(rng.standard_normal(int(1.6 * SR)), 5000) * env(int(1.6 * SR), 0.002, 0.45)
add(crash, 6.45, 0.07, pan=0.2)
# 6.5 forma / 7.0 se estira / 7.3 "A tu medida"
add(pluck(67, 0.5), 6.5, 0.16); add(pluck(71, 0.5), 7.0, 0.16)
add(bell(83, 1.4), 7.3, 0.18); add(bell(79, 1.4), 7.3, 0.10, pan=-0.3)
# 8.0-8.5 se contrae: whoosh inverso
add(noise_sweep(0.45, 7000, 500) * env(int(0.45 * SR), 0.05, 0.3, rel=0.05), 8.0, 0.16)
# 8.5 los anillos salen con resorte
add(pluck(81, 0.6, 6000), 8.5, 0.16); add(sub_boom(0.4), 8.5)
# 10.0 los anillos salen volando
add(noise_sweep(0.7, 800, 8000) * env(int(0.7 * SR), 0.5, 0.2, rel=0.1), 10.0, 0.15)
# 10.25-11.7 tramado de puntos: brillitos
for i in range(40):
    t = 10.25 + rng.uniform(0, 1.4)
    add(tone(rng.uniform(3000, 7000), 0.04) * env(int(0.04 * SR), 0.001, 0.01), t, 0.035, pan=rng.uniform(-0.8, 0.8))
add(noise_sweep(0.55, 2000, 12000) * env(int(0.55 * SR), 0.5, 1, rel=0.03), 11.2, 0.12)
# 11.72 el plano se cierra
add(noise_sweep(0.3, 6000, 300) * env(int(0.3 * SR), 0.02, 0.15), 11.72, 0.18); add(kick(0.7), 12.0)
# 12.0 logo + 12.15 / 12.25 texto + 12.6 lema
add(bell(84, 2.0), 12.02, 0.20); add(bell(91, 2.0), 12.02, 0.08, pan=0.3)
add(pluck(72, 0.4), 12.15, 0.10, pan=-0.2); add(pluck(76, 0.4), 12.25, 0.10, pan=0.2)
add(pluck(79, 0.6), 12.6, 0.13)
add(pluck(84, 0.6), 12.9, 0.08, pan=0.3)
# 14.2 estallido de partículas + 14.4 el switch vuelve a prenderse + 14.5 mouse
for k in range(14):
    add(tone(2500 + k * 180, 0.05) * env(int(0.05 * SR), 0.001, 0.015), 14.2 + k * 0.012, 0.05, pan=np.cos(k / 14 * 6.28) * 0.7)
add(tone(lambda t: 500 + 500 * np.minimum(t / 0.12, 1), 0.16) * env(int(0.16 * SR), 0.002, 0.05), 14.45, 0.18)

# ---------------- mezcla ----------------
mix = np.stack([L, R])
# reverb: IR de ruido con caída exponencial, estéreo
ir_n = int(1.6 * SR); tt = np.arange(ir_n) / SR
irL = rng.standard_normal(ir_n) * np.exp(-tt * 4.0); irR = rng.standard_normal(ir_n) * np.exp(-tt * 4.0)
irL = lp(irL, 6000); irR = lp(irR, 6000)
wetL = fftconvolve(mix[0], irL)[:N]; wetR = fftconvolve(mix[1], irR)[:N]
wet = np.stack([wetL, wetR]); wet /= np.max(np.abs(wet)) + 1e-9
dry = mix / (np.max(np.abs(mix)) + 1e-9)
out = dry + 0.22 * wet

# loop: la cola (15-17 s) se suma al principio para que no haya corte al repetirse
n15 = int(DUR * SR)
loop = out[:, :n15].copy()
loop[:, : N - n15] += out[:, n15:]
loop = hp(loop, 28)
# limitador suave
loop = np.tanh(loop / (np.max(np.abs(loop)) + 1e-9) * 1.4) / np.tanh(1.4) * 0.89
wavfile.write(sys.argv[1] if len(sys.argv) > 1 else 'panel.wav', SR, (loop.T * 32767).astype(np.int16))
print('ok')
