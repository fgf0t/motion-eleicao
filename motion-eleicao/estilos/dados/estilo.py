# Estilo "dados": cartões de dado sobre fundo preto com câmera 3D sutil (palco com perspectiva, camadas em
# profundidades diferentes e um sobrevoo por cena). Rótulo, número gigante, seta, selo e fonte. (Peça 9.)
from montar import br, cabe, esc, carregar_estilo
pesquise = carregar_estilo("pesquise")

GAP, FIM, CAMA, VOL_CAMA = 0.7, 3.6, "dados", 0.3
CSS = pesquise.CSS + """
.rot9 { position:absolute; left:0; right:0; text-align:center; font:700 40px Maquina; color:#9a9a92; letter-spacing:6px; opacity:0; z-index:20; text-transform:uppercase; }
.num9 { position:absolute; left:0; right:0; text-align:center; font:900 330px/1 Archivo; font-stretch:72%; color:#f1f1ec; opacity:0; z-index:20; white-space:nowrap; }
.sub9 { position:absolute; left:90px; right:90px; text-align:center; font:300 50px/1.15 Archivo; color:#e6e6df; opacity:0; z-index:20; }
.selo9 { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; border:6px solid #f2c230; color:#f2c230; font:900 60px/1 Archivo; font-stretch:75%; padding:10px 22px; white-space:nowrap; opacity:0; z-index:21; text-transform:uppercase; }
.fonte9 { position:absolute; left:60px; right:60px; text-align:center; font:700 22px Maquina; color:#8f8f88; letter-spacing:1px; opacity:0; z-index:20; }
.seta9 { position:absolute; left:0; right:0; margin:0 auto; width:120px; opacity:0; z-index:20; }
#cam3 { position:absolute; inset:0; perspective:1300px; perspective-origin:50% 45%; }
#mundo { position:absolute; inset:0; transform-style:preserve-3d; }
#mundo .ret { left:0; right:0; margin:0 auto; transform:none; }
"""
SETA = {"baixo": '<svg width="120" height="150" viewBox="0 0 120 150"><path d="M60 5 V125 M15 85 L60 135 L105 85" fill="none" stroke="#f2c230" stroke-width="16" stroke-linecap="square"/></svg>',
        "cima": '<svg width="120" height="150" viewBox="0 0 120 150"><path d="M60 145 V25 M15 65 L60 15 L105 65" fill="none" stroke="#f2c230" stroke-width="16" stroke-linecap="square"/></svg>'}


def cenas(x):
    c, js = ['<div id="fundo"></div><div id="cam3"><div id="mundo">'], ""
    n = len(x.L); ult = n - 1
    # câmera: cada cena tem um sobrevoo (gira em X/Y e avança em Z), alternando o lado
    marcas = [0.0] + [L["t"] - 0.12 for L in x.L[1:]] + [x.total]
    for i in range(len(marcas) - 1):
        a, b = marcas[i], marcas[i + 1]; s = 1 if i % 2 == 0 else -1
        js += (f'tl.fromTo("#mundo", {{ rotationX: {4 * s}, rotationY: {-7 * s}, z: -120, x: {18 * s} }}, '
               f'{{ rotationX: {-2 * s}, rotationY: {5 * s}, z: 40, x: {-12 * s}, duration: {b - a:.2f}, ease: "sine.inOut" }}, {a:.3f});\n')

    def mostra(sel, t0, t1, dur=0.25, de="y: 30"):
        eixo = de.split(":")[0]
        return f'tl.fromTo("{sel}", {{ opacity: 0, {de} }}, {{ opacity: 1, {eixo}: 0, duration: {dur} }}, {t0:.3f}); tl.set("{sel}", {{ opacity: 0 }}, {t1:.3f});\n'

    escrita = set()
    for k, L in enumerate(x.L):
        cena, ate = L["c"], x.fim_cena(k)
        if k == ult:
            txt = cena.get("tela") or cena["fala"]
            c.append(f'<div class="gig" id="g{k}" style="top:380px; font-size:{cabe(txt, 260, 1000, .62, 3)}px; line-height:.95">{br(txt)}</div>')
            tp = x.bate(L, None, 0.0)
            js += f'tl.set("#g{k}", {{ opacity: 1 }}, {tp:.3f}); tl.fromTo("#g{k}", {{ scale: 1.08 }}, {{ scale: 1, duration: 0.4, ease: "power3.out" }}, {tp:.3f});\n'
            x.aud("sfx/thump.wav", tp, 0.6)
            if cena.get("detalhe"):
                escrita.add(k)
                c.append(f'<div class="perg" id="d{k}" style="top:1290px; font-size:56px; font-weight:400">{esc(cena["detalhe"])}</div>')
                js += f'tl.to("#d{k}", {{ opacity: 1, duration: 0.3 }}, {L["t"] + (L["fim"] - L["t"]) * 0.55:.3f});\n'
            continue
        if not cena.get("numero"):
            # cena sem número: foto em retícula + a fala escrita (como no estilo pesquise)
            f = x.foto(k, "branca", 820)
            ty = 980
            if f:
                w = int(min(820, 640 * f["w"] / f["h"]))
                c.append(f'<div class="ret" id="f{k}" style="top:300px; width:{w}px"><img src="{f["src"]}"></div>')
                js += f'tl.set("#f{k}", {{ opacity: 1 }}, {L["t"] - 0.1:.3f}); tl.fromTo("#f{k}", {{ scale: 1 }}, {{ scale: 1.06, duration: {ate - L["t"] + 0.1:.2f}, ease: "none" }}, {L["t"] - 0.1:.3f}); tl.set("#f{k}", {{ opacity: 0 }}, {ate:.3f});\n'
                ty = 300 + int(w * f["h"] / f["w"]) + 70
            if cena.get("tela"):
                c.append(f'<div class="rot9" id="r{k}" style="top:{ty - 10}px">{esc(cena["tela"])}</div>')
                js += mostra(f"#r{k}", L["t"] - 0.1, ate); ty += 80
            escrita.add(k)
            pal = " ".join(f'<span class="p">{esc(w[0])}</span>' for w in L["ws"])
            tam_q = cabe(cena["fala"], 64, 920, .5, 4)
            c.append(f'<div class="perg" id="q{k}" style="top:{ty}px; font-size:{tam_q}px">{pal}</div>')
            ty += int(tam_q * 1.2 * max(1, -(-len(cena["fala"]) * tam_q * 0.56 // 900))) + 50  # depois da frase, sem encavalar
            js += f'tl.set("#q{k}", {{ opacity: 1 }}, {L["t"] - 0.05:.3f}); tl.set("#q{k}", {{ opacity: 0 }}, {ate:.3f});\n'
            for j, w in enumerate(L["ws"]): js += f'tl.to("#q{k} .p:nth-child({j + 1})", {{ opacity: 1, duration: 0.18 }}, {w[1]:.3f});\n'
            if cena.get("carimbo"):
                c.append(f'<div class="selo9" id="e{k}" style="top:{ty}px; font-size:{cabe(cena["carimbo"], 72, 900, .55, 1)}px">{esc(cena["carimbo"])}</div>')
                ty += 210  # o selo fica mais perto da câmera 3D e desce com a perspectiva
                tsel = x.bate(L, None, 0.7)
                js += f'tl.fromTo("#e{k}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.12, ease: "power4.in" }}, {tsel:.3f}); tl.set("#e{k}", {{ opacity: 0 }}, {ate:.3f});\n'
                x.aud("sfx/carimbo.wav", tsel + 0.05, 0.6)
            if cena.get("fonte"):
                c.append(f'<div class="fonte9" id="o{k}" style="top:{max(ty, 1290)}px">FONTE: {esc(cena["fonte"]).upper()}</div>')
                js += mostra(f"#o{k}", L["t"] + 0.5, ate, 0.3, "y: 0")
            continue
        # cartão de dado
        c.append(f'<div class="rot9" id="r{k}" style="top:330px">{esc(cena.get("tela", ""))}</div>')
        c.append(f'<div class="num9" id="n{k}" style="top:410px; font-size:{cabe(cena["numero"], 330, 1000, .55, 1)}px">{esc(cena["numero"])}</div>')
        js += mostra(f"#r{k}", L["t"] - 0.1, ate)
        js += f'tl.fromTo("#n{k}", {{ opacity: 0, scale: 1.25 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power3.out" }}, {L["t"]:.3f}); tl.set("#n{k}", {{ opacity: 0 }}, {ate:.3f});\n'
        x.aud("sfx/whoosh.wav", L["t"] - 0.2, 0.22); x.aud("sfx/thump.wav", L["t"] + 0.05, 0.5)
        if cena.get("seta") in SETA:
            c.append(f'<div class="seta9" id="s{k}" style="top:770px">{SETA[cena["seta"]]}</div>')
            js += mostra(f"#s{k}", L["t"] + 0.3, ate, 0.3, "y: -40" if cena["seta"] == "baixo" else "y: 40")
        if cena.get("detalhe"):
            c.append(f'<div class="sub9" id="b{k}" style="top:960px">{esc(cena["detalhe"])}</div>')
            js += mostra(f"#b{k}", L["t"] + 0.5, ate)
        tsel = x.bate(L, None, 0.7)
        if cena.get("carimbo"):
            c.append(f'<div class="selo9" id="e{k}" style="top:1110px; font-size:{cabe(cena["carimbo"], 60, 900, .55, 1)}px">{esc(cena["carimbo"])}</div>')
            js += f'tl.fromTo("#e{k}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.12, ease: "power4.in" }}, {tsel:.3f}); tl.set("#e{k}", {{ opacity: 0 }}, {ate:.3f});\n'
            x.aud("sfx/carimbo.wav", tsel + 0.05, 0.6)
        if cena.get("fonte"):
            c.append(f'<div class="fonte9" id="o{k}" style="top:1290px">FONTE: {esc(cena["fonte"]).upper()}</div>')
            js += mostra(f"#o{k}", tsel + 0.2, ate, 0.3, "y: 0")
        if cena.get("ressalva"):
            c.append(f'<div class="sub9" id="rs{k}" style="top:1370px; font-size:34px; color:#f2c230">{esc(cena["ressalva"])}</div>')
            js += mostra(f"#rs{k}", x.bate(L, None, 0.8), ate)
    # profundidades: o fundo fica atrás, o número e o selo vêm pra frente
    js += 'tl.set(".ret", { z: -120 }, 0); tl.set(".rot9", { z: 20 }, 0); tl.set(".num9", { z: 90 }, 0); tl.set(".seta9", { z: 130 }, 0); tl.set(".sub9", { z: 40 }, 0); tl.set(".selo9", { z: 160 }, 0); tl.set(".fonte9", { z: 0 }, 0); tl.set(".perg, .gig", { z: 120 }, 0);\n'
    c.append('</div></div>')  # fecha #mundo e #cam3 (legenda, créditos e assinatura ficam fora do 3D)
    fim = x.L[-1]["fim"]
    c.append(f'<div class="cred" id="cred">{esc(x.creditos())}</div>')
    js += f'tl.to("#cred", {{ opacity: 1, duration: 0.4 }}, {fim + 0.3:.3f});\n'
    if x.assinatura():
        c.append(f'<div class="fim-ass" id="ass">{x.assinatura()}</div>')
        js += f'tl.to("#ass", {{ opacity: 1, duration: 0.4 }}, {fim + 0.5:.3f});\n'
    leg, ljs = x.legenda("font:700 34px/1.25 Archivo; color:#f2c230;", "#ffffff", topo=1560, extra_css="z-index:30", pular=escrita)
    c.append(leg); js += ljs
    x.aud("sfx/boom.wav", 0.0, 0.3, 4.0)
    return c, js
