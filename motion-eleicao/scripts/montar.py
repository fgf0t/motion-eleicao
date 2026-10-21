# Monta o projeto HyperFrames a partir do roteiro, das falas (voz/) e das fotos (fotos/).
# O tempo de cada palavra sai da própria fala (pausas detectadas no áudio), sem transcrição.
# Cada estilo (estilos/<nome>/estilo.py ou estilos/<nome>/config.json) só desenha as cenas; o resto é igual pra todos.
# uso: python3 scripts/montar.py roteiro.json
import importlib, importlib.util, json, os, re, shutil, sys
import numpy as np
from PIL import Image
from comum import SKILL, ASSETS, HYPERFRAMES, ff, ler_roteiro, ler_wav, duracao_wav, passo, aviso, sem_acento
import reticula, sons

INTRO = 0.55
PONTUA = ",.;:?!…"


# ---------- fala: onde começa, onde termina, onde respira ----------
def analisar(wav, margem=0.0):
    a, sr = ler_wav(wav)
    fr = int(0.02 * sr); n = len(a) // fr
    rms = np.sqrt((a[:n * fr].reshape(n, fr) ** 2).mean(axis=1))
    lim = rms.max() * 0.08
    on = np.nonzero(rms > lim)[0]
    # folga: 0,05 s antes da primeira palavra e 0,25 s depois da última (mais a margem extra da conferência)
    # (o fim pode passar do arquivo: a extração completa com silêncio)
    s0 = max(0.0, on[0] * 0.02 - 0.05 - margem); s1 = (on[-1] + 1) * 0.02 + 0.30 + margem
    pausas, ini = [], None
    for k in range(on[0], on[-1] + 1):
        if rms[k] <= lim * 1.3:
            if ini is None: ini = k
        elif ini is not None:
            if (k - ini) * 0.02 >= 0.12: pausas.append((ini * 0.02, k * 0.02))
            ini = None
    return s0, s1, pausas


def peso(w):
    """tamanho falado aproximado: número e símbolo falam mais do que escrevem ("5,1%" = "cinco vírgula um por cento")"""
    letras = len(re.sub(r"[^A-Za-zÀ-ÿ]", "", w))
    return letras + 5 * len(re.findall(r"\d", w)) + 7 * w.count(",") * bool(re.search(r"\d,\d", w)) + 9 * w.count("%") + 6 * w.count("$") + 1.5


def tempos(texto, s0, s1, pausas):
    """tempo de cada palavra: âncoras nas pausas que caem perto da pontuação, proporcional no resto"""
    ws = texto.split()
    if not ws: return []
    pesos = [peso(w) for w in ws]; acum = np.cumsum(pesos); total = acum[-1]
    segs, ini_i, ini_t = [], 0, s0
    for k, w in enumerate(ws[:-1]):
        if w[-1] not in PONTUA: continue
        esperado = s0 + (s1 - s0) * acum[k] / total
        cand = [p for p in pausas if abs((p[0] + p[1]) / 2 - esperado) < 0.8 and p[0] > ini_t + 0.1]
        if not cand: continue
        p = min(cand, key=lambda p: abs((p[0] + p[1]) / 2 - esperado))
        segs.append((ini_i, k + 1, ini_t, p[0])); ini_i, ini_t = k + 1, p[1]
    segs.append((ini_i, len(ws), ini_t, s1 - 0.05))
    out = []
    for i0, i1, t0, t1 in segs:
        soma = sum(pesos[i0:i1]); c = 0.0
        for k in range(i0, i1):
            a = t0 + (t1 - t0) * c / soma; c += pesos[k]
            out.append([ws[k], a, t0 + (t1 - t0) * c / soma])
    return out


class Ctx:
    def __init__(self, r, est):
        self.r, self.est = r, est
        self.D = r["_proj"]; self.A = os.path.join(self.D, "assets")
        self.cenas = r["cenas"]; self.sons = []; self.usadas = set()  # cenas que mostraram foto (crédito na tela)
        cred = os.path.join(self.D, "fotos", "creditos.json")
        self.cred = json.load(open(cred, encoding="utf-8")) if os.path.exists(cred) else {}
        mf = os.path.join(self.D, "manchetes", "manchetes.json")
        self.manch = json.load(open(mf, encoding="utf-8")) if os.path.exists(mf) else {}
        self.manchetes_usadas = []
        for i, c in enumerate(self.cenas):  # a manchete vale como fonte da cena
            m = self.manch.get(f"c{i}")
            if m and c.get("manchete") and not c.get("fonte"): c["fonte"] = m["veiculo"] + (f', {m["data"]}' if m.get("data") else "")
        for p in ("a", "i", "sfx", "fonts"): os.makedirs(os.path.join(self.A, p), exist_ok=True)
        # linhas do tempo das falas
        t, self.L = INTRO, []
        for i, c in enumerate(self.cenas):
            t += float(c.get("pausa_antes", 0))
            wav = os.path.join(self.D, "voz", f"c{i}.wav")
            mg = os.path.join(self.D, "voz", f"c{i}.margem")
            s0, s1, pausas = analisar(wav, float(open(mg).read()) if os.path.exists(mg) else 0.0)
            ws = [[w, t + a - s0, t + b - s0] for w, a, b in tempos(c["fala"], s0, s1, pausas)]
            self.L.append(dict(i=i, t=t, fim=t + (s1 - s0), s0=s0, s1=s1, ws=ws, c=c))
            d = s1 - s0
            ff("-ss", f"{s0:.3f}", "-i", wav, "-t", f"{d:.3f}", "-af",
               f"apad=pad_dur=2,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,afade=t=in:d=0.02,afade=t=out:st={max(0, d - 0.06):.3f}:d=0.06,loudnorm=I=-16:TP=-1.5",
               "-ar", "48000", "-ac", "2", os.path.join(self.A, "a", f"c{i}.wav"))
            # "segura": tempo extra na tela depois da fala (lista de respostas ganha tempo pra ler)
            t += d + est.GAP + float(c.get("segura", 0)) + 0.75 * len(c.get("lista") or [])
        self.total = self.L[-1]["fim"] + est.FIM

    # ---------- tempo ----------
    def wt(self, L, palavra, n=0):
        """tempo da n-ésima palavra da linha L que começa com `palavra` (sem acento, sem caixa)"""
        alvo = sem_acento(palavra).strip(PONTUA)
        hits = [w for w in L["ws"] if sem_acento(w[0]).strip(PONTUA + "\"“”'").startswith(alvo)]
        return hits[min(n, len(hits) - 1)][1] if hits else None

    def bate(self, L, chave=None, frac=0.5):
        """momento de impacto: a palavra `chave` (ou "bate" da cena), senão uma fração da fala"""
        for k in (L["c"].get("bate"), chave):
            if k:
                for w in str(k).split()[:1]:
                    x = self.wt(L, w)
                    if x is not None: return x
        return L["t"] + (L["fim"] - L["t"]) * frac

    def fim_cena(self, k):
        return self.L[k + 1]["t"] - 0.12 if k + 1 < len(self.L) else self.total

    # ---------- mídia ----------
    def aud(self, arq, t, vol, dur=None):
        if dur is None: dur = duracao_wav(os.path.join(self.A, arq))
        self.sons.append((arq, max(0, t), dur, vol))

    def foto(self, i, modo, largura=900):
        info = self.cred.get(f"c{i}")
        if not info: return None
        self.usadas.add(i)
        origem = os.path.join(self.D, "fotos", info["arquivo"])
        ext = ".jpg" if modo in ("pb", "vhs") else ".png"
        nome = f"c{i}-{modo}{ext}"; saida = os.path.join(self.A, "i", nome)
        if not os.path.exists(saida) or os.path.getmtime(saida) < os.path.getmtime(origem):
            caixa = self.cenas[i].get("foto_corte") or info.get("caixa")  # o acervo já traz o recorte conferido
            reticula.tratar(origem, saida, modo, largura, caixa, semente=i + 1)
        w, h = Image.open(saida).size
        return dict(src=f"assets/i/{nome}", w=w, h=h)

    def manchete(self, i):
        """título, veículo e data da matéria da cena (lidos por scripts/manchetes.py), ou None"""
        m = self.manch.get(f"c{i}") if self.cenas[i].get("manchete") else None
        if m: self.manchetes_usadas.append((i, m))
        return m

    def recorte(self, i, m, top, rot=-2, largura=880, extra=""):
        """recorte de jornal desenhado em código: veículo, data, título (sem a foto da matéria)"""
        tam = cabe(m["titulo"], 58, largura - 80, .5, 5)
        linha = f'<div class="rec-linha">{esc(m["linha"])}</div>' if m.get("linha") else ""
        return (f'<div class="recorte-j" id="rj{i}" style="top:{top}px; left:{(1080 - largura) // 2}px; width:{largura}px; transform:rotate({rot}deg); {extra}">'
                f'<div class="rec-topo"><span>{esc(m["veiculo"]).upper()}</span><span>{esc(m.get("data", ""))}</span></div>'
                f'<div class="rec-tit" style="font-size:{tam}px">{esc(m["titulo"])}</div>{linha}</div>')

    def audios_html(self):
        """cada som numa faixa sem sobreposição (narração e trilha primeiro)"""
        fim_faixa, out = {}, []
        for k, (arq, t, dur, vol) in enumerate(sorted(self.sons, key=lambda a: (not a[0].startswith("a/"), a[1]))):
            tr = 20
            while fim_faixa.get(tr, -1) > t - 0.01: tr += 1
            fim_faixa[tr] = t + dur
            out.append(f'<audio id="au{k}" src="assets/{arq}" data-start="{t:.3f}" data-duration="{dur:.3f}" data-track-index="{tr}" data-volume="{vol}"></audio>')
        return "\n".join(out)

    # ---------- textos ----------
    def legenda(self, fonte_css, cor_ativa, fundo_css="", topo=1330, extra_css="", ativa_prop="color", pular=()):
        """palavra a palavra em blocos de até 3 palavras; quebra na pontuação"""
        h, js, n = [f'<div class="leg" style="top:{topo}px; {extra_css}">'], "", 0
        for L in self.L:
            if L["i"] in pular: continue
            blocos, cur = [], []
            for w in L["ws"]:
                cur.append(w)
                if len(cur) == 3 or w[0][-1] in PONTUA: blocos.append(cur); cur = []
            if cur: blocos.append(cur)
            for bi, b in enumerate(blocos):
                ini = b[0][1]; fim = blocos[bi + 1][0][1] if bi + 1 < len(blocos) else L["fim"] + 0.15
                spans = "".join(f'<span class="w" id="lw{n}-{k}">{esc(w[0])}</span>' for k, w in enumerate(b))
                h.append(f'<div class="ch" id="lc{n}" style="{fonte_css}"><span style="{fundo_css}">{spans}</span></div>')
                js += f'tl.set("#lc{n}", {{ opacity: 1 }}, {ini:.3f}); tl.set("#lc{n}", {{ opacity: 0 }}, {fim:.3f});\n'
                js += f'tl.fromTo("#lc{n}", {{ y: 14 }}, {{ y: 0, duration: 0.12, ease: "power2.out" }}, {ini:.3f});\n'
                for k, w in enumerate(b):
                    js += f'tl.set("#lw{n}-{k}", {{ {ativa_prop}: "{cor_ativa}" }}, {w[1]:.3f});\n'
                n += 1
        h.append("</div>")
        return "\n".join(h), js

    def creditos(self):
        fotos = []
        for k in sorted(self.cred, key=lambda k: int(k[1:])):
            c = self.cred[k]
            item = f'{c["autor"]} ({c["licenca"]})' if c.get("licenca") else c["autor"]
            if item not in fotos: fotos.append(item)
        partes = []
        if fotos:
            via = " via Wikimedia Commons" if any(self.cred[k].get("pagina") for k in self.cred) else ""
            partes.append("Fotos: " + ", ".join(fotos) + via + ".")
        motor = (self.r.get("voz") or {}).get("motor", "sistema")
        propria = (self.r.get("voz") or {}).get("propria")
        partes.append("Narração com a voz do autor, clonada (IA)." if propria else "Narração com voz sintética (IA).")
        partes.append("Feito com IA. Trilha e sons gerados em código.")
        return " ".join(partes)

    def assinatura(self):
        a = self.r.get("assinatura")
        return esc(a) if a else ""


def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def br(s): return esc(s).replace("\n", "<br>")


def cabe(texto, base, largura=940, k=0.55, linhas=3):
    """tamanho de fonte que faz o texto caber: a palavra mais longa numa linha, o todo em `linhas` linhas"""
    t = str(texto); maior = max((len(w) for w in t.split()), default=1)
    return int(max(28, min(base, largura / (maior * k), largura * linhas / (max(1, len(t)) * k))))


FONTES = """@font-face { font-family:"Archivo"; src:url("assets/fonts/Archivo.ttf") format("truetype"); font-weight:100 900; font-stretch:62% 125%; font-display:block; }
@font-face { font-family:"Maquina"; src:url("assets/fonts/CourierPrime-Bold.ttf") format("truetype"); font-weight:700; font-display:block; }
@font-face { font-family:"Jornal"; src:url("assets/fonts/DMSerifDisplay-400.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"JornalIt"; src:url("assets/fonts/DMSerifDisplay-400i.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"Patrick Hand"; src:url("assets/fonts/PatrickHand-Regular.ttf") format("truetype"); font-display:block; }
@font-face { font-family:"Abril Fatface"; src:url("assets/fonts/AbrilFatface-400.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"Alfa Slab One"; src:url("assets/fonts/AlfaSlabOne-400.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"Archivo Black"; src:url("assets/fonts/ArchivoBlack-400.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"Anton"; src:url("assets/fonts/Anton-400.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"Playfair Display"; font-style:italic; font-weight:900; src:url("assets/fonts/PlayfairDisplay-900i.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"DM Serif Display"; src:url("assets/fonts/DMSerifDisplay-400.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"DM Serif Display"; font-style:italic; src:url("assets/fonts/DMSerifDisplay-400i.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"Bungee"; src:url("assets/fonts/Bungee-400.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"Ultra"; src:url("assets/fonts/Ultra-400.woff2") format("woff2"); font-display:block; }
@font-face { font-family:"Pixel"; src:url("assets/fonts/PressStart2P-Regular.ttf") format("truetype"); font-display:block; }
@font-face { font-family:"Pixel2"; src:url("assets/fonts/Silkscreen-Regular.ttf") format("truetype"); font-display:block; }
@font-face { font-family:"Pixel2"; font-weight:700; src:url("assets/fonts/Silkscreen-Bold.ttf") format("truetype"); font-display:block; }
@font-face { font-family:"Rubik"; font-weight:800; src:url("assets/fonts/Rubik-800.woff2") format("woff2"); font-display:block; }
"""
BASE_CSS = """* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:1080px; height:1920px; overflow:hidden; background:#000; }
#root { position:relative; width:1080px; height:1920px; overflow:hidden; font-family:"Archivo", sans-serif; }
.el { position:absolute; opacity:0; }
.grao { position:absolute; left:-40px; top:-40px; width:1160px; height:2000px; opacity:.09; mix-blend-mode:overlay; pointer-events:none; z-index:90; }
.vinheta { position:absolute; inset:0; background:radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 100%); z-index:89; pointer-events:none; }
.leg { position:absolute; left:70px; right:150px; text-align:center; z-index:80; }
.leg .ch { position:absolute; left:0; right:0; opacity:0; }
.leg .w { display:inline-block; margin:0 .12em; }
.cred { position:absolute; left:80px; right:80px; bottom:330px; text-align:center; font:400 21px/1.4 "Archivo"; opacity:0; z-index:85; }
.recorte-j { position:absolute; background:#ece6d6; color:#141414; padding:26px 36px 30px; box-shadow:0 14px 30px rgba(0,0,0,.55); opacity:0;
  background-image:repeating-linear-gradient(0deg, rgba(0,0,0,.035) 0 1px, transparent 1px 5px); clip-path:polygon(0 2%, 3% 0, 30% 1.5%, 62% 0, 100% 1%, 99% 40%, 100% 98%, 70% 100%, 35% 98.5%, 2% 100%, 0 60%); }
.recorte-j .rec-topo { display:flex; justify-content:space-between; font:900 24px/1 "Archivo"; letter-spacing:2px; border-bottom:3px solid #141414; padding-bottom:10px; margin-bottom:16px; }
.recorte-j .rec-topo span:last-child { font:700 22px "Maquina"; letter-spacing:0; }
.recorte-j .rec-tit { font:400 58px/1.08 "Jornal"; }
.recorte-j .rec-linha { font:400 28px/1.3 "Archivo"; margin-top:14px; color:#333; }
.cred-foto { position:absolute; left:40px; right:40px; bottom:22px; text-align:right; font:500 19px/1.2 "Archivo"; color:rgba(240,240,232,.78); text-shadow:0 1px 3px #000, 0 0 8px rgba(0,0,0,.8); opacity:0; z-index:95; }
.fim-ass { position:absolute; left:0; right:0; bottom:440px; text-align:center; font:600 30px "Archivo"; letter-spacing:1px; opacity:0; z-index:85; }
"""

PRELUDIO = """window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
const FPS = 12;
const st = (e, d) => { const f = gsap.parseEase(e || "power2.out"); const n = Math.max(1, Math.round(d * FPS)); return t => f(Math.min(1, Math.floor(t * n + 1e-6) / n)); };
let semente = 11;
const rnd = () => { semente = (semente * 16807) % 2147483647; return semente / 2147483647; };
"""


def html(ctx, corpo, js):
    est = ctx.est
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
{FONTES}{BASE_CSS}{est.CSS}
</style>
</head>
<body>
{getattr(est, "SVG_DEFS", "")}
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{ctx.total:.3f}">
{corpo}
<img class="grao" src="assets/grao.png">
{ctx.audios_html()}
</div>
<script>
{PRELUDIO}{getattr(est, "JS_ANTES", "")}
for (let t = 0; t < {ctx.total:.3f}; t += 1 / FPS) tl.set(".grao", {{ x: -Math.round(rnd() * 40), y: -Math.round(rnd() * 40) }}, +t.toFixed(3));
{js}
tl.set({{}}, {{}}, {ctx.total:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""


def carregar_estilo(nome):
    """estilos/<nome>/estilo.py; um estilo só com config.json usa o estilo configurável (estilos/_base)"""
    pasta = os.path.join(SKILL, "estilos", nome)
    arq = os.path.join(pasta, "estilo.py")
    if not os.path.exists(arq):
        if not os.path.exists(os.path.join(pasta, "config.json")):
            raise SystemExit(f'Estilo "{nome}" não existe. Veja os estilos com: python3 scripts/estilos.py')
        base = carregar_estilo("_base")
        return base.com_config(os.path.join(pasta, "config.json"))
    chave = f"estilo_{nome.replace('-', '_')}"
    if chave in sys.modules: return sys.modules[chave]
    spec = importlib.util.spec_from_file_location(chave, arq)
    mod = importlib.util.module_from_spec(spec); sys.modules[chave] = mod; spec.loader.exec_module(mod)
    return mod


def montar(r):
    estilo = r["estilo"]
    passo(f"Montagem (estilo {estilo})")
    est = carregar_estilo(estilo)
    ctx = Ctx(r, est)
    A = ctx.A
    for f in os.listdir(os.path.join(ASSETS, "fonts")):
        if not f.startswith("."): shutil.copy(os.path.join(ASSETS, "fonts", f), os.path.join(A, "fonts", f))
    sons.gerar(os.path.join(A, "sfx"), est.CAMA, ctx.total)
    rng = np.random.default_rng(3)
    Image.fromarray(rng.normal(128, 40, (960, 540)).clip(0, 255).astype(np.uint8)).resize((1080, 1920), Image.NEAREST).save(os.path.join(A, "grao.png"))
    corpo, js = est.cenas(ctx)
    # crédito da foto embaixo, durante a cena que usa a foto
    for i in sorted(ctx.usadas):
        c = ctx.cred.get(f"c{i}", {}); L = ctx.L[i]
        if not c.get("autor"): continue
        txt = f'Foto: {c["autor"]}' + (f' ({c["licenca"]})' if c.get("licenca") else "") + (", Wikimedia Commons" if c.get("pagina") else "")
        corpo.append(f'<div class="cred-foto" id="cf{i}">{esc(txt)}</div>')
        js += f'tl.set("#cf{i}", {{ opacity: 1 }}, {max(0, L["t"] - 0.1):.3f}); tl.set("#cf{i}", {{ opacity: 0 }}, {ctx.fim_cena(i):.3f});\n'
    for i, m in ctx.manchetes_usadas:
        L = ctx.L[i]
        corpo.append(f'<div class="cred-foto" id="cm{i}">{esc("Reprodução: " + m["veiculo"] + (", " + m["data"] if m.get("data") else ""))}</div>')
        js += f'tl.set("#cm{i}", {{ opacity: 1 }}, {max(0, L["t"] - 0.1):.3f}); tl.set("#cm{i}", {{ opacity: 0 }}, {ctx.fim_cena(i):.3f});\n' 
    for L in ctx.L: ctx.aud(f"a/c{L['i']}.wav", L["t"], 1.0)
    ctx.aud("sfx/cama.wav", 0.0, est.VOL_CAMA, ctx.total)
    open(os.path.join(ctx.D, "index.html"), "w", encoding="utf-8").write(html(ctx, "\n".join(corpo), js))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"assets": "assets"}, "media": {"autoProxy": False}},
              open(os.path.join(ctx.D, "hyperframes.json"), "w"), indent=2)
    json.dump({"name": r["_nome"], "private": True, "type": "module",
               "scripts": {k: f"npx --yes {HYPERFRAMES} {k}" for k in ("preview", "render")}}, open(os.path.join(ctx.D, "package.json"), "w"), indent=2)
    # créditos e fontes num texto, pra legenda do post
    fontes = []
    for c in r["cenas"]:
        for f in [c.get("fonte")] + [x.get("fonte") for x in c.get("lista") or []]:
            if f and f not in fontes: fontes.append(f)
    open(os.path.join(r["_pasta"], f"{r['_nome']}-fontes.txt"), "w", encoding="utf-8").write(
        "Fontes:\n" + "\n".join(f"- {f}" for f in fontes) + "\n\n" + ctx.creditos() + "\nConteúdo orgânico, sem impulsionamento.\n")
    print(f"  {ctx.D}/index.html  ({ctx.total:.1f} s, {len(ctx.L)} cenas)")
    return ctx


if __name__ == "__main__":
    if len(sys.argv) < 2: raise SystemExit("uso: python3 scripts/montar.py roteiro.json")
    montar(ler_roteiro(sys.argv[1]))
