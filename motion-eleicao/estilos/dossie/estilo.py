# Estilo "dossie": investigação sobre mesa escura. Pasta de arquivo, polaroide com alfinete, fichas
# datilografadas, nota com o número marcado, barbante amarelo ligando as provas, carimbo azul. (Peças 1 e 4.)
from montar import br, cabe, esc

GAP, FIM, CAMA, VOL_CAMA = 0.38, 3.4, "dossie", 0.32
CLIPE_FILTRO = "hue=s=0,eq=contrast=1.35:brightness=-0.03,noise=alls=16:allf=t"  # clipe do Flow vira P&B granulado
CSS = """
#mesa-d { position:absolute; inset:-60px; background-color:#1b1611;
  background-image:repeating-linear-gradient(91deg, rgba(255,255,255,.025) 0 2px, transparent 2px 37px), repeating-linear-gradient(89deg, rgba(0,0,0,.25) 0 5px, transparent 5px 61px); }
#pasta { position:absolute; left:40px; top:240px; width:1000px; height:1330px; background:#c9a46a; border-radius:6px 6px 10px 10px;
  background-image:repeating-linear-gradient(0deg, rgba(90,60,20,.05) 0 2px, transparent 2px 9px); box-shadow:0 30px 60px rgba(0,0,0,.6); }
#pasta:before { content:""; position:absolute; left:40px; top:-58px; width:360px; height:62px; background:#c9a46a; border-radius:12px 12px 0 0; }
#pasta .aba { position:absolute; left:70px; top:-46px; font:700 30px Maquina; color:#3a2a14; letter-spacing:2px; }
#sombra { position:absolute; inset:-200px; background:repeating-linear-gradient(115deg, rgba(0,0,0,0) 0 160px, rgba(0,0,0,.24) 160px 230px); filter:blur(16px); z-index:70; pointer-events:none; }
.etq { position:absolute; background:#efe6cf; color:#1b1b1b; font:700 30px Maquina; padding:10px 18px; box-shadow:0 6px 14px rgba(0,0,0,.45); z-index:5; }
.polar { position:absolute; background:#f4f1e8; padding:22px 22px 104px; box-shadow:0 18px 30px rgba(0,0,0,.45); z-index:3; }
.polar img { display:block; width:100%; filter:contrast(1.1) sepia(.15); }
.polar .cap { position:absolute; left:26px; right:26px; bottom:26px; font:700 40px/1.05 Maquina; color:#222; text-transform:uppercase; }
.pino { position:absolute; width:46px; height:46px; border-radius:50%; background:radial-gradient(circle at 35% 35%, #ffe27a, #d9a400 60%, #8a6a00); box-shadow:0 6px 8px rgba(0,0,0,.4); z-index:6; }
.folha { position:absolute; background:#f1ead8; color:#1b1b1b; box-shadow:0 18px 40px rgba(0,0,0,.5); padding:40px 44px; z-index:3;
  background-image:repeating-linear-gradient(0deg, transparent 0 53px, rgba(60,90,160,.13) 53px 55px); }
.folha h2 { font:700 54px/1.05 Maquina; letter-spacing:1px; border-bottom:4px solid #1b1b1b; padding-bottom:12px; margin-bottom:22px; text-transform:uppercase; }
.folha p { font:700 36px/1.45 Maquina; }
.folha .chk { display:inline-block; width:44px; color:#2c4bc9; opacity:0; }
.nota { position:absolute; background:#f4f1e8; color:#111; padding:20px 26px; font:700 40px/1.2 Maquina; box-shadow:0 10px 18px rgba(0,0,0,.35); z-index:4; }
.nota b { background:#f2c230; padding:0 10px; font-family:Archivo; font-weight:900; font-stretch:75%; }
.cita-d { position:absolute; background:#f4f1e8; color:#222; padding:26px 32px; font:44px/1.25 JornalIt; box-shadow:0 10px 18px rgba(0,0,0,.35); z-index:4; }
.cita-d small { display:block; margin-top:10px; font:700 22px Maquina; letter-spacing:1px; }
.carimbo { position:absolute; border:9px solid #2c4bc9; color:#2c4bc9; font:900 88px/1 Archivo; font-stretch:80%; padding:10px 26px; letter-spacing:4px; mix-blend-mode:multiply; opacity:0; z-index:7; text-transform:uppercase; white-space:nowrap; }
.fonte-d { position:absolute; left:90px; right:150px; font:700 25px Maquina; letter-spacing:1px; color:#2a1e10; z-index:8; }
.grande { position:absolute; left:60px; right:60px; text-align:left; font:900 150px/.9 Archivo; font-stretch:72%; color:#f4ecd8; text-transform:uppercase; text-shadow:0 8px 30px rgba(0,0,0,.6); z-index:9; }
.cred { color:#cfc4ab; }
.fim-ass { color:#efe6cf; }
"""


def cenas(x):
    c = ['<div id="mesa-d"></div>']
    chapeu = x.r.get("chapeu") or x.r.get("titulo", "")
    c.append(f'<div id="pasta"><div class="aba">ARQUIVO</div></div>')
    c.append(f'<div class="etq el" id="topo" style="left:70px; top:110px; transform:rotate(-2deg)">{esc(chapeu).upper()}</div>')
    js = 'tl.fromTo("#topo", { opacity: 0, x: -500 }, { opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }, 0.1);\n'
    js += f'tl.fromTo("#pasta, #mesa-d", {{ scale: 1.0 }}, {{ scale: 1.05, duration: {x.total:.2f}, ease: "none" }}, 0);\n'
    x.aud("sfx/papel.wav", 0.1, 0.5); x.aud("sfx/boom.wav", 0.0, 0.35, 4.0)
    ult = len(x.L) - 1
    for k, L in enumerate(x.L):
        cena, t0, t1 = L["c"], L["t"] - 0.15, x.fim_cena(k)
        sgn = 1 if k % 2 == 0 else -1
        ids = []
        if k == ult:
            # fecho: frase grande, a última linha em amarelo
            linhas = (cena.get("tela") or cena["fala"]).replace("\n", "|").split("|")
            if len(linhas) == 1:
                ws = linhas[0].split(); meio = max(1, len(ws) // 2); linhas = [" ".join(ws[:meio]), " ".join(ws[meio:])] if len(ws) > 1 else linhas
            tam = min(cabe(l, 160, 960, .5, 2) for l in linhas)
            top = 420
            for j, l in enumerate(linhas):
                cor = "#f2c230" if j == len(linhas) - 1 and len(linhas) > 1 else "#f4ecd8"
                c.append(f'<div class="grande el" id="g{j}" style="top:{top}px; font-size:{tam}px; color:{cor}">{esc(l)}</div>')
                tj = L["t"] + (L["fim"] - L["t"]) * j / max(1, len(linhas))
                js += f'tl.fromTo("#g{j}", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "power4.in" }}, {tj:.3f});\n'
                x.aud("sfx/carimbo.wav" if j == len(linhas) - 1 else "sfx/thump.wav", tj + 0.1, 0.6)
                top += int(tam * 0.95 * max(1, len(l) * tam * .5 // 960 + 1))
            js += f'tl.to("#pasta", {{ opacity: 0.25, duration: 0.3 }}, {L["t"] - 0.2:.3f});\n'
            if cena.get("detalhe"):
                c.append(f'<div class="etq el" id="dfim" style="left:90px; top:{top + 40}px; font-size:40px; transform:rotate(1.5deg)">{esc(cena["detalhe"]).upper()}</div>')
                js += f'tl.fromTo("#dfim", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.12 }}, {L["fim"] - 0.4:.3f});\n'
                x.aud("sfx/fita.wav", L["fim"] - 0.4, 0.5)
            continue
        f = x.foto(k, "pb", 760) if not cena.get("lista") else None
        y = 300
        if f:
            iw = 716; ih = int(min(620, iw * f["h"] / f["w"])); left = 160 if sgn > 0 else 140
            c.append(f'<div class="polar el" id="p{k}" style="left:{left}px; top:{y}px; width:{iw + 44}px; transform:rotate({-3 * sgn}deg)">'
                     f'<div class="pino" style="left:{iw / 2:.0f}px; top:-12px"></div><div style="height:{ih}px; overflow:hidden"><img src="{f["src"]}"></div>'
                     f'<div class="cap">{esc(cena.get("tela", ""))}</div></div>')
            js += f'tl.fromTo("#p{k}", {{ opacity: 0, y: -1400, rotation: {-12 * sgn} }}, {{ opacity: 1, y: 0, rotation: {-3 * sgn}, duration: 0.45, ease: st("back.out(1.2)", 0.45) }}, {t0:.3f});\n'
            x.aud("sfx/papel.wav", t0, 0.5)
            ids.append(f"#p{k}"); pino = (left + 22 + iw / 2, y + 10)
            y += ih + 104 + 60
        else:
            # ficha datilografada
            linhas = []
            if cena.get("detalhe"): linhas.append(f'<p>{esc(cena["detalhe"])}</p>')
            for j, it in enumerate(cena.get("lista") or []):
                linhas.append(f'<p><span class="chk" id="k{k}-{j}">✓</span>{esc(it.get("q", ""))}: {esc(it.get("a", ""))}</p>')
            c.append(f'<div class="folha el" id="p{k}" style="left:110px; top:{y}px; width:860px; min-height:560px; transform:rotate({-1.5 * sgn}deg)"><h2>{esc(cena.get("tela", "")) or "&nbsp;"}</h2>{"".join(linhas)}</div>')
            js += f'tl.fromTo("#p{k}", {{ opacity: 0, y: 900, rotation: {8 * sgn} }}, {{ opacity: 1, y: 0, rotation: {-1.5 * sgn}, duration: 0.45, ease: "power3.out" }}, {t0:.3f});\n'
            x.aud("sfx/papel.wav", t0, 0.6)
            for j, it in enumerate(cena.get("lista") or []):
                tj = L["fim"] + 0.2 + j * 0.7
                js += f'tl.fromTo("#k{k}-{j}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.12 }}, {tj:.3f});\n'; x.aud("sfx/tecla.wav", tj, 0.7)
            ids.append(f"#p{k}"); pino = None
            y += max(560, 140 + 60 * (len(linhas) + 1)) + 40
        if cena.get("numero"):
            rot = f'{esc(cena.get("detalhe", "")).upper()}<br>' if (f and cena.get("detalhe")) else ""
            tam = cabe(cena["numero"], 96, 700, .55, 1)
            nx = 520 if sgn > 0 else 120; ny = min(y - 120, 1250)
            c.append(f'<div class="nota el" id="n{k}" style="left:{nx}px; top:{ny}px; transform:rotate({3 * sgn}deg)">{rot}<b style="font-size:{tam}px">{esc(cena["numero"])}</b></div>')
            tb = x.bate(L, cena["numero"], 0.4)
            js += f'tl.fromTo("#n{k}", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.12 }}, {tb:.3f});\n'; x.aud("sfx/fita.wav", tb, 0.5)
            ids.append(f"#n{k}")
            if pino:
                bx, by = nx + 160, ny + 10
                c.append(f'<svg class="el" id="fio{k}" style="position:absolute; left:0; top:0; z-index:5" width="1080" height="1920"><path id="fiop{k}" d="M{pino[0]:.0f} {pino[1]:.0f} Q {(pino[0] + bx) / 2 + 160 * sgn:.0f} {(pino[1] + by) / 2:.0f} {bx:.0f} {by:.0f}" fill="none" stroke="#f2c230" stroke-width="6" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/></svg>')
                js += f'tl.set("#fio{k}", {{ opacity: 1 }}, {tb - 0.5:.3f}); tl.to("#fiop{k}", {{ strokeDashoffset: 0, duration: 0.5, ease: st("none", 0.5) }}, {tb - 0.5:.3f});\n'
                ids.append(f"#fio{k}")
            y = max(y, ny + tam + 120)
        elif f and cena.get("detalhe"):
            c.append(f'<div class="nota el" id="n{k}" style="left:{460 if sgn > 0 else 120}px; top:{y - 120}px; transform:rotate({2 * sgn}deg); max-width:520px; font-size:34px">{esc(cena["detalhe"])}</div>')
            js += f'tl.fromTo("#n{k}", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.12 }}, {x.bate(L, None, 0.5):.3f});\n'; ids.append(f"#n{k}")
        if cena.get("citacao"):
            quem = f'<small>{esc(cena.get("quem", "")).upper()}</small>' if cena.get("quem") else ""
            cy = min(y, 1200)
            c.append(f'<div class="cita-d el" id="q{k}" style="left:110px; top:{cy}px; width:860px; transform:rotate({-1 * sgn}deg)">“{esc(cena["citacao"])}”{quem}</div>')
            js += f'tl.fromTo("#q{k}", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: 0.14 }}, {x.bate(L, None, 0.35):.3f});\n'; x.aud("sfx/fita.wav", x.bate(L, None, 0.35), 0.4)
            ids.append(f"#q{k}")
        if cena.get("carimbo"):
            tb = x.bate(L, None, 0.75)
            c.append(f'<div class="carimbo" id="cb{k}" style="left:{300 if sgn > 0 else 200}px; top:{560}px; font-size:{cabe(cena["carimbo"], 88, 760, .6, 1)}px; transform:rotate({-12 * sgn}deg)">{esc(cena["carimbo"])}</div>')
            js += f'tl.fromTo("#cb{k}", {{ opacity: 0, scale: 2.6 }}, {{ opacity: .92, scale: 1, duration: 0.14, ease: "power4.in" }}, {tb:.3f});\n'; x.aud("sfx/carimbo.wav", tb + 0.08, 0.8)
            ids.append(f"#cb{k}")
        if cena.get("fonte"):
            c.append(f'<div class="fonte-d el" id="fo{k}" style="top:1380px">FONTE: {esc(cena["fonte"]).upper()}</div>')
            js += f'tl.to("#fo{k}", {{ opacity: 1, duration: 0.2 }}, {L["t"] + 0.6:.3f});\n'; ids.append(f"#fo{k}")
        # saída: cada cena sai pra um lado
        saida = f'x: {-1200 * sgn}, rotation: {-8 * sgn}' if k % 3 != 2 else 'y: 1500'
        js += f'tl.to("{", ".join(ids)}", {{ opacity: 0, {saida}, duration: 0.3, ease: "power2.in" }}, {t1 - 0.2:.3f});\n'
        x.aud("sfx/whoosh.wav", t1 - 0.25, 0.3)
    c.append('<div class="vinheta"></div><div id="sombra"></div>')
    js += f'tl.fromTo("#sombra", {{ x: -60 }}, {{ x: 60, duration: {x.total:.2f}, ease: "none" }}, 0);\n'
    fim = x.L[-1]["fim"]
    c.append(f'<div class="cred" id="cred">{esc(x.creditos())}</div>')
    js += f'tl.to("#cred", {{ opacity: 1, duration: 0.4 }}, {fim + 0.3:.3f});\n'
    if x.assinatura():
        c.append(f'<div class="fim-ass" id="ass">{x.assinatura()}</div>')
        js += f'tl.to("#ass", {{ opacity: 1, duration: 0.4 }}, {fim + 0.5:.3f});\n'
    leg, ljs = x.legenda('font:800 50px/1.25 Archivo; color:#111;', "#111", "background:#f4f1e8; padding:6px 16px; box-decoration-break:clone; -webkit-box-decoration-break:clone; box-shadow:6px 6px 0 #111",
                         topo=1440, ativa_prop="backgroundColor")
    leg = leg.replace('class="leg"', 'class="leg" ')
    c.append(leg); js += ljs.replace('backgroundColor: "#111"', 'backgroundColor: "#f2c230"')
    return c, js
