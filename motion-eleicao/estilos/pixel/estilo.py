# Estilo "pixel": explainer de dados em pixel art, tudo em código. Fundo grafite com grade de pixel sutil,
# ícones desenhados como grade de pixels (SVG de retângulos a partir de matrizes), fonte pixelada, número grande,
# gráfico de linha em degraus, linha do tempo com marcadores, foto pequena pixelada em moldura, linha "FONTE:" em
# verde-água, legenda com a palavra ativa em amarelo, transição de faixas coloridas em glitch, câmera dando zoom
# no detalhe e tudo andando em degrau de 12 qps. Sons 8-bit gerados em código (scripts/sons.py).
from montar import br, cabe, esc
from comum import sem_acento

GAP, FIM, CAMA, VOL_CAMA = 0.55, 3.4, "pixel", 0.16
FUNDO, VERDE, AMARELO, VERMELHO, PAPEL = "#2a2a2e", "#3fd6b0", "#f2c230", "#e0464f", "#f4f1e8"
COR = {"X": "#a8a8b0", "W": PAPEL, "K": FUNDO, "Y": AMARELO, "O": "#e8a33a", "B": "#b7793a", "G": VERDE, "R": VERMELHO, "L": "#5a5a62", "P": PAPEL}

ICONES = {
    "carrinho": ["P.............", "PP............", ".PPPPPPPPPPPP.", ".PLLLLLLLLLLP.", ".PLGLGLGLGLP..", ".PLLLLLLLLLP..", "..PLGLGLGLP...",
                 "..PPPPPPPPP...", "..P...........", "..PPPPPPPPPP..", "...YY....YY...", "...YY....YY..."],
    "documento": ["XXXXXXX...", "XWWWWWXX..", "XWWWWWXWX.", "XWKKKWXXXX", "XWWWWWWWWX", "XWKKKKKKWX", "XWWWWWWWWX", "XWKKKKKKWX",
                  "XWWWWWWWWX", "XWKKKKWWWX", "XWWWWWWWWX", "XWWWWWYYWX", "XXXXXXXXXX"],
    "bolo": ["......YY....", "....YYWWY...", "..YYWWWWWY..", "YYOOOOOOOOY.", "YBBBBBBBBBY.", "YWWWWWWWWWY.", "YBBBBBBBBBY.", "YOOOOOOOOOY.", "YYYYYYYYYYY."],
    "calendario": ["XXXXXXXXXX", "XRRRRRRRRX", "XRRRRRRRRX", "XWWWWWWWWX", "XWKWKWKWWX", "XWWWWWWWWX", "XWKWKWKWWX", "XWWWWWWWWX", "XXXXXXXXXX"],
    "moedas": ["..YYYYYY..", ".YOOOOOOY.", "..YYYYYY..", ".YOOOOOOY.", "..YYYYYY..", ".YOOOOOOY.", "..YYYYYY..", ".YOOOOOOY.", "..YYYYYY.."],
    "lupa": ["..PPPP.....", ".PGGGGP....", "PGWGGGGP...", "PGGGGGGP...", "PGGGGGGP...", ".PGGGGP....", "..PPPPPP...", "......PPP..", ".......PPP.", "........PPP", ".........P."],
    "pessoa": ["..PPP..", "..PPP..", "...P...", ".PPPPP.", "P.PPP.P", "P.PPP.P", "..PPP..", "..P.P..", "..P.P..", ".PP.PP."],
    "casa": [".....R.....", "....RRR....", "...RRRRR...", "..RRRRRRR..", ".RRRRRRRRR.", "..PPPPPPP..", "..PYPPPYP..", "..PPPLPPP..", "..PPPLPPP..", "..PPPLPPP.."],
    "urna": ["..LLLLLL....", "..LWWWWL....", "PPPPPPPPPPPP", "PXXXXXXXXXXP", "PXLLLLLLLLXP", "PXLGGGGGGLXP", "PXLLLLLLLLXP", "PXXXXXXXXXXP",
             "PXYXYXYXXXXP", "PXYXYXYXXXXP", "PPPPPPPPPPPP"],
    "predio": ["......P......", "....PPPPP....", "..PPPPPPPPP..", "PPPPPPPPPPPPP", ".P.P.P.P.P.P.", ".P.P.P.P.P.P.", ".P.P.P.P.P.P.", ".P.P.P.P.P.P.", "PPPPPPPPPPPPP", "PPPPPPPPPPPPP"],
    "cadeado": ["...PPPP...", "..P....P..", "..P....P..", "..P....P..", "PPPPPPPPPP", "PYYYYYYYYP", "PYYYKKYYYP", "PYYYKKYYYP", "PYYYYKYYYP", "PYYYYYYYYP", "PPPPPPPPPP"],
    "dinheiro": ["GGGGGGGGGGGGGG", "GWGGGGGGGGGGWG", "GGGGGWWWWGGGGG", "GGGGWGGGGWGGGG", "GGGGWGGGGWGGGG", "GGGGGWWWWGGGGG", "GWGGGGGGGGGGWG", "GGGGGGGGGGGGGG"],
    "balanca": ["......P......", ".PPPPPPPPPPP.", ".P....P....P.", "P.P...P...P.P", "P.P...P...P.P", "YYYYY.P.YYYYY", ".YYY..P..YYY.", "......P......", "......P......", "....PPPPP....", "...PPPPPPP..."],
    "alerta": [".....Y.....", "....YYY....", "....YKY....", "...YYKYY...", "...YYKYY...", "..YYYKYYY..", "..YYYYYYY..", ".YYYYKYYYY.", "YYYYYYYYYYY"],
    "cifrao": ["....G....", "..GGGGG..", ".GG.G..G.", ".GG.G....", "..GGGG...", "....GGG..", "....G.GG.", ".G..G.GG.", "..GGGGG..", "....G...."],
    "grafico": ["P.........", "P.......G.", "P.......G.", "P....Y..G.", "P....Y..G.", "P.R..Y..G.", "P.R..Y..G.", "P.R..Y..G.", "PPPPPPPPPP"],
}
# palavra da cena → ícone (quando a cena não diz "icone")
PALAVRAS = {"carrinho": "compra mercado preco inflacao cesta alimento comida feira", "documento": "lei decreto projeto documento relatorio contrato pl norma",
            "bolo": "fatia parte ganho pedaco divisao", "calendario": "ano anos dia data prazo mes vigor",
            "moedas": "dinheiro salario real reais milhoes bilhoes renda gasto", "cifrao": "custo imposto preco r$ orcamento", "lupa": "pesquisa investiga verifica confere fonte",
            "pessoa": "pessoas trabalhador desemprego emprego gente familia brasileiros", "casa": "casa moradia imovel mansao aluguel",
            "urna": "voto vota eleicao urna turno eleitor", "predio": "governo senado camara congresso ministerio prefeitura",
            "cadeado": "sigilo segredo esconder", "balanca": "justica julgamento juiz stj stf tribunal processo reu",
            "alerta": "alerta cuidado risco perigo", "grafico": "cresce caiu subiu indice taxa queda alta menor maior"}


def pixel_svg(nome, cel, cor=None):
    m = ICONES[nome]; h, w = len(m), max(len(l) for l in m)
    r = "".join(f'<rect x="{x * cel}" y="{y * cel}" width="{cel}" height="{cel}" fill="{cor if (cor and ch in "PX") else COR[ch]}"/>'
                for y, linha in enumerate(m) for x, ch in enumerate(linha) if ch != ".")
    return f'<svg width="{w * cel}" height="{h * cel}" viewBox="0 0 {w * cel} {h * cel}" shape-rendering="crispEdges">{r}</svg>', w * cel, h * cel


def icone_da_cena(c):
    if c.get("icone") in ICONES: return c["icone"]
    txt = sem_acento(" ".join(str(c.get(k, "")) for k in ("tela", "numero", "detalhe", "fala")))
    pal = set(txt.replace(",", " ").replace(".", " ").split())
    melhor = max(PALAVRAS, key=lambda k: sum(1 for p in PALAVRAS[k].split() if p in pal or (p == "r$" and "r$" in txt)))
    return melhor if any(p in pal for p in PALAVRAS[melhor].split()) else None


CSS = f"""
html, body {{ background:{FUNDO}; }}
#fundo-px {{ position:absolute; inset:0; background:{FUNDO}; }}
#fundo-px:after {{ content:""; position:absolute; inset:0; background-image:linear-gradient(rgba(255,255,255,.035) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.035) 2px, transparent 2px); background-size:24px 24px; }}
.cena-px {{ position:absolute; inset:0; opacity:0; transform-origin:50% 40%; }}
.rot-px {{ position:absolute; left:60px; right:60px; text-align:center; font:700 44px/1.2 Pixel2; color:{VERDE}; letter-spacing:3px; text-transform:uppercase; }}
.num-px {{ position:absolute; left:0; right:0; text-align:center; font:400 120px/1 Pixel; color:{PAPEL}; text-shadow:8px 8px 0 #111; white-space:nowrap; text-transform:uppercase; }}
.degrau-px {{ position:absolute; background:#4a4a52; box-shadow:inset 0 8px 0 #6a6a74; }}
.sub-px {{ position:absolute; left:80px; right:80px; text-align:center; font:400 38px/1.35 Pixel2; color:{PAPEL}; }}
.selo-px {{ position:absolute; left:0; right:0; margin:0 auto; width:fit-content; padding:16px 22px; font:400 30px/1.2 Pixel; color:{FUNDO}; background:{AMARELO}; box-shadow:8px 8px 0 #111; opacity:0; text-transform:uppercase; white-space:nowrap; }}
.fonte-px {{ position:absolute; left:90px; right:90px; top:1390px; font:400 22px/1.4 Pixel2; color:{VERDE}; letter-spacing:1px; border-left:8px solid {VERDE}; padding-left:14px; text-transform:uppercase; }}
.ic-px {{ position:absolute; }}
.ic-px svg {{ display:block; }}
.foto-px {{ position:absolute; border:12px solid {PAPEL}; box-shadow:0 0 0 6px #111, 12px 12px 0 6px #111; background:#111; }}
.foto-px img {{ display:block; width:100%; image-rendering:pixelated; }}
.foto-px .leg-f {{ position:absolute; left:-12px; right:-12px; top:100%; margin-top:18px; background:{PAPEL}; color:{FUNDO}; font:400 26px/1.3 Pixel2; padding:8px 14px; text-transform:uppercase; }}
.balao-px {{ position:absolute; left:90px; right:90px; background:{PAPEL}; color:{FUNDO}; font:400 40px/1.35 Pixel2; padding:30px 34px; box-shadow:10px 10px 0 #111; }}
.balao-px small {{ display:block; margin-top:14px; font:400 22px Pixel2; color:#555; }}
.item-px {{ position:absolute; left:90px; right:90px; background:#38383e; border:6px solid {PAPEL}; padding:16px 22px; box-shadow:8px 8px 0 #111; opacity:0; }}
.item-px .q {{ font:400 30px/1.3 Pixel2; color:{PAPEL}; }}
.item-px .a {{ font:400 34px/1.3 Pixel; color:{AMARELO}; margin-top:8px; text-transform:uppercase; }}
.item-px .f {{ font:400 18px Pixel2; color:{VERDE}; margin-top:6px; text-transform:uppercase; }}
.graf-px text {{ font-family:Pixel2; }}
.faixa-px {{ position:absolute; left:0; width:1080px; height:192px; z-index:60; transform:translateX(-1100px); }}
.fim-px {{ position:absolute; left:60px; right:60px; text-align:center; font:400 86px/1.3 Pixel; color:{PAPEL}; text-shadow:8px 8px 0 #111; }}
.cred {{ color:#8a8a92; }}
.fim-ass {{ color:{PAPEL}; font-family:Pixel2; }}
"""

JS_ANTES = """const DEGRAU = 12;
const emDegrau = (v) => { const n = Math.max(1, Math.round((v.duration ?? 0.3) * DEGRAU)), e = gsap.parseEase(v.ease || "power2.out"); return { ...v, ease: (p) => e(Math.floor(p * n) / n) }; };
const _to = tl.to.bind(tl), _from = tl.from.bind(tl), _fromTo = tl.fromTo.bind(tl);
tl.to = (t, v, p) => _to(t, emDegrau(v), p); tl.from = (t, v, p) => _from(t, emDegrau(v), p); tl.fromTo = (t, a, b, p) => _fromTo(t, a, emDegrau(b), p);
"""
FAIXAS = [VERDE, AMARELO, VERMELHO, "#1b1f3a", AMARELO, VERDE, VERMELHO, PAPEL, VERDE, AMARELO]


def grafico(k, g, top=640, alt=560):
    """linha em degraus: cada série vira uma escada; as séries vão se afastando"""
    series = g.get("series") or []
    vals = [v for s in series for v in s.get("valores", [])]
    if not vals: return "", ""
    vmax, vmin = max(vals), min(0, min(vals))
    x0, x1, y0, y1 = 140, 900, top + alt, top
    cores = [VERDE, PAPEL, AMARELO]
    svg = [f'<svg class="graf-px" id="g{k}" style="position:absolute; left:0; top:0" width="1080" height="1920" shape-rendering="crispEdges">',
           f'<rect x="{x0 - 6}" y="{y1}" width="6" height="{alt + 6}" fill="{PAPEL}"/><rect x="{x0 - 6}" y="{y0}" width="{x1 - x0 + 40}" height="6" fill="{PAPEL}"/>']
    rot = g.get("rotulos") or []
    for j, r in enumerate(rot):
        xx = x0 + (x1 - x0) * j / max(1, len(rot) - 1)
        svg.append(f'<text x="{xx:.0f}" y="{y0 + 50}" fill="{PAPEL}" font-size="26" text-anchor="middle">{esc(r)}</text>')
    for si, s in enumerate(series):
        v = s.get("valores", []); n = len(v)
        if n < 2: continue
        pts = []
        for j, val in enumerate(v):
            xx = x0 + (x1 - x0) * j / (n - 1); yy = y0 - (val - vmin) / (vmax - vmin or 1) * alt
            if pts: pts.append((xx, pts[-1][1]))
            pts.append((xx, yy))
        d = " ".join(f"{a:.0f},{b:.0f}" for a, b in pts)
        tr = 'stroke-dasharray="14 10"' if si == 1 else ""
        svg.append(f'<polyline points="{d}" fill="none" stroke="{cores[si % 3]}" stroke-width="12" {tr}/>')
        if s.get("rotulo_final"):
            svg.append(f'<text x="{x1 + 14}" y="{pts[-1][1] + 10:.0f}" fill="{cores[si % 3]}" font-size="30">{esc(s["rotulo_final"])}</text>')
        if s.get("nome"):
            svg.append(f'<rect x="{x0 + 10}" y="{y1 - 70 + si * 40}" width="26" height="26" fill="{cores[si % 3]}"/><text x="{x0 + 48}" y="{y1 - 48 + si * 40}" fill="{PAPEL}" font-size="24">{esc(s["nome"])}</text>')
    svg.append("</svg>")
    return "".join(svg), f'tl.fromTo("#g{k}", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 1.6, ease: "none" }}, {{T}});\n'


def cenas(x):
    c, js = ['<div id="fundo-px"></div>'], ""
    ult = len(x.L) - 1
    for i, cor in enumerate(FAIXAS):
        c.append(f'<div class="faixa-px" id="fx{i}" style="top:{i * 192}px; background:{cor}"></div>')

    def transicao(t0):
        j = ""
        for i in range(len(FAIXAS)):
            d = 0.04 * ((i * 7) % 5)
            j += f'tl.fromTo("#fx{i}", {{ x: -1100 }}, {{ x: 0, duration: 0.17, ease: "power2.in" }}, {t0 + d:.3f}); tl.to("#fx{i}", {{ x: 1100, duration: 0.17, ease: "power2.out" }}, {t0 + 0.26 + d:.3f});\n'
        x.aud("sfx/glitch8.wav", t0, 0.45)
        return j

    for k, L in enumerate(x.L):
        cena = L["c"]; a = max(0, L["t"] - 0.35); b = x.L[k + 1]["t"] - 0.35 if k < ult else x.total
        h = []; jk = ""
        if k > 0: js += transicao(a - 0.25)
        if k == ult:
            txt = cena.get("tela") or cena["fala"]
            h.append(f'<div class="fim-px" style="top:700px; font-size:{cabe(txt, 86, 960, 1.0, 3)}px">{br(txt)}<span id="cursor">_</span></div>')
            if cena.get("detalhe"): h.append(f'<div class="sub-px" style="top:1080px; color:{VERDE}">{esc(cena["detalhe"])}</div>')
            jk += f'for (let t = {a:.2f}; t < {x.total:.2f}; t += 0.5) tl.set("#cursor", {{ opacity: (Math.round(t * 2) % 2) ? 1 : 0 }}, +t.toFixed(2));\n'
            x.aud("sfx/bip.wav", L["t"], 0.5)
        else:
            y = 230
            if cena.get("tela"):
                h.append(f'<div class="rot-px" style="top:{y}px; font-size:{cabe(cena["tela"], 44, 960, .8, 2)}px">{esc(cena["tela"])}</div>'); y += 90
            if cena.get("numero"):
                tam = cabe(cena["numero"], 130, 960, 1.05, 1)
                h.append(f'<div class="num-px" id="n{k}" style="top:{y}px; font-size:{tam}px">{esc(cena["numero"])}</div>')
                larg_n = len(cena["numero"]) * tam * 1.0
                if 540 + larg_n / 2 + 120 < 1040 and any(w.isdigit() and len(w) == 4 and w.startswith(("19", "20")) for w in cena["fala"].replace(",", " ").replace(".", " ").split()):
                    svg_c, _, _ = pixel_svg("calendario", 10)  # ano na fala: calendarinho ao lado do número
                    h.append(f'<div class="ic-px" style="left:{540 + larg_n / 2 + 30:.0f}px; top:{y - 10}px">{svg_c}</div>')
                tn = x.bate(L, cena["numero"], 0.35)
                jk += f'tl.fromTo("#n{k}", {{ scale: 2.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25 }}, {tn:.3f});\n'
                # câmera: zoom no número quando ele bate
                jk += f'tl.to("#c{k}", {{ scale: 1.1, transformOrigin: "50% {(y + tam / 2) / 19.2:.0f}%", duration: 0.25, ease: "power2.out" }}, {tn:.3f}); tl.to("#c{k}", {{ scale: 1.0, duration: 0.4 }}, {tn + 0.9:.3f});\n'
                x.aud("sfx/moeda.wav", tn, 0.5); y += int(tam * 1.05) + 20
            if cena.get("carimbo"):
                tc = x.bate(L, None, 0.7)
                h.append(f'<div class="selo-px" id="s{k}" style="top:{y}px; font-size:{cabe(cena["carimbo"], 30, 900, 1.0, 1)}px">{esc(cena["carimbo"])}</div>')
                jk += f'tl.fromTo("#s{k}", {{ opacity: 0, scale: 1.8 }}, {{ opacity: 1, scale: 1, duration: 0.17 }}, {tc:.3f});\n'
                x.aud("sfx/vitoria.wav", tc, 0.4); y += 110
            y = max(y, 640)
            if cena.get("grade"):  # vários ícones em grade, um destacado ("1 em cada 20")
                g = cena["grade"]; ic = g.get("icone", "pessoa") if g.get("icone") in ICONES else "pessoa"
                total = max(2, min(40, int(g.get("total", 20)))); dest = max(0, min(total, int(g.get("destaque", 1))))
                col = 5 if total <= 25 else 8; lw = max(len(l) for l in ICONES[ic]); lh = len(ICONES[ic]); linhas = (total - 1) // col + 1
                cel = max(5, min(int(780 / col / (lw + 3)), int((1360 - y - 140) / linhas / (lh + 3))))
                svg_n, iw, ih = pixel_svg(ic, cel, "#8a8a90"); svg_d, _, _ = pixel_svg(ic, cel, AMARELO)
                passo_x, passo_y = 860 / col, ih + 30
                destaques = set(range(total - dest - 7, total - 7)) if dest else set()
                destaques = {i % total for i in destaques}
                for i in range(total):
                    gx = 110 + (i % col) * passo_x + (passo_x - iw) / 2; gy = y + 40 + (i // col) * passo_y
                    h.append(f'<div class="ic-px" id="p{k}-{i}" style="left:{gx:.0f}px; top:{gy:.0f}px; opacity:0">{svg_d if i in destaques else svg_n}</div>')
                    ti = L["t"] + 0.5 + i * min(0.06, 1.6 / total)
                    jk += f'tl.fromTo("#p{k}-{i}", {{ opacity: 0, y: -40 }}, {{ opacity: 1, y: 0, duration: 0.17 }}, {ti:.3f});\n'
                    if i % 4 == 0: x.aud("sfx/blip.wav", ti, 0.25)
                td = L["t"] + 0.6 + total * min(0.06, 1.6 / total) + 0.3
                for i in destaques: jk += f'tl.to("#p{k}-{i}", {{ y: -30, duration: 0.17, yoyo: true, repeat: 3 }}, {td:.3f});\n'
                x.aud("sfx/moeda.wav", td, 0.5)
                if g.get("texto"):
                    yt = y + 40 + ((total - 1) // col + 1) * passo_y + 20
                    h.append(f'<div class="sub-px" id="gt{k}" style="top:{yt:.0f}px; opacity:0">{esc(g["texto"])}</div>')
                    jk += f'tl.to("#gt{k}", {{ opacity: 1, duration: 0.17 }}, {td:.3f});\n'
            elif cena.get("escada"):  # boneco subindo a escada degrau por degrau
                base = 1240; dg = 5
                for i in range(dg):
                    h.append(f'<div class="degrau-px" style="left:{160 + i * 150}px; top:{base - i * 90}px; width:150px; height:{90 + i * 90}px"></div>')
                svg_b, bw, bh = pixel_svg("pessoa", 12, AMARELO); svg_m, _, _ = pixel_svg("moedas", 8)
                h.append(f'<div class="ic-px" id="bo{k}" style="left:{235 - bw / 2:.0f}px; top:{base - bh}px">{svg_b}</div>')
                h.append(f'<div class="ic-px" id="mo{k}" style="left:{160 + (dg - 1) * 150 + 100}px; top:{base - (dg - 1) * 90 - bh}px; opacity:0">{svg_m}</div>')
                t0e = x.bate(L, None, 0.3)
                for i in range(1, dg):
                    tt = t0e + i * 0.45
                    jk += f'tl.to("#bo{k}", {{ x: {i * 150}, y: {-i * 90}, duration: 0.25, ease: "power1.out" }}, {tt:.3f});\n'; x.aud("sfx/pulo.wav", tt, 0.35)
                tf = t0e + dg * 0.45
                jk += f'tl.fromTo("#mo{k}", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.17 }}, {tf:.3f}); tl.to("#mo{k}", {{ y: -40, duration: 0.25, yoyo: true, repeat: 1 }}, {tf + 0.2:.3f});\n'
                x.aud("sfx/moeda.wav", tf, 0.5)
                if cena.get("detalhe"): h.append(f'<div class="sub-px" style="top:{min(y, 760)}px">{esc(cena["detalhe"])}</div>')
            elif cena.get("grafico"):
                svg, jg = grafico(k, cena["grafico"], top=y + 40, alt=min(560, 1330 - y - 120))
                h.append(svg); jk += jg.replace("{T}", f"{L['t'] + 0.3:.3f}")
                for j in range(6): x.aud("sfx/blip.wav", L["t"] + 0.3 + j * 0.27, 0.25)
            elif cena.get("linha_tempo"):
                lt = cena["linha_tempo"]; yl = 1150
                h.append(f'<div style="position:absolute; left:90px; width:900px; top:{yl}px; height:10px; background:{PAPEL}"></div>')
                for j, m in enumerate(lt):
                    xm = 230 + 620 * j / max(1, len(lt) - 1); up = j % 2 == 0
                    h.append(f'<div id="m{k}-{j}" style="position:absolute; left:{xm - 20:.0f}px; top:{yl - 15}px; width:40px; height:40px; background:{AMARELO}; box-shadow:4px 4px 0 #111; opacity:0"></div>'
                             f'<div id="mt{k}-{j}" class="sub-px" style="left:{xm - 150:.0f}px; right:auto; width:300px; top:{yl - 230 if up else yl + 60}px; font-size:26px; opacity:0">'
                             f'<span style="font:400 30px Pixel; color:{AMARELO}">{esc(m.get("ano", ""))}</span><br>{esc(m.get("texto", ""))}</div>')
                    tj = L["t"] + 0.4 + j * min(0.8, (L["fim"] - L["t"]) / max(1, len(lt)))
                    jk += f'tl.fromTo("#m{k}-{j}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.17 }}, {tj:.3f}); tl.to("#mt{k}-{j}", {{ opacity: 1, duration: 0.17 }}, {tj + 0.1:.3f});\n'
                    x.aud("sfx/bip.wav", tj, 0.35)
            elif cena.get("citacao"):
                quem = f'<small>{esc(cena.get("quem", ""))}</small>' if cena.get("quem") else ""
                h.append(f'<div class="balao-px" id="q{k}" style="top:{y + 40}px">“{esc(cena["citacao"])}”{quem}</div>')
                jk += f'tl.fromTo("#q{k}", {{ clipPath: "inset(0 0 100% 0)" }}, {{ clipPath: "inset(0 0 0% 0)", duration: 0.5, ease: "steps(6)" }}, {x.bate(L, None, 0.25):.3f});\n'
                for j in range(8): x.aud("sfx/blip.wav", x.bate(L, None, 0.25) + j * 0.07, 0.25)
            elif cena.get("lista"):
                for j, it in enumerate(cena["lista"]):
                    tj = L["fim"] + 0.2 + j * 0.7
                    h.append(f'<div class="item-px" id="i{k}-{j}" style="top:{y + 20 + j * 200}px"><div class="q">{esc(it.get("q", ""))}</div><div class="a">{esc(it.get("a", ""))}</div><div class="f">FONTE: {esc(it.get("fonte", ""))}</div></div>')
                    jk += f'tl.fromTo("#i{k}-{j}", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.17 }}, {tj:.3f});\n'; x.aud("sfx/bip.wav", tj, 0.4)
            else:
                f = x.foto(k, "pixel", 640)
                if f:
                    w = 600; hh = int(w * f["h"] / f["w"])
                    if hh > 560: w = int(560 * f["w"] / f["h"]); hh = 560
                    leg_f = f'<div class="leg-f">{esc(cena["detalhe"])}</div>' if cena.get("detalhe") else ""
                    h.append(f'<div class="foto-px" id="f{k}" style="left:{540 - w / 2:.0f}px; top:{y + 30}px; width:{w}px"><img src="{f["src"]}">{leg_f}</div>')
                    jk += f'tl.fromTo("#f{k}", {{ opacity: 0, scale: .6 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }}, {L["t"] + 0.2:.3f});\n'
                    x.aud("sfx/pulo.wav", L["t"] + 0.2, 0.35)
                    cena = {**cena, "detalhe": None}
                ic = icone_da_cena(L["c"]) if not f else None
                if ic:
                    largura = max(len(l) for l in ICONES[ic])
                    svg, iw, ih = pixel_svg(ic, max(14, (320 if cena.get("numero") else 420) // largura))
                    h.append(f'<div class="ic-px" id="ic{k}" style="left:{540 - iw / 2:.0f}px; top:{y + 60}px">{svg}</div>')
                    jk += f'tl.fromTo("#ic{k}", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "back.out(2)" }}, {L["t"] + 0.25:.3f});\n'
                    jk += f'tl.to("#ic{k}", {{ y: -24, duration: 0.17, yoyo: true, repeat: 3 }}, {L["t"] + 1.0:.3f});\n'
                    x.aud("sfx/pulo.wav", L["t"] + 0.25, 0.3); y += ih + 100
                if cena.get("detalhe"):
                    h.append(f'<div class="sub-px" id="d{k}" style="top:{min(y + 30, 1300)}px; opacity:0">{esc(cena["detalhe"])}</div>')
                    jk += f'tl.to("#d{k}", {{ opacity: 1, duration: 0.17 }}, {x.bate(L, None, 0.5):.3f});\n'
            if cena.get("ressalva"):
                h.append(f'<div class="sub-px" style="top:1340px; font-size:28px; color:{AMARELO}">{esc(cena["ressalva"])}</div>')
            if cena.get("fonte"):
                h.append(f'<div class="fonte-px">FONTE: {esc(cena["fonte"])}</div>')
        c.append(f'<div class="cena-px" id="c{k}">' + "".join(h) + '</div>')
        js += f'tl.set("#c{k}", {{ opacity: 1 }}, {a:.3f}); tl.set("#c{k}", {{ opacity: 0 }}, {b:.3f});\n' + jk
    fim = x.L[-1]["fim"]
    c.append(f'<div class="cred" id="cred">{esc(x.creditos())}</div>')
    js += f'tl.to("#cred", {{ opacity: 1, duration: 0.3 }}, {fim + 0.3:.3f});\n'
    if x.assinatura():
        c.append(f'<div class="fim-ass" id="ass">{x.assinatura()}</div>'); js += f'tl.to("#ass", {{ opacity: 1, duration: 0.3 }}, {fim + 0.5:.3f});\n'
    leg, ljs = x.legenda(f"font:400 36px/1.4 Pixel2; color:{PAPEL};", AMARELO, "background:rgba(0,0,0,.55); padding:4px 12px; box-decoration-break:clone; -webkit-box-decoration-break:clone",
                         topo=1560, extra_css="z-index:50", pular={ult})
    c.append(leg); js += ljs
    return c, js
