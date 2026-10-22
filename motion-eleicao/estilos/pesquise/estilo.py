# Estilo "pesquise": fundo preto, foto em retícula branca, a pergunta escrita palavra a palavra,
# palavra gigante no gancho e no fecho, lista de respostas com fonte. (Peça 8 do debate.)
from montar import br, cabe, esc

GAP, FIM, CAMA, VOL_CAMA = 0.55, 3.6, "pesquise", 0.3
CLIPE_FILTRO = "hue=s=0,eq=contrast=1.7:brightness=-0.05,noise=alls=10:allf=t"  # clipe do Flow vira P&B duro
CSS = """
#fundo { position:absolute; inset:0; background:#050505; }
.ret { position:absolute; left:50%; transform:translateX(-50%); opacity:0; }
.ret img { display:block; width:100%; }
.perg { position:absolute; left:80px; right:150px; top:1010px; text-align:center; font:300 64px/1.12 Archivo; color:#f1f1ec; letter-spacing:-0.5px; opacity:0; z-index:20; }
.perg .p { opacity:0; }
.gig { position:absolute; left:60px; right:150px; text-align:center; font:900 230px/.86 Archivo; font-stretch:75%; color:#f1f1ec; text-transform:uppercase; opacity:0; z-index:20; }
.selo { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; border:6px solid #f2c230; color:#f2c230; font:900 64px/1 Archivo; font-stretch:75%; padding:10px 22px; text-transform:uppercase; opacity:0; z-index:21; }
.fonte { position:absolute; left:80px; right:150px; text-align:center; font:700 23px Maquina; color:#8f8f88; letter-spacing:1px; opacity:0; z-index:20; }
.resp { position:absolute; left:90px; right:150px; opacity:0; z-index:20; }
.resp .n { font:300 30px Archivo; color:#9a9a92; }
.resp .q { font:300 34px/1.15 Archivo; color:#d8d8d0; }
.resp .a { font:900 58px/1 Archivo; font-stretch:75%; color:#f2c230; text-transform:uppercase; margin-top:6px; }
.resp .f { font:700 20px Maquina; color:#8f8f88; letter-spacing:1px; margin-top:6px; }
.cred { color:#77776f; }
.fim-ass { color:#9a9a92; }
"""


def cenas(x):
    c, js = ['<div id="fundo"></div>'], ""
    ult = len(x.L) - 1
    escrita = set()  # cenas em que a fala já aparece escrita na tela (sem legenda embaixo)
    for k, L in enumerate(x.L):
        cena, t0, t1 = L["c"], L["t"] - 0.1, x.fim_cena(k)
        tem_lista = bool(cena.get("lista"))
        # foto em retícula, com empurrão lento
        f = x.foto(k, "branca", 900) if not tem_lista else None
        if f:
            w = int(min(900, 680 * f["w"] / f["h"]))  # cabe numa caixa de 900 x 680
            top = 260 if k else 330
            c.append(f'<div class="ret" id="f{k}" style="top:{top}px; width:{w}px"><img src="{f["src"]}"></div>')
            js += (f'tl.set("#f{k}", {{ opacity: 1 }}, {t0:.3f}); tl.fromTo("#f{k}", {{ scale: 1 }}, {{ scale: 1.08, duration: {t1 - t0:.2f}, ease: "none" }}, {t0:.3f});\n'
                   f'tl.fromTo("#f{k}", {{ filter: "brightness(2.2)" }}, {{ filter: "brightness(1)", duration: 0.25 }}, {t0:.3f}); tl.set("#f{k}", {{ opacity: 0 }}, {t1:.3f});\n')
            x.aud("sfx/whoosh.wav", t0 - 0.15, 0.22)
        topo_txt = (top + int(w * f["h"] / f["w"]) + 70) if f else 760
        if k == ult or (k == 0 and cena.get("tela")):
            # palavra gigante (gancho ou fecho)
            txt = cena.get("tela") or cena["fala"]
            tam = cabe(txt, 260 if k == ult else 170, 1000, 0.62, 3)
            top = 380 if k == ult else topo_txt
            c.append(f'<div class="gig" id="g{k}" style="top:{top}px; font-size:{tam}px">{br(txt)}</div>')
            tb = x.bate(L, None, 0.0)
            js += f'tl.set("#g{k}", {{ opacity: 1 }}, {tb:.3f}); tl.fromTo("#g{k}", {{ scale: 1.08 }}, {{ scale: 1, duration: 0.4, ease: "power3.out" }}, {tb:.3f}); tl.set("#g{k}", {{ opacity: 0 }}, {t1:.3f});\n'
            x.aud("sfx/thump.wav", tb, 0.55)
            if k == ult and cena.get("detalhe"):
                escrita.add(k)
                c.append(f'<div class="perg" id="d{k}" style="top:1270px; font-size:56px; font-weight:400">{esc(cena["detalhe"])}</div>')
                js += f'tl.to("#d{k}", {{ opacity: 1, duration: 0.3 }}, {L["t"] + (L["fim"] - L["t"]) * 0.6:.3f});\n'
        elif tem_lista:
            for j, it in enumerate(cena["lista"]):
                top = 230 + j * min(250, 1150 // len(cena["lista"]))
                c.append(f'<div class="resp" id="r{k}-{j}" style="top:{top}px"><div class="q"><span class="n">{j + 1}.</span> {esc(it.get("q", ""))}</div>'
                         f'<div class="a">{esc(it.get("a", ""))}</div><div class="f">{esc(it.get("fonte", "")).upper()}</div></div>')
                tj = L["fim"] + 0.2 + j * 0.7
                js += f'tl.fromTo("#r{k}-{j}", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.18 }}, {tj:.3f}); tl.set("#r{k}-{j}", {{ opacity: 0 }}, {t1:.3f});\n'
                x.aud("sfx/thump.wav", tj, 0.5)
            c.append(f'<div class="gig" id="g{k}" style="top:700px; font-size:{cabe(cena.get("tela") or cena["fala"], 120, 1000, .62, 3)}px">{br(cena.get("tela") or cena["fala"])}</div>')
            js += f'tl.set("#g{k}", {{ opacity: 1 }}, {L["t"]:.3f}); tl.set("#g{k}", {{ opacity: 0 }}, {L["fim"] + 0.15:.3f});\n'
        else:
            # a fala escrita, palavra a palavra; número gigante se tiver
            if cena.get("numero"):
                c.append(f'<div class="gig" id="g{k}" style="top:{topo_txt - 30}px; font-size:{cabe(cena["numero"], 230, 1000, .55, 1)}px; color:#f2c230">{esc(cena["numero"])}</div>')
                tb = x.bate(L, cena["numero"], 0.3)
                js += f'tl.fromTo("#g{k}", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power3.out" }}, {tb:.3f}); tl.set("#g{k}", {{ opacity: 0 }}, {t1:.3f});\n'
                x.aud("sfx/thump.wav", tb, 0.5)
                topo_txt += cabe(cena["numero"], 230, 1000, .55, 1) + 30
            escrita.add(k)
            pal = " ".join(f'<span class="p">{esc(w[0])}</span>' for w in L["ws"])
            c.append(f'<div class="perg" id="q{k}" style="top:{topo_txt}px; font-size:{cabe(cena["fala"], 64, 920, .5, 4)}px">{pal}</div>')
            js += f'tl.set("#q{k}", {{ opacity: 1 }}, {L["t"] - 0.05:.3f}); tl.set("#q{k}", {{ opacity: 0 }}, {t1:.3f});\n'
            for j, w in enumerate(L["ws"]):
                js += f'tl.to("#q{k} .p:nth-child({j + 1})", {{ opacity: 1, duration: 0.18 }}, {w[1]:.3f});\n'
        if cena.get("carimbo"):
            c.append(f'<div class="selo" id="s{k}" style="top:{1380 if f else 1150}px; transform:rotate(-4deg)">{esc(cena["carimbo"])}</div>')
            tb = x.bate(L, None, 0.7)
            js += f'tl.fromTo("#s{k}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "power4.in" }}, {tb:.3f}); tl.set("#s{k}", {{ opacity: 0 }}, {t1:.3f});\n'
            x.aud("sfx/carimbo.wav", tb + 0.05, 0.6)
        if cena.get("fonte") and not tem_lista:
            c.append(f'<div class="fonte" id="o{k}" style="top:1395px">FONTE: {esc(cena["fonte"]).upper()}</div>')
            js += f'tl.to("#o{k}", {{ opacity: 1, duration: 0.3 }}, {L["t"] + 0.4:.3f}); tl.set("#o{k}", {{ opacity: 0 }}, {t1:.3f});\n'
    fim = x.L[-1]["fim"]
    c.append(f'<div class="cred" id="cred">{esc(x.creditos())}</div>')
    js += f'tl.to("#cred", {{ opacity: 1, duration: 0.4 }}, {fim + 0.3:.3f});\n'
    if x.assinatura():
        c.append(f'<div class="fim-ass" id="ass">{x.assinatura()}</div>')
        js += f'tl.to("#ass", {{ opacity: 1, duration: 0.4 }}, {fim + 0.5:.3f});\n'
    leg, ljs = x.legenda("font:700 34px/1.25 Archivo; color:#f2c230;", "#ffffff", topo=1445, extra_css="z-index:30", pular=escrita)
    c.append(leg); js += ljs
    x.aud("sfx/boom.wav", 0.0, 0.3, 4.0)
    return c, js
