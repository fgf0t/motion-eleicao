# Efeitos sonoros e cama de fundo: sintetizados em código (sem direito autoral, iguais em todo render)
# mais os CC0 do Freesound em assets/sfx-cc0 (créditos lá) e os que a pessoa baixar em assets/sfx-extra.
# uso: python3 scripts/sons.py pasta_destino [estilo duracao]
import os, shutil, sys
import numpy as np
from comum import ASSETS, SR, ff, salvar_wav

R = np.random.default_rng(7)


def t(d): return np.arange(int(d * SR)) / SR
def env(d, ataque=0.005, queda=6.0):
    x = t(d); return np.minimum(1, x / max(ataque, 1e-4)) * np.exp(-x * queda)
def ruido(d): return R.standard_normal(int(d * SR))
def passa_baixa(a, corte):
    k = np.exp(-2 * np.pi * corte / SR); y = np.zeros_like(a); acc = 0.0
    for i, v in enumerate(a): acc = (1 - k) * v + k * acc; y[i] = acc
    return y
def passa_alta(a, corte): return a - passa_baixa(a, corte)
def norm(a, pico=0.9): return a / (np.abs(a).max() + 1e-9) * pico


def sfx():
    s = {}
    d = 1.2; x = t(d)  # whoosh: ruído com filtro varrendo, sobe e desce
    n = ruido(d); bands = [passa_baixa(n, f) for f in (400, 1500, 4000)]
    mix = np.where(x < d * .55, bands[0] + (bands[1] - bands[0]) * (x / (d * .55)), bands[1] + (bands[0] - bands[1]) * ((x - d * .55) / (d * .45)))
    s["whoosh"] = norm(mix * np.sin(np.pi * x / d) ** 2, .7)
    d = .5; x = t(d)  # thump: grave curto
    s["thump"] = norm(np.sin(2 * np.pi * (55 + 90 * np.exp(-x * 30)) * x) * env(d, .002, 9) + passa_baixa(ruido(d), 900) * env(d, .001, 40) * .3)
    d = .45; x = t(d)  # carimbo: estalo + corpo
    s["carimbo"] = norm(passa_baixa(ruido(d), 2500) * env(d, .001, 35) + np.sin(2 * np.pi * 120 * x) * env(d, .002, 14) * .8)
    d = .09  # tecla de máquina
    s["tecla"] = norm(passa_alta(ruido(d), 1800) * env(d, .0005, 70) + np.sin(2 * np.pi * 900 * t(d)) * env(d, .0005, 90) * .4, .6)
    d = .06; s["clique"] = norm(passa_alta(ruido(d), 3000) * env(d, .0003, 120), .5)
    d = .7; x = t(d)  # papel deslizando
    s["papel"] = norm(passa_alta(passa_baixa(ruido(d), 5000), 800) * np.sin(np.pi * x / d) * (1 + .4 * np.sin(2 * np.pi * 23 * x)), .45)
    d = .35; x = t(d)  # pop de recorte
    s["pop"] = norm(np.sin(2 * np.pi * (300 + 500 * np.exp(-x * 25)) * x) * env(d, .001, 18), .55)
    d = .6; x = t(d)  # caneta riscando
    s["caneta"] = norm(passa_alta(ruido(d), 2500) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7 * x))) * np.sin(np.pi * x / d), .35)
    d = .4; s["fita"] = norm(passa_alta(ruido(d), 1200) * (1 + np.sin(2 * np.pi * 40 * t(d))) * env(d, .01, 6), .4)
    d = 1.0; s["estatica"] = norm(passa_alta(ruido(d), 500) * (0.6 + 0.4 * (R.random(int(d * SR)) > .97)) * env(d, .005, 2.5), .6)
    d = 2.5; x = t(d); s["zumbido"] = norm(np.sin(2 * np.pi * 3900 * x) * np.minimum(1, x * 20) * np.exp(-x * 1.1), .25)
    d = 4.0; x = t(d)  # boom: impacto grave com cauda
    s["boom"] = norm(np.sin(2 * np.pi * (38 + 40 * np.exp(-x * 6)) * x) * env(d, .004, 1.6) + passa_baixa(ruido(d), 200) * env(d, .002, 3) * .5)
    d = 2.0; x = t(d); s["riser"] = norm(passa_baixa(ruido(d), 3000) * (x / d) ** 2 + np.sin(2 * np.pi * (200 + 600 * (x / d) ** 2) * x) * (x / d) ** 2 * .3, .5)
    return s


def onda_quadrada(f, d, duty=0.5):
    fase = np.cumsum(np.full(int(d * SR), f) if np.isscalar(f) else f) / SR
    return np.where((fase % 1) < duty, 1.0, -1.0)


def sfx8():
    """efeitos 8-bit no jeito do sfxr: onda quadrada com envelope de altura"""
    s = {}
    d = .35; x = t(d); f = np.where(x < .07, 988, 1319)  # moeda: dois tons subindo
    s["moeda"] = onda_quadrada(f, d) * np.exp(-x * 7) * .5
    d = .3; x = t(d); s["pulo"] = onda_quadrada(220 * (1 + 3 * x / d), d, .25) * np.exp(-x * 6) * .5
    d = .12; s["bip"] = onda_quadrada(880, d) * env(d, .002, 12) * .45
    d = .05; s["blip"] = onda_quadrada(1500, d, .25) * env(d, .001, 40) * .35
    d = .45; x = t(d); s["erro"] = onda_quadrada(np.where(x < .2, 196, 147), d) * np.exp(-x * 3) * .45
    d = .9; x = t(d); s["explosao"] = np.sign(ruido(d)) * np.repeat(R.random(int(d * 60) + 1) > .0, int(SR / 60) + 1)[:int(d * SR)] * np.exp(-x * 4.5) * .5
    s["explosao"] = passa_baixa(s["explosao"], 2500 * 1.0)
    d = .4; x = t(d); s["glitch8"] = onda_quadrada(np.repeat(R.choice([110, 220, 440, 880, 1760], int(d * 30) + 1), int(SR / 30) + 1)[:int(d * SR)], d, .3) * .35
    d = .7; x = t(d); notas = np.select([x < .12, x < .24, x < .36], [523, 659, 784], 1047)
    s["vitoria"] = onda_quadrada(notas, d) * np.where(x < .36, 1, np.exp(-(x - .36) * 5)) * .4
    return {k: norm(v, .6) for k, v in s.items()}


def cama(estilo, dur):
    x = t(dur); out = np.zeros_like(x)
    fade = np.minimum(1, x / 1.5) * np.minimum(1, (dur - x) / 2.0)
    if estilo == "leve":  # pulso leve tipo marimba, pentatônica, 110 bpm
        notas = [261.6, 293.7, 329.6, 392.0, 440.0, 523.3]; passo = 60 / 110 / 2
        seq = np.random.default_rng(3).integers(0, len(notas), 64)
        for k in range(int(dur / passo)):
            if k % 8 in (3, 7): continue
            i0 = int(k * passo * SR); nd = int(.35 * SR); f = notas[seq[k % 64]] / (2 if k % 4 == 0 else 1)
            seg = np.sin(2 * np.pi * f * np.arange(nd) / SR) * np.exp(-np.arange(nd) / SR * 9) * (.8 if k % 4 == 0 else .45)
            out[i0:i0 + nd] += seg[:len(out) - i0]
        out += (np.sin(2 * np.pi * 130.8 * x) + .6 * np.sin(2 * np.pi * 196 * x)) * .08 * (1 + .3 * np.sin(2 * np.pi * .1 * x))
    elif estilo == "pixel":  # chiptune: baixo em quadrada + arpejo, 120 bpm
        passo = 60 / 120 / 2; acordes = [(220, 261.6, 329.6), (174.6, 220, 261.6), (196, 246.9, 293.7), (164.8, 207.7, 246.9)]
        for k in range(int(dur / passo)):
            ac = acordes[(k // 16) % 4]; i0 = int(k * passo * SR); nd = int(passo * SR)
            arp = onda_quadrada(ac[k % 3] * 2, passo, .25) * np.exp(-np.arange(nd) / SR * 8) * .22
            baixo = onda_quadrada(ac[0] / 2, passo, .5) * .16 if k % 2 == 0 else np.zeros(nd)
            seg = (arp + baixo)[:len(out) - i0]; out[i0:i0 + len(seg)] += seg
        out = passa_baixa(out, 5000)
    elif estilo == "vhs":  # drone escuro, chiado de fita e batidas graves espaçadas
        out += (np.sin(2 * np.pi * 43.65 * x) + .7 * np.sin(2 * np.pi * 46.2 * x) + .3 * np.sin(2 * np.pi * 87.3 * x * (1 + .002 * np.sin(2 * np.pi * .2 * x)))) * .35
        out += passa_alta(ruido(dur), 3000) * .05
        for k in np.arange(2.0, dur - 1, 4.3):
            i0 = int(k * SR); nd = int(1.5 * SR); seg = np.sin(2 * np.pi * 50 * np.arange(nd) / SR) * np.exp(-np.arange(nd) / SR * 3)
            out[i0:i0 + nd] += seg[:len(out) - i0] * .6
    else:  # dossiê, pesquise, dados: drone grave + pulso de relógio
        out += (np.sin(2 * np.pi * 55 * x) + .5 * np.sin(2 * np.pi * 82.4 * x)) * .3 * (1 + .25 * np.sin(2 * np.pi * .15 * x))
        out += passa_baixa(ruido(dur), 300) * .06
        bpm = 96 if estilo == "dossie" else 104
        for k in np.arange(0.5, dur - .5, 60 / bpm):
            i0 = int(k * SR); nd = int(.25 * SR); xx = np.arange(nd) / SR
            seg = np.sin(2 * np.pi * (60 + 60 * np.exp(-xx * 30)) * xx) * np.exp(-xx * 14)
            out[i0:i0 + nd] += seg[:len(out) - i0] * .5
    return norm(out * fade, .7)


def gerar(pasta, estilo=None, dur=None):
    os.makedirs(pasta, exist_ok=True)
    for nome, a in {**sfx(), **sfx8()}.items():
        p = os.path.join(pasta, f"{nome}.wav")
        if not os.path.exists(p): salvar_wav(p, a)
    # gravações CC0 e as baixadas pela pessoa substituem as sintetizadas de mesmo nome
    for sub in ("sfx-cc0", "sfx-extra"):
        d = os.path.join(ASSETS, sub)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith(".wav") and not f.startswith("."): shutil.copy(os.path.join(d, f), os.path.join(pasta, f))
    if not os.path.exists(os.path.join(pasta, "papel.wav")) and os.path.exists(os.path.join(pasta, "papel-desliza.wav")):
        shutil.copy(os.path.join(pasta, "papel-desliza.wav"), os.path.join(pasta, "papel.wav"))
    if estilo:  # trilha em -24 LUFS fixo; o VOL_CAMA de cada estilo leva ela pra uns 20 dB abaixo da voz (-16)
        bruta = os.path.join(pasta, "cama-bruta.wav"); salvar_wav(bruta, cama(estilo, dur))
        ff("-i", bruta, "-af", "loudnorm=I=-24:TP=-6:LRA=7", "-ar", str(SR), "-ac", "1", os.path.join(pasta, "cama.wav"))
        os.remove(bruta)


if __name__ == "__main__":
    gerar(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None, float(sys.argv[3]) if len(sys.argv) > 3 else None)
