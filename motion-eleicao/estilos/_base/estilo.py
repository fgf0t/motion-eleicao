# Estilo configurável: a base dos estilos novos criados a partir de referências.
# Um estilo novo é só uma pasta estilos/<nome>/ com sobre.json + config.json (ver estilos/_base/config-modelo.json).
# Este arquivo lê o config e desenha as cenas: fundo, foto, título, número, carimbo, citação, lista, fonte e fecho,
# com a entrada, a transição e os efeitos escolhidos.
import json, os, types
from montar import br, cabe, esc

FONTES_TITULO = {"Archivo": "900 {t}px/.9 Archivo; font-stretch:75%", "Archivo Black": "400 {t}px/.95 'Archivo Black'", "Anton": "400 {t}px/.95 Anton",
                 "Abril Fatface": "400 {t}px/.95 'Abril Fatface'", "Alfa Slab One": "400 {t}px/.95 'Alfa Slab One'", "Bungee": "400 {t}px/.95 Bungee",
                 "Ultra": "400 {t}px/.95 Ultra", "Rubik": "800 {t}px/.95 Rubik", "Playfair Display": "italic 900 {t}px/.95 'Playfair Display'",
                 "DM Serif Display": "400 {t}px/.95 'DM Serif Display'", "Maquina": "700 {t}px/1 Maquina", "Patrick Hand": "400 {t}px/1 'Patrick Hand'",
                 "Pixel": "400 {t}px/1.1 Pixel", "Pixel2": "400 {t}px/1 Pixel2", "Recortada": "400 {t}px/1 Archivo"}
LARGURA = {"Archivo": .52, "Archivo Black": .66, "Anton": .5, "Abril Fatface": .62, "Alfa Slab One": .7, "Bungee": .75, "Ultra": .8, "Rubik": .66,
           "Playfair Display": .6, "DM Serif Display": .55, "Maquina": .62, "Patrick Hand": .45, "Pixel": 1.0, "Pixel2": .7, "Recortada": .88}
PADRAO = {
    "fundo": {"cor": "#151515", "cor2": "#2a2a2a", "textura": "grao"},
    "paleta": {"texto": "#f1f1ec", "destaque": "#f2c230", "apoio": "#e0464f", "papel": "#f4f1e8"},
    "fonte_titulo": "Archivo", "titulo_caixa_alta": True, "fonte_texto": "Archivo",
    "foto": {"modo": "pb", "moldura": "borda", "posicao": "topo"},
    "entrada": "pop", "transicao": "corte", "movimento_degrau": True,
    "efeitos": ["grao", "vinheta"],
    "camadas": [],
    "legenda": {"cor": "#f1f1ec", "ativa": "#f2c230", "fundo": "rgba(0,0,0,.6)", "fonte": "Archivo"},
    "carimbo": {"cor": "#e0464f", "forma": "borda"},
    "cama": "dados",
}


def mescla(a, b):
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = mescla(a[k], v) if isinstance(v, dict) and isinstance(a.get(k), dict) else v
    return out


OPCOES = {("fundo", "textura"): "grao papel grade linhas pontos pixel nenhuma", ("fonte_titulo",): " ".join(FONTES_TITULO).replace("Archivo Black", "").split(),
          ("foto", "modo"): "pb cor vhs branca jornal tiras", ("foto", "moldura"): "borda polaroide rasgado pixel nenhuma", ("foto", "posicao"): "topo cheia",
          ("entrada",): "pop desliza maquina glitch corte", ("transicao",): "corte chicote preto flash faixas", ("carimbo", "forma"): "borda faixa",
          ("cama",): "leve dossie vhs dados pixel pesquise"}
CAMADAS = {"retalhos", "amassado", "formas", "tarjas"}


def com_config(caminho):
    dado = json.load(open(caminho, encoding="utf-8"))
    cfg = mescla(PADRAO, dado)
    for chave, ops in OPCOES.items():  # valor fora da lista volta pro padrão, com aviso
        alvo, padrao = cfg, PADRAO
        for c in chave[:-1]: alvo, padrao = alvo[c], padrao[c]
        v = alvo.get(chave[-1]); ops = ops.split() if isinstance(ops, str) else ops
        if chave == ("fonte_titulo",): ops = list(FONTES_TITULO)
        if v not in ops:
            print(f'  ! config: {".".join(chave)} = "{v}" não existe; usando "{padrao[chave[-1]]}". Opções: {", ".join(ops)}')
            alvo[chave[-1]] = padrao[chave[-1]]
    errados = [c for c in cfg.get("camadas", []) if c not in CAMADAS]
    if errados: print(f'  ! config: camadas {errados} não existem; opções: {", ".join(sorted(CAMADAS))}'); cfg["camadas"] = [c for c in cfg["camadas"] if c in CAMADAS]
    m = types.SimpleNamespace(GAP=0.5, FIM=3.6, CAMA=cfg.get("cama", "dados"), VOL_CAMA=0.3)
    P, F = cfg["paleta"], cfg["fundo"]
    tex = {"grao": "", "papel": f"background-image:var(--papel);",
           "grade": f"background-image:linear-gradient({F['cor2']} 2px, transparent 2px), linear-gradient(90deg, {F['cor2']} 2px, transparent 2px); background-size:60px 60px;",
           "linhas": f"background-image:repeating-linear-gradient(0deg, {F['cor2']} 0 2px, transparent 2px 9px);",
           "pontos": f"background-image:radial-gradient({F['cor2']} 2px, transparent 2.5px); background-size:22px 22px;",
           "pixel": f"background-image:linear-gradient({F['cor2']} 1px, transparent 1px), linear-gradient(90deg, {F['cor2']} 1px, transparent 1px); background-size:12px 12px;",
           "nenhuma": ""}.get(F.get("textura", "grao"), "")
    moldura = {"polaroide": f"background:{P['papel']}; padding:20px 20px 90px; box-shadow:0 18px 30px rgba(0,0,0,.45);",
               "borda": f"border:10px solid {P['papel']}; box-shadow:0 14px 30px rgba(0,0,0,.45);",
               "rasgado": f"background:{P['papel']}; padding:14px; filter:drop-shadow(8px 10px 0 rgba(0,0,0,.3));",
               "pixel": f"border:12px solid {P['texto']}; outline:6px solid {P['destaque']}; outline-offset:-24px; image-rendering:pixelated;",
               "nenhuma": ""}.get(cfg["foto"].get("moldura", "borda"), "")
    filtro = {"pb": "grayscale(1) contrast(1.15)", "tiras": "grayscale(1) contrast(1.2)", "vhs": "grayscale(.85) contrast(1.35) brightness(.78)", "cor": "none"}.get(cfg["foto"].get("modo"), "none")
    tarja = contraste(P["destaque"], F["cor"]) < 3  # amarelo solto em fundo claro não se lê: vira tarja
    tinta = cor_sobre(P["destaque"])
    num_cor = f"color:{tinta}; background:{P['destaque']}; width:fit-content; margin:0 auto; padding:.02em .14em 0; transform:rotate(-2deg);" if tarja else f"color:{P['destaque']};"
    li_cor = f"display:inline-block; color:{tinta}; background:{P['destaque']}; padding:6px 16px 2px; margin-top:6px;" if tarja else f"display:block; color:{P['destaque']};"
    m.CSS = f"""
:root {{ --papel: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' seed='4'/%3E%3CfeColorMatrix values='0 0 0 0 0.3 0 0 0 0 0.25 0 0 0 0 0.2 0 0 0 0.25 0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E"); }}
html, body {{ background:{F['cor']}; }}
#fundo-b {{ position:absolute; inset:-40px; background-color:{F['cor']}; {tex} }}
.foto-b {{ position:absolute; left:50%; opacity:0; z-index:3; {moldura} }}
.foto-b img {{ display:block; width:100%; height:100%; object-fit:cover; filter:{filtro}; }}
.foto-b.cheia {{ left:-40px; top:-40px; width:1160px; height:2000px; border:0; padding:0; outline:0; box-shadow:none; background:none; }}
.foto-b.cheia img {{ filter:{filtro} brightness(.55); }}
.tit-b {{ position:absolute; left:90px; right:150px; text-align:center; color:{P['texto']}; opacity:0; z-index:10; {"text-transform:uppercase;" if cfg.get("titulo_caixa_alta") else ""} }}
.num-b {{ position:absolute; left:0; right:0; text-align:center; {num_cor} opacity:0; z-index:11; white-space:nowrap; font:900 300px/1 Archivo; font-stretch:72%; }}
.det-b {{ position:absolute; left:90px; right:150px; text-align:center; color:{P['texto']}; font:400 46px/1.2 {_fonte_texto(cfg)}; opacity:0; z-index:10; }}
.carimbo-b {{ position:absolute; left:0; right:0; margin:0 auto; width:fit-content; opacity:0; z-index:12; white-space:nowrap; text-transform:uppercase; font:900 70px/1 Archivo; font-stretch:78%; padding:10px 24px;
  {"background:" + cfg['carimbo']['cor'] + "; color:" + F['cor'] + ";" if cfg['carimbo'].get('forma') == 'faixa' else "border:8px solid " + cfg['carimbo']['cor'] + "; color:" + cfg['carimbo']['cor'] + ";"} }}
.cita-b {{ position:absolute; left:80px; right:150px; background:{P['papel']}; color:#1b1b1b; padding:30px 36px; font:46px/1.25 JornalIt; opacity:0; z-index:10; box-shadow:0 12px 24px rgba(0,0,0,.4); }}
.cita-b small {{ display:block; margin-top:12px; font:700 22px Maquina; letter-spacing:1px; }}
.li-b {{ position:absolute; left:90px; right:150px; opacity:0; z-index:10; color:{P['texto']}; font:400 36px/1.15 {_fonte_texto(cfg)}; }}
.li-b b {{ {li_cor} font:900 56px/1 Archivo; font-stretch:75%; text-transform:uppercase; }}
.li-b small {{ display:block; margin-top:6px; font:700 20px Maquina; opacity:.7; }}
.fonte-b {{ position:absolute; left:70px; right:150px; text-align:center; font:700 23px Maquina; letter-spacing:1px; color:{P.get('fonte', P['texto'])}; opacity:0; z-index:12; }}
.faixa-b {{ position:absolute; left:0; width:1080px; opacity:0; z-index:60; }}
.cam-b {{ position:absolute; opacity:0; }}
.jornal-b {{ background-color:#e6dcc4; background-image:var(--papel), repeating-linear-gradient(0deg, rgba(40,30,20,.55) 0 3px, transparent 3px 12px); filter:drop-shadow(6px 8px 0 rgba(0,0,0,.35)); }}
.amassado-b {{ background:#151413; background-image:var(--papel); filter:contrast(1.6) drop-shadow(6px 8px 0 rgba(0,0,0,.3)); }}
.tira-b {{ position:absolute; overflow:hidden; }}
.tira-b img {{ position:absolute; left:0; filter:{filtro}; }}
.palavra {{ display:flex; justify-content:center; align-items:flex-end; flex-wrap:wrap; gap:.06em; }}
.chip {{ display:inline-block; filter:drop-shadow(.04em .05em 0 rgba(20,20,20,.45)); }}
.letra {{ display:inline-block; line-height:1; padding:.06em .1em .02em; }}
.espaco {{ display:inline-block; width:.4em; }}
#linhas-b {{ position:absolute; inset:0; background:repeating-linear-gradient(0deg, rgba(0,0,0,.25) 0 2px, rgba(0,0,0,0) 2px 5px); z-index:61; pointer-events:none; }}
#persiana-b {{ position:absolute; inset:-200px; background:repeating-linear-gradient(115deg, rgba(0,0,0,0) 0 160px, rgba(0,0,0,.22) 160px 230px); filter:blur(16px); z-index:62; pointer-events:none; }}
#flash-b {{ position:absolute; inset:0; background:{P['texto']}; opacity:0; z-index:63; pointer-events:none; }}
#preto-b {{ position:absolute; inset:0; background:#000; opacity:0; z-index:63; pointer-events:none; }}
.cred {{ color:{P['texto']}; opacity:0; }}
.fim-ass {{ color:{P['texto']}; }}
"""
    pares = json.dumps([[P["papel"], "#1b1b1b"], [P["destaque"], "#1b1b1b"], ["#1b1b1b", P["papel"]], [P["apoio"], "#1b1b1b"], ["#ffffff", "#1b1b1b"]])
    m.JS_ANTES = """const gerador = (s) => () => ((s = (s * 16807) % 2147483647) / 2147483647);
const borda = (r) => { const p = [], j = () => (r() * 7).toFixed(1);
  for (let i = 0; i <= 4; i++) p.push(`${i * 25}% ${j()}%`); for (let i = 1; i <= 4; i++) p.push(`${100 - j()}% ${i * 25}%`);
  for (let i = 3; i >= 0; i--) p.push(`${i * 25}% ${100 - j()}%`); for (let i = 3; i >= 1; i--) p.push(`${j()}% ${i * 25}%`); return `polygon(${p.join(",")})`; };
document.querySelectorAll(".rasga").forEach((el, i) => { if (!el.style.borderRadius) el.style.clipPath = borda(gerador(4049 + i * 131)); });
const FONTES_R = [["Abril Fatface", 400, "normal"], ["Alfa Slab One", 400, "normal"], ["Archivo Black", 400, "normal"], ["Anton", 400, "normal"],
  ["Playfair Display", 900, "italic"], ["DM Serif Display", 400, "normal"], ["Bungee", 400, "normal"], ["Ultra", 400, "normal"], ["Maquina", 700, "normal"]];
const PARES = """ + pares + """;
document.querySelectorAll("[data-recorte]").forEach((el) => { const r = gerador(+el.dataset.semente * 7919 + 1); let ultimo = -1;
  let pal = document.createElement("span"); pal.style.cssText = "display:inline-flex; white-space:nowrap; align-items:flex-end; gap:.06em"; el.appendChild(pal);
  [...el.dataset.recorte].forEach((c) => { if (c === " ") { const e = document.createElement("span"); e.className = "espaco"; el.appendChild(e);
      pal = document.createElement("span"); pal.style.cssText = "display:inline-flex; white-space:nowrap; align-items:flex-end; gap:.06em"; el.appendChild(pal); return; }
    let f; do { f = Math.floor(r() * FONTES_R.length); } while (f === ultimo); ultimo = f;
    const [fam, peso, estilo] = FONTES_R[f], [fundo, cor] = PARES[Math.floor(r() * PARES.length)];
    const chip = document.createElement("span"); chip.className = "chip"; const l = document.createElement("span"); l.className = "letra"; l.textContent = c;
    Object.assign(l.style, { fontFamily: `"${fam}"`, fontWeight: peso, fontStyle: estilo, background: fundo, color: cor, clipPath: borda(r), fontSize: (0.85 + r() * 0.3).toFixed(2) + "em" });
    chip.style.transform = `rotate(${((r() - 0.5) * 12).toFixed(1)}deg)`; chip.appendChild(l); pal.appendChild(chip); }); });
"""
    if cfg.get("movimento_degrau", True):
        m.JS_ANTES += """const DEGRAU = 12;
const emDegrau = (v) => { const n = Math.max(1, Math.round((v.duration ?? 0.5) * DEGRAU)), e = gsap.parseEase(v.ease || "power1.out"); return { ...v, ease: (p) => e(Math.floor(p * n) / n) }; };
const _to = tl.to.bind(tl), _from = tl.from.bind(tl), _fromTo = tl.fromTo.bind(tl);
tl.to = (t, v, p) => _to(t, emDegrau(v), p); tl.from = (t, v, p) => _from(t, emDegrau(v), p); tl.fromTo = (t, a, b, p) => _fromTo(t, a, emDegrau(b), p);
"""
    m.cenas = lambda x: _cenas(x, cfg)
    return m


def _lum(h):
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    """razão de contraste WCAG entre duas cores #rrggbb (3 = mínimo pra número grande)"""
    try: la, lb = _lum(a), _lum(b)
    except ValueError: return 21
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def cor_sobre(fundo):
    return "#1b1b1b" if contraste(fundo, "#1b1b1b") >= contraste(fundo, "#ffffff") else "#ffffff"


def _fonte_texto(cfg):
    return {"Maquina": "Maquina", "Patrick Hand": "'Patrick Hand'", "Jornal": "Jornal", "Pixel": "Pixel", "Pixel2": "Pixel2"}.get(cfg.get("fonte_texto"), "Archivo")


def titulo(tid, txt, top, tam, fonte_t, k):
    if fonte_t == "Recortada":
        return f'<div class="tit-b palavra" id="{tid}" data-recorte="{esc(str(txt).replace(chr(10), " "))}" data-semente="{k * 7 + 3}" style="top:{top}px; font-size:{tam}px"></div>'
    return f'<div class="tit-b" id="{tid}" style="top:{top}px; font:{FONTES_TITULO.get(fonte_t, FONTES_TITULO["Archivo"]).format(t=tam)}">{br(txt)}</div>'


def camadas(cfg, k, x, y, w, h, atras):
    """colagem em volta da foto: retalhos de jornal, papel amassado, tarjas de cor e formas (com semente)"""
    import random
    rng = random.Random(k * 31 + (0 if atras else 7)); P = cfg["paleta"]; out = []; cl = "ca" if atras else "cf"
    cam = cfg.get("camadas") or []
    if atras and "retalhos" in cam:
        for j in range(3):
            rw, rh = rng.randint(260, 460), rng.randint(220, 420)
            out.append(f'<div class="cam-b jornal-b rasga {cl}{k}" style="left:{x + rng.uniform(-200, w - 160):.0f}px; top:{y + rng.uniform(-120, h - 120):.0f}px; width:{rw}px; height:{rh}px; z-index:2; transform:rotate({rng.uniform(-12, 12):.1f}deg)"></div>')
    if atras and "amassado" in cam:
        out.append(f'<div class="cam-b amassado-b rasga {cl}{k}" style="left:{x + w - 180:.0f}px; top:{y + h * .5:.0f}px; width:300px; height:340px; z-index:2; transform:rotate({rng.uniform(-20, 20):.1f}deg)"></div>')
    if atras and "formas" in cam:
        out.append(f'<div class="cam-b {cl}{k}" style="left:{x + w - 120:.0f}px; top:{y + h - 140:.0f}px; width:220px; height:220px; border-radius:50%; background:{P["destaque"]}; z-index:2"></div>')
        out.append(f'<div class="cam-b {cl}{k}" style="left:{x - 70:.0f}px; top:{y + 40:.0f}px; width:110px; height:110px; border-radius:50%; background:#151413; z-index:2"></div>')
    if not atras and "tarjas" in cam:
        for j in range(2):
            ty = y + h * (0.28 + j * 0.3) + rng.uniform(-20, 20)
            out.append(f'<div class="cam-b rasga {cl}{k}" style="left:{x - 60 + j * 50:.0f}px; top:{ty:.0f}px; width:{w + 80}px; height:{rng.randint(46, 80)}px; background:{P["destaque"]}; z-index:4; mix-blend-mode:multiply; transform:rotate({rng.uniform(-3, 3):.1f}deg)"></div>')
    return out


def entra(cfg, sel, t, ate, sgn=1):
    """animação de entrada escolhida no config"""
    e = cfg.get("entrada", "pop")
    if e == "desliza": j = f'tl.fromTo("{sel}", {{ opacity: 0, x: {600 * sgn} }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }}, {t:.3f});\n'
    elif e == "maquina": j = f'tl.set("{sel}", {{ opacity: 1 }}, {t:.3f}); tl.fromTo("{sel}", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.6, ease: "steps(14)" }}, {t:.3f});\n'
    elif e == "glitch": j = f'tl.set("{sel}", {{ opacity: 1 }}, {t:.3f}); tl.fromTo("{sel}", {{ x: -20, skewX: 10 }}, {{ x: 0, skewX: 0, duration: 0.15, ease: "steps(3)" }}, {t:.3f});\n'
    elif e == "corte": j = f'tl.set("{sel}", {{ opacity: 1 }}, {t:.3f});\n'
    else: j = f'tl.fromTo("{sel}", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, {t:.3f});\n'
    return j + f'tl.set("{sel}", {{ opacity: 0 }}, {ate:.3f});\n'


def _cenas(x, cfg):
    P = cfg["paleta"]; c, js = ['<div id="fundo-b"></div>'], ""
    ult = len(x.L) - 1; fonte_t = cfg.get("fonte_titulo", "Archivo"); k_larg = LARGURA.get(fonte_t, .6)
    modo_foto = {"pb": "pb", "vhs": "vhs", "cor": "vhs", "branca": "branca", "jornal": "jornal"}.get(cfg["foto"].get("modo", "pb"), "pb")
    cheia = cfg["foto"].get("posicao") == "cheia"
    x.aud("sfx/boom.wav", 0.0, 0.3, 4.0)
    for k, L in enumerate(x.L):
        cena, t0, t1 = L["c"], L["t"] - 0.1, x.fim_cena(k); sgn = 1 if k % 2 == 0 else -1
        if k and x.r.get("camera") == "canva": t0 = L["t"] - 0.6  # a câmera sai rumo a um quadro que já tem foto e título
        if k == 0: t0 = 0.0  # o primeiro quadro do vídeo já abre montado
        ti = t0 + 0.1  # entrada do título
        if k == ult:
            txt = cena.get("tela") or cena["fala"]; tam = cabe(txt, 200, 840, k_larg, 4)
            c.append(titulo(f"t{k}", txt, 520, tam, fonte_t, k))
            js += entra(cfg, f"#t{k}", L["t"], x.total, sgn); x.aud("sfx/thump.wav", L["t"], 0.5)
            if cena.get("detalhe"):
                # chamada final em tarja da cor de destaque (cor solta sobre fundo claro não se lê)
                rgb = [int(P["destaque"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
                cor_t = "#1b1b1b" if (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) > 140 else "#ffffff"
                c.append(f'<div class="det-b" id="d{k}" style="top:1150px; left:0; right:0; margin:0 auto; width:fit-content; max-width:900px; '
                         f'background:{P["destaque"]}; color:{cor_t}; font-weight:700; font-size:56px; padding:12px 30px; transform:rotate(-2deg)">{esc(cena["detalhe"])}</div>')
                js += entra(cfg, f"#d{k}", L["t"] + (L["fim"] - L["t"]) * 0.6, x.total)
            continue
        y = 300
        tela = cena.get("tela")
        tam_t = cabe(tela, 150, 840, k_larg, 2) if tela else 0
        lin_t = max(1, round(len(tela) * tam_t * k_larg / 840 + .4)) if tela else 0
        tam_n = cabe(cena["numero"], 240, 1000, .55, 1) if cena.get("numero") else 0
        alt_txt = (tam_t * 1.05 * lin_t + 40) + tam_n * 1.05 + (90 if cena.get("detalhe") else 0) + (110 if cena.get("carimbo") else 0)
        f = x.foto(k, modo_foto, 900) if not (cena.get("lista") or cena.get("citacao")) else None
        tem_foto = bool(f)
        if f:
            if cheia:
                c.append(f'<div class="foto-b cheia" id="f{k}"><img src="{f["src"]}"></div>')
                js += f'tl.set("#f{k}", {{ opacity: 1 }}, {t0:.3f}); tl.fromTo("#f{k}", {{ scale: 1.02 }}, {{ scale: 1.12, duration: {t1 - t0:.2f}, ease: "none" }}, {t0:.3f}); tl.set("#f{k}", {{ opacity: 0 }}, {t1:.3f});\n'
            else:
                alt = max(300, min(640, 1320 - y - 90 - alt_txt))
                w = int(min(860, alt * f["w"] / f["h"])); h = int(w * f["h"] / f["w"])
                c.extend(camadas(cfg, k, 540 - w / 2, y, w, h, atras=True))
                if cfg["foto"].get("modo") == "tiras":  # foto cortada em 3 tiras deslocadas
                    tiras = "".join(f'<div class="tira-b" style="left:{(j - 1) * 28 * sgn}px; top:{h * j / 3:.0f}px; width:{w}px; height:{h / 3 + 1:.0f}px"><img src="{f["src"]}" style="top:{-h * j / 3:.0f}px; width:{w}px; height:{h}px"></div>' for j in range(3))
                    c.append(f'<div class="foto-b" id="f{k}" style="top:{y}px; width:{w}px; height:{h}px; margin-left:{-w / 2:.0f}px; transform:rotate({-2 * sgn}deg); background:none; padding:0; border:0; box-shadow:none">{tiras}</div>')
                else:
                    c.append(f'<div class="foto-b" id="f{k}" style="top:{y}px; width:{w}px; height:{h}px; margin-left:{-w / 2:.0f}px; transform:rotate({-2 * sgn}deg)"><img src="{f["src"]}"></div>')
                c.extend(camadas(cfg, k, 540 - w / 2, y, w, h, atras=False))
                for cl in ("ca", "cf"): js += f'tl.set(".{cl}{k}", {{ opacity: 1 }}, {t0:.3f}); tl.set(".{cl}{k}", {{ opacity: 0 }}, {t1:.3f});\n' 
                js += entra(cfg, f"#f{k}", t0, t1, sgn); x.aud("sfx/papel.wav", t0, 0.4)
                y += h + 90
        if tela:
            tam = tam_t
            c.append(titulo(f"t{k}", tela, y, tam, fonte_t, k))
            js += entra(cfg, f"#t{k}", ti, t1, sgn); x.aud("sfx/pop.wav", ti, 0.35)
            y += int(tam * 1.05 * lin_t) + 40
        if cena.get("numero"):
            tam = tam_n; tn = x.bate(L, cena["numero"], 0.4) if tem_foto else ti + 0.25  # sem foto, o número preenche o quadro desde o início
            c.append(f'<div class="num-b" id="n{k}" style="top:{y}px; font-size:{tam}px">{esc(cena["numero"])}</div>')
            js += entra(cfg, f"#n{k}", tn, t1, sgn); x.aud("sfx/thump.wav", tn, 0.6)
            y += int(tam * 1.05)
        if cena.get("detalhe"):
            c.append(f'<div class="det-b" id="d{k}" style="top:{y}px">{esc(cena["detalhe"])}</div>')
            js += entra(cfg, f"#d{k}", x.bate(L, None, 0.5) if tem_foto else ti + 0.45, t1, sgn); y += 90
        if cena.get("citacao"):
            quem = f'<small>{esc(cena.get("quem", "")).upper()}</small>' if cena.get("quem") else ""
            c.append(f'<div class="cita-b" id="q{k}" style="top:{y}px">“{esc(cena["citacao"])}”{quem}</div>')
            js += entra(cfg, f"#q{k}", ti + 0.35, t1, sgn); y += 200 + 55 * (len(cena["citacao"]) // 30)
        n_li = len(cena.get("lista") or [])
        for j, it in enumerate(cena.get("lista") or []):
            tj = ti + 0.35 + j * max(0.6, (L["fim"] - ti - 0.6) / max(1, n_li))  # uma por vez ao longo da fala, a primeira logo no começo
            c.append(f'<div class="li-b" id="l{k}-{j}" style="top:{y}px">{esc(it.get("q", ""))}<b>{esc(it.get("a", ""))}</b><small>{esc(it.get("fonte", "")).upper()}</small></div>')
            js += entra(cfg, f"#l{k}-{j}", tj, t1, sgn); x.aud("sfx/thump.wav", tj, 0.45); y += 170
        if cena.get("carimbo"):
            tc = x.bate(L, None, 0.75)
            c.append(f'<div class="carimbo-b" id="cb{k}" style="top:{y + 10}px; font-size:{cabe(cena["carimbo"], 70, 900, .55, 1)}px; transform:rotate(-4deg)">{esc(cena["carimbo"])}</div>')
            js += f'tl.fromTo("#cb{k}", {{ opacity: 0, scale: 2.2 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "power4.in" }}, {tc:.3f}); tl.set("#cb{k}", {{ opacity: 0 }}, {t1:.3f});\n'
            x.aud("sfx/carimbo.wav", tc, 0.6)
        if cena.get("fonte"):
            c.append(f'<div class="fonte-b" id="o{k}" style="top:1385px">FONTE: {esc(cena["fonte"]).upper()}</div>')
            js += f'tl.to("#o{k}", {{ opacity: .9, duration: 0.2 }}, {L["t"] + 0.5:.3f}); tl.set("#o{k}", {{ opacity: 0 }}, {t1:.3f});\n'
        # transição pra próxima cena
        if k + 1 < len(x.L):
            tt = x.L[k + 1]["t"] - 0.2; tr = cfg.get("transicao", "corte")
            if tr == "preto": js += f'tl.set("#preto-b", {{ opacity: 1 }}, {tt:.3f}); tl.set("#preto-b", {{ opacity: 0 }}, {tt + 0.2:.3f});\n'
            elif tr == "flash": js += f'tl.set("#flash-b", {{ opacity: .9 }}, {tt + 0.12:.3f}); tl.to("#flash-b", {{ opacity: 0, duration: 0.25 }}, {tt + 0.16:.3f});\n'
            elif tr == "faixas":
                cores = [P["destaque"], P["apoio"], P["texto"], cfg["fundo"]["cor"]]
                for j, cor in enumerate(cores):
                    js += (f'tl.set("#fx{j}", {{ opacity: 1, backgroundColor: "{cor}", top: {(j * 480 + k * 170) % 1920}, height: 480, x: {-1100 * sgn} }}, {tt:.3f}); '
                           f'tl.to("#fx{j}", {{ x: {1100 * sgn}, duration: 0.3, ease: "steps(4)" }}, {tt + j * 0.03:.3f}); tl.set("#fx{j}", {{ opacity: 0 }}, {tt + 0.34 + j * 0.03:.3f});\n')
            elif tr == "chicote": js += f'tl.fromTo("#cena-b", {{ filter: "blur(0px)" }}, {{ filter: "blur(14px)", duration: 0.15, yoyo: true, repeat: 1, immediateRender: false }}, {tt:.3f});\n'
            x.aud("sfx/whoosh.wav", tt - 0.1, 0.25)
    corpo = ['<div id="cena-b" style="position:absolute; inset:0">'] + c + ['</div>']
    corpo += [f'<div class="faixa-b" id="fx{j}"></div>' for j in range(4)]
    ef = cfg.get("efeitos", [])
    if "scanlines" in ef: corpo.append('<div id="linhas-b"></div>')
    if "persiana" in ef: corpo.append('<div id="persiana-b"></div>'); js += f'tl.fromTo("#persiana-b", {{ x: -60 }}, {{ x: 60, duration: {x.total:.2f}, ease: "none" }}, 0);\n'
    if "vinheta" in ef: corpo.append('<div class="vinheta"></div>')
    corpo.append('<div id="flash-b"></div><div id="preto-b"></div>')
    if "grao" not in ef: js += 'tl.set(".grao", { display: "none" }, 0);\n'
    fim = x.L[-1]["fim"]
    corpo.append(f'<div class="cred" id="cred">{esc(x.creditos())}</div>')
    js += f'tl.to("#cred", {{ opacity: .8, duration: 0.4 }}, {fim + 0.3:.3f});\n'
    if x.assinatura():
        corpo.append(f'<div class="fim-ass" id="ass">{x.assinatura()}</div>'); js += f'tl.to("#ass", {{ opacity: 1, duration: 0.4 }}, {fim + 0.5:.3f});\n'
    lg = cfg["legenda"]
    fundo = f"background:{lg['fundo']}; padding:6px 16px; box-decoration-break:clone; -webkit-box-decoration-break:clone" if lg.get("fundo") else ""
    fl = {"Maquina": "700 40px/1.3 Maquina", "Patrick Hand": "400 52px/1.2 'Patrick Hand'", "Pixel": "400 30px/1.6 Pixel", "Pixel2": "400 44px/1.3 Pixel2"}.get(lg.get("fonte"), "800 46px/1.25 Archivo")
    leg, ljs = x.legenda(f"font:{fl}; color:{lg['cor']};", lg["ativa"], fundo, topo=1440)
    corpo.append(leg); js += ljs
    return corpo, js
