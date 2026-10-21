# Estilo "vhs": terror analógico, fita achada. Foto livre tratada como imagem de fita (P&B esverdeado,
# linhas, rasgo de tracking, piscadas, chiado), tarjas pretas, PLAY e data, texto que grita com glitch,
# corte pro preto entre as cenas. Sem sangue, sem susto barato: o medo vem do fato. (Peças 5 a 7.)
import datetime
from montar import br, cabe, esc
from comum import sem_acento

# desenhos em traço de luz pra cena sem foto (caixa 600x600): tudo objeto ou lugar neutro, sem texto nem rosto
DESENHOS = {
    "porta": "M180 560 V70 H420 V560 M205 545 V95 H395 V545 M225 120 H375 V300 H225 Z M225 330 H375 V520 H225 Z M372 318 a10 10 0 1 0 0.1 0 M60 560 H540",
    "corredor": "M0 40 L230 230 M600 40 L370 230 M0 600 L230 380 M600 600 L370 380 M230 230 H370 V380 H230 Z M60 100 L60 520 M60 100 L140 165 L140 440 L60 520 "
                "M540 100 L540 520 M540 100 L460 165 L460 440 L540 520 M250 60 H350 M262 130 H338 M275 190 H325",
    "mesa": "M80 380 H520 L560 420 H40 Z M70 420 V570 M530 420 V570 M110 420 V540 M490 420 V540 M380 380 L420 210 L330 150 M300 135 L360 135 L345 175 L315 175 Z "
            "M150 360 L270 340 L290 372 L170 392 Z M160 352 L282 332",
    "envelope": "M90 170 H510 V450 H90 Z M90 170 L300 330 L510 170 M90 450 L240 300 M510 450 L360 300",
    "cadeado": "M200 280 V200 a100 100 0 0 1 200 0 V280 M235 280 V205 a65 65 0 0 1 130 0 V280 M150 280 H450 V540 H150 Z M300 370 a28 28 0 1 0 0.1 0 M300 398 V470",
    "cracha": "M200 40 L300 230 L400 40 M240 40 L300 160 L360 40 M285 230 H315 V260 H285 Z M180 260 H420 V560 H180 Z M220 300 H380 V420 H220 Z M220 460 H380 M220 500 H330",
    "medalha": "M220 60 H380 L360 300 H240 Z M265 60 L262 300 M335 60 L338 300 M240 300 H360 V325 H240 Z M300 450 m-120 0 a120 120 0 1 0 240 0 a120 120 0 1 0 -240 0 "
               "M300 450 m-85 0 a85 85 0 1 0 170 0 a85 85 0 1 0 -170 0",
    "cartuchos": "M150 560 V300 Q150 220 190 180 Q230 220 230 300 V560 Z M150 480 H230 M260 560 V260 Q260 180 300 140 Q340 180 340 260 V560 Z M260 460 H340 "
                 "M370 560 V320 Q370 240 410 200 Q450 240 450 320 V560 Z M370 500 H450 M100 560 H500",
    "martelo": "M140 260 L320 80 L400 160 L220 340 Z M175 230 L355 50 M190 315 L370 135 M300 200 L520 420 L480 460 L260 240 M100 540 H360 V500 H140 Z",
    "predio": "M300 60 L540 170 H60 Z M80 190 H520 M80 520 H520 M60 550 H540 M120 200 V510 M200 200 V510 M260 200 V510 M340 200 V510 M400 200 V510 M480 200 V510",
    "arquivo": "M160 60 H440 V560 H160 Z M160 220 H440 M160 390 H440 M260 130 H340 V160 H260 Z M260 295 H340 V325 H260 Z M260 465 H340 V495 H260 Z",
    "relogio": "M300 300 m-220 0 a220 220 0 1 0 440 0 a220 220 0 1 0 -440 0 M300 300 V150 M300 300 L400 360 M300 100 V120 M300 480 V500 M100 300 H120 M480 300 H500",
    "urna": "M120 170 H480 V520 H120 Z M220 170 L250 110 H350 L380 170 M160 220 H330 V330 H160 Z M370 230 H440 V250 H370 Z M370 280 H440 V300 H370 Z "
            "M170 380 H210 V410 H170 Z M240 380 H280 V410 H240 Z M310 380 H350 V410 H310 Z M170 440 H210 V470 H170 Z M240 440 H280 V470 H240 Z M310 440 H350 V470 H310 Z",
    "casa": "M80 290 L300 100 L520 290 M130 250 V540 H470 V250 M260 540 V400 H340 V540 M170 320 H240 V390 H170 Z M360 320 H430 V390 H360 Z M40 540 H560",
}
PISTAS = {"porta": "porta casa entrada sigilo", "corredor": "corredor delegacia policia presidio preso cadeia", "mesa": "gabinete mesa escritorio deputado",
          "envelope": "documento carta recurso processo denuncia", "cadeado": "sigilo segredo cadeado esconder", "cracha": "mae mulher cracha funcionario trabalharam",
          "medalha": "medalha homenagem homenageado premio", "cartuchos": "bala municao tiro fuzil cartucho capsula", "martelo": "juri justica julgado stj tribunal",
          "predio": "senado assembleia congresso camara plenario", "arquivo": "arquivo arquivado caso investigacao", "relogio": "anos tempo prazo espera",
          "urna": "voto eleicao urna turno", "casa": "mansao imovel apartamento casa"}


def desenho_da_cena(c):
    if c.get("desenho") in DESENHOS: return c["desenho"]
    pal = lambda campos: set(sem_acento(" ".join(str(c.get(k, "")) for k in campos)).replace(",", " ").replace(".", " ").split())
    tela, resto = pal(("tela",)), pal(("fala", "detalhe", "carimbo"))
    pontos = {k: sum(2 * (p in tela) + (p in resto) for p in v.split()) for k, v in PISTAS.items()}  # o título da cena pesa o dobro
    k = max(pontos, key=pontos.get)
    return k if pontos[k] else "corredor"

GAP, FIM, CAMA, VOL_CAMA = 0.42, 4.2, "vhs", 0.24
CSS = """
#fundo { position:absolute; inset:0; background:#050605; }
.vhs { position:absolute; left:-40px; top:-40px; width:1160px; height:2000px; opacity:0; }
.vhs img { width:100%; height:100%; object-fit:cover; filter:grayscale(.85) contrast(1.35) brightness(.78) blur(.6px); }
#tinta { position:absolute; inset:0; background:rgba(40,90,70,.30); mix-blend-mode:color; z-index:60; pointer-events:none; }
#linhas { position:absolute; inset:0; background:repeating-linear-gradient(0deg, rgba(0,0,0,.28) 0 2px, rgba(0,0,0,0) 2px 5px); z-index:61; pointer-events:none; }
#rasgo { position:absolute; left:0; width:1080px; height:70px; background:url("assets/grao.png") center/400px; opacity:0; mix-blend-mode:screen; z-index:62; }
#apaga { position:absolute; inset:0; background:#000; opacity:0; z-index:63; pointer-events:none; }
#chiado { position:absolute; left:-40px; top:-40px; width:1160px; height:2000px; opacity:0; z-index:64; pointer-events:none; filter:contrast(1.8); }
.vcr { position:absolute; font:700 40px Maquina; color:#e9f1ea; letter-spacing:3px; text-shadow:0 0 10px rgba(200,255,220,.55), 3px 0 0 rgba(0,255,200,.35), -3px 0 0 rgba(120,255,120,.25); z-index:70; }
.grita { position:absolute; left:40px; right:40px; text-align:center; font:900 150px/.92 Archivo; font-stretch:68%; color:#f1f4ee; text-transform:uppercase; letter-spacing:2px; opacity:0;
  text-shadow:6px 0 0 rgba(0,255,210,.45), -6px 0 0 rgba(140,255,90,.35), 0 0 40px rgba(0,0,0,.9); z-index:72; }
.miud { position:absolute; left:60px; right:60px; text-align:center; font:700 34px Maquina; color:#cfe3d6; letter-spacing:4px; z-index:72; text-shadow:0 0 12px #000; opacity:0; }
.carimbo5 { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; border:9px solid #e9f1ea; color:#e9f1ea; font:900 120px/1 Archivo; font-stretch:70%; padding:10px 30px; letter-spacing:6px; z-index:72; opacity:0; text-transform:uppercase; white-space:nowrap; }
.tarja { position:absolute; left:0; width:1080px; background:#020302; z-index:66; }
.desenho { position:absolute; left:140px; top:560px; width:800px; height:800px; opacity:0; overflow:visible; }
.desenho path { fill:none; stroke:#d6f2df; stroke-width:6; stroke-linecap:round; stroke-linejoin:round; filter:drop-shadow(0 0 6px rgba(150,255,200,.55)); }
.cita5 { position:absolute; left:90px; right:90px; font:52px/1.3 JornalIt; color:#e9f1ea; z-index:72; text-shadow:0 0 16px #000; opacity:0; }
.cita5 small { display:block; font:700 26px Maquina; letter-spacing:3px; margin-top:14px; }
.cred { color:#8fa797; z-index:80; }
.fim-ass { color:#cfe3d6; z-index:80; }
"""


def cenas(x):
    c, js = ['<div id="fundo"></div>'], ""
    ult = len(x.L) - 1
    manch = {}
    for k, L in enumerate(x.L):
        m = x.manchete(k) if k < ult else None
        f = x.foto(k, "vhs") if not m else None
        ini, fim = max(0, L["t"] - 0.3), (x.fim_cena(k) + 0.12 if k < ult else x.total)
        if m:  # manchete da matéria como recorte de jornal, gravado na fita
            manch[k] = m
            c.append(x.recorte(k, m, 660, rot=-2.5 if k % 2 else 2, extra="filter:grayscale(.3) contrast(1.1);"))
            js += f'tl.set("#rj{k}", {{ opacity: 1 }}, {ini + 0.15:.3f}); tl.set("#rj{k}", {{ opacity: 0 }}, {fim:.3f});\n'
            js += f'tl.fromTo("#rj{k}", {{ scale: 1.0 }}, {{ scale: 1.07, duration: {fim - ini:.2f}, ease: "none" }}, {ini:.3f});\n'
            js += f'for (let t = {ini + 0.15:.2f}; t < {fim:.2f}; t += 1 / 12) tl.set("#rj{k}", {{ x: (rnd() - .5) * 6, y: (rnd() - .5) * 4 }}, +t.toFixed(3));\n'
        elif f:
            c.append(f'<div class="vhs" id="bg{k}"><img src="{f["src"]}"></div>')
            js += f'tl.set("#bg{k}", {{ opacity: 1 }}, {ini:.3f}); tl.set("#bg{k}", {{ opacity: 0 }}, {fim:.3f});\n'
            js += f'tl.fromTo("#bg{k}", {{ scale: 1.02 }}, {{ scale: 1.14, duration: {fim - ini:.2f}, ease: "none" }}, {ini:.3f});\n'
        elif k < ult:  # sem foto: o objeto desenhado em código, traço de luz que se desenha na fita
            d = DESENHOS[desenho_da_cena(L["c"])]
            c.append(f'<svg class="desenho" id="dz{k}" viewBox="0 0 600 600"><path class="dzp{k}" d="{d}"/></svg>')
            js += f'tl.set("#dz{k}", {{ opacity: .62 }}, {ini:.3f}); tl.set("#dz{k}", {{ opacity: 0 }}, {fim:.3f});\n'
            js += f'tl.fromTo("#dz{k}", {{ scale: 0.96 }}, {{ scale: 1.06, duration: {fim - ini:.2f}, ease: "none" }}, {ini:.3f});\n'
            js += (f'{{ const p = document.querySelector(".dzp{k}"); const n = p.getTotalLength(); p.style.strokeDasharray = n; p.style.strokeDashoffset = n; '
                   f'tl.to(p, {{ strokeDashoffset: 0, duration: 1.6, ease: "steps(20)" }}, {ini + 0.1:.3f}); }}\n')
            js += f'for (let t = {ini:.2f}; t < {fim:.2f}; t += 1 / 12) tl.set("#dz{k}", {{ x: (rnd() - .5) * 5, opacity: .5 + rnd() * .2 }}, +t.toFixed(3));\n'
    c.append('<div id="tinta"></div><div id="linhas"></div><div id="rasgo"></div>'
             '<div class="vinheta" style="background:radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 40%, rgba(0,0,0,.85) 100%)"></div>')
    c.append('<img id="chiado" src="assets/grao.png"><div id="apaga"></div>')
    c.append('<div class="tarja" style="top:0; height:200px"></div><div class="tarja" style="top:1535px; height:385px"></div>')
    data = x.r.get("data_vhs") or datetime.date.today().strftime("%d.%m.%Y")
    c.append(f'<div class="vcr" id="play" style="left:70px; top:110px">▶ PLAY</div><div class="vcr" id="data" style="left:70px; top:1570px">{esc(data)}</div>')
    fim_fita = x.L[-1]["t"]
    js += 'tl.fromTo("#play, #data", { opacity: 0 }, { opacity: 1, duration: 0.05 }, 0.2);\n'
    js += f'for (let t = 0.2; t < {fim_fita:.2f}; t += 1.0) tl.set("#play", {{ opacity: (Math.round(t) % 2) ? 1 : 0.15 }}, +t.toFixed(2));\n'
    js += f'for (let t = 0.6; t < {fim_fita - 0.3:.2f}; t += 0.7 + rnd() * 1.6) {{ tl.set("#apaga", {{ opacity: 0.25 + rnd() * 0.45 }}, +t.toFixed(3)); tl.set("#apaga", {{ opacity: 0 }}, +(t + 0.04 + rnd() * 0.08).toFixed(3)); }}\n'
    js += f'for (let t = 1.0; t < {fim_fita - 0.3:.2f}; t += 1.5 + rnd() * 2.5) {{ tl.set("#rasgo", {{ opacity: .6, y: Math.round(rnd() * 1800) }}, +t.toFixed(3)); tl.set("#rasgo", {{ opacity: 0 }}, +(t + 0.12).toFixed(3)); }}\n'

    def chiado(t, d=0.3, forte=0.75):
        x.aud("sfx/estatica.wav", t, 0.5)
        return f'tl.set("#chiado", {{ opacity: {forte} }}, {t:.3f}); tl.set("#chiado", {{ opacity: 0 }}, {t + d:.3f});\n'

    def grita(gid, txt, top, t, ate, size):
        c.append(f'<div class="grita" id="{gid}" style="top:{top}px; font-size:{size}px">{br(txt)}</div>')
        return (f'tl.set("#{gid}", {{ opacity: 1 }}, {t:.3f}); tl.fromTo("#{gid}", {{ x: -18, skewX: 8 }}, {{ x: 0, skewX: 0, duration: 0.12, ease: "steps(3)" }}, {t:.3f}); '
                f'tl.set("#{gid}", {{ opacity: 0 }}, {ate:.3f});\n')

    x.aud("sfx/boom.wav", 0.0, 0.3, 4.0)
    for k, L in enumerate(x.L):
        cena = L["c"]; t1 = x.fim_cena(k) if k < ult else L["fim"] + 0.2
        if k > 0:  # corte pro preto com chiado entre as cenas
            js += f'tl.set("#apaga", {{ opacity: 1 }}, {L["t"] - 0.32:.3f}); tl.set("#apaga", {{ opacity: 0 }}, {L["t"] - 0.08:.3f});\n' + chiado(L["t"] - 0.1, 0.15, 0.6)
        if k == ult:
            tf = L["t"]
            js += f'tl.to("#apaga", {{ opacity: 1, duration: 0.5, ease: "none" }}, {tf - 0.1:.3f}); tl.set("#play, #data, #tinta, #rasgo", {{ opacity: 0 }}, {tf + 0.4:.3f});\n'
            txt = cena.get("tela") or cena["fala"]
            c.append(f'<div class="grita" id="fim1" style="top:620px; font-size:{cabe(txt, 130, 980, .58, 3)}px; z-index:80">{br(txt)}</div>')
            js += f'tl.fromTo("#fim1", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {tf + 0.2:.3f});\n'
            if cena.get("detalhe"):
                c.append(f'<div class="miud" id="fim2" style="top:1000px; font-size:40px; z-index:80">{esc(cena["detalhe"]).upper()}</div>')
                js += f'tl.fromTo("#fim2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6 }}, {tf + (L["fim"] - tf) * 0.6:.3f});\n'
            continue
        top = 300 if k in manch else 480; y = top
        tela = cena.get("tela")
        tb = x.bate(L, None, 0.0)
        if tela:
            tam = cabe(tela, 110 if k in manch else 150, 1000, .58, 3)
            fim_tela = x.bate(L, cena.get("numero"), 0.45) - 0.05 if cena.get("numero") else t1
            js += grita(f"g{k}", tela, y, max(L["t"], tb), fim_tela, tam)
            for j in range(min(9, len(tela))): x.aud("sfx/tecla.wav", max(L["t"], tb) + j * 0.07, 0.3)
        if cena.get("numero"):
            tn = x.bate(L, cena["numero"], 0.45)
            js += grita(f"n{k}", cena["numero"], 300 if k in manch else 520, tn, t1, cabe(cena["numero"], 230, 1000, .55, 1))
            x.aud("sfx/thump.wav", tn, 0.7)
        if cena.get("carimbo"):
            tc = x.bate(L, None, 0.75)
            c.append(f'<div class="carimbo5" id="cb{k}" style="top:{1110 if k in manch else 900}px; font-size:{cabe(cena["carimbo"], 120, 900, .55, 1)}px; transform:rotate(-6deg)">{esc(cena["carimbo"])}</div>')
            js += f'tl.fromTo("#cb{k}", {{ opacity: 0, scale: 2.4 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "power4.in" }}, {tc:.3f}); tl.set("#cb{k}", {{ opacity: 0 }}, {t1:.3f});\n'
            x.aud("sfx/carimbo.wav", tc, 0.8); js += chiado(tc + 0.02, 0.1, 0.4)
        if cena.get("detalhe"):
            c.append(f'<div class="miud" id="d{k}" style="top:{230 if k in manch else 360}px">{esc(cena["detalhe"]).upper()}</div>')
            js += f'tl.set("#d{k}", {{ opacity: 1 }}, {L["t"] + 0.3:.3f}); tl.set("#d{k}", {{ opacity: 0 }}, {t1:.3f});\n'
        if cena.get("citacao"):
            quem = f'<small>{esc(cena.get("quem", "")).upper()}</small>' if cena.get("quem") else ""
            tq = x.bate(L, None, 0.3)
            if tela: js += f'tl.set("#g{k}", {{ opacity: 0 }}, {tq - 0.05:.3f});\n'
            c.append(f'<div class="cita5" id="q{k}" style="top:520px">“{esc(cena["citacao"])}”{quem}</div>')
            js += f'tl.set("#q{k}", {{ opacity: 1 }}, {tq:.3f}); tl.set("#q{k}", {{ opacity: 0 }}, {t1:.3f});\n'
            for j in range(10): x.aud("sfx/tecla.wav", tq + j * 0.08, 0.3)
        for j, it in enumerate(cena.get("lista") or []):
            tj = L["fim"] + 0.2 + j * 0.7
            c.append(f'<div class="miud" id="li{k}-{j}" style="top:{820 + j * 110}px; font-size:30px; letter-spacing:2px">{esc(it.get("q", "")).upper()}: '
                     f'<span style="color:#9dffcf">{esc(it.get("a", "")).upper()}</span><br><span style="font-size:20px">{esc(it.get("fonte", "")).upper()}</span></div>')
            js += f'tl.set("#li{k}-{j}", {{ opacity: 1 }}, {tj:.3f}); tl.set("#li{k}-{j}", {{ opacity: 0 }}, {t1:.3f});\n'; x.aud("sfx/clique.wav", tj, 0.6)
        if cena.get("fonte"):
            c.append(f'<div class="miud" id="fo{k}" style="top:1200px; font-size:24px"><span style="background:rgba(0,0,0,.7); padding:4px 12px">FONTE: {esc(cena["fonte"]).upper()}</span></div>')
            js += f'tl.set("#fo{k}", {{ opacity: .85 }}, {L["t"] + 0.5:.3f}); tl.set("#fo{k}", {{ opacity: 0 }}, {t1:.3f});\n'
    fim = x.L[-1]["fim"]
    c.append(f'<div class="cred" id="cred">{esc(x.creditos())}</div>')
    js += f'tl.to("#cred", {{ opacity: .8, duration: 0.4 }}, {fim + 0.4:.3f});\n'
    if x.assinatura():
        c.append(f'<div class="fim-ass" id="ass">{x.assinatura()}</div>')
        js += f'tl.to("#ass", {{ opacity: 1, duration: 0.4 }}, {fim + 0.6:.3f});\n'
    leg, ljs = x.legenda("font:700 40px/1.3 Maquina; color:#e9f1ea; letter-spacing:1px;", "#9dffcf",
                         "background:rgba(0,0,0,.75); padding:4px 14px; box-decoration-break:clone; -webkit-box-decoration-break:clone", topo=1330, extra_css="z-index:79")
    c.append(leg); js += ljs
    x.aud("sfx/zumbido.wav", x.L[0]["t"] + 0.2, 0.15)
    return c, js
