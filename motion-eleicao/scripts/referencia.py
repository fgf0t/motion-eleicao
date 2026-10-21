# Estilo novo a partir de referências: baixa (ou copia) as referências, tira quadros dos vídeos, mede paleta, brilho,
# textura e ritmo de corte, monta uma folha de contato pra IA olhar e deixa um rascunho do estilo em estilos/<nome>/
# (sobre.json + config.json, status "rascunho"). Depois: a IA olha a folha, ajusta o config.json, roda
# `python3 scripts/estilos.py testar <nome>`, mostra o teste e só aprova se a pessoa gostar.
# uso: python3 scripts/referencia.py <nome-novo> <referência> [<referência> ...]
#      referência = imagem ou vídeo no computador, ou link (Pinterest, Instagram, YouTube, página com imagem)
import glob, json, os, re, shutil, subprocess, sys, tempfile, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from comum import SKILL, ff, slug

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
IMG = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp")
VID = (".mp4", ".mov", ".webm", ".mkv", ".m4v")


def baixar_link(url, pasta, n):
    """tenta yt-dlp (vídeo de Instagram, YouTube, Pinterest); senão pega a og:image / og:video da página"""
    try:
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "-q", "-f", "mp4/best", "-o", os.path.join(pasta, f"ref{n}.%(ext)s"), url],
                           capture_output=True, text=True, timeout=300)
        achou = glob.glob(os.path.join(pasta, f"ref{n}.*"))
        if r.returncode == 0 and achou: return achou[0]
    except Exception:
        pass
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    dados = urllib.request.urlopen(req, timeout=30).read()
    tipo = url.lower().split("?")[0]
    if tipo.endswith(IMG + VID):
        p = os.path.join(pasta, f"ref{n}{os.path.splitext(tipo)[1]}"); open(p, "wb").write(dados); return p
    html = dados.decode("utf-8", "replace")
    for prop in ("og:video", "og:video:url", "og:image", "twitter:image"):
        m = re.search(rf'<meta[^>]+(?:property|name)=["\']{prop}["\'][^>]+content=["\']([^"\']+)', html) or \
            re.search(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{prop}["\']', html)
        if m:
            alvo = m.group(1).replace("&amp;", "&")
            ext = ".mp4" if "video" in prop else ".jpg"
            p = os.path.join(pasta, f"ref{n}{ext}")
            urllib.request.urlretrieve(alvo, p) if not alvo.startswith("//") else urllib.request.urlretrieve("https:" + alvo, p)
            return p
    raise SystemExit(f"Não consegui baixar {url}. Mande um print ou o arquivo da referência.")


def quadros_video(video, pasta, n, maximo=12):
    """um quadro a cada troca de cena (ou a cada trecho, se não houver corte), até `maximo`"""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout or 0)
    r = subprocess.run(["ffmpeg", "-i", video, "-vf", "select='gt(scene,0.3)',showinfo", "-vsync", "vfr", "-f", "null", "-"], capture_output=True, text=True, errors="replace")
    cortes = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    tempos = sorted(set([0.5] + cortes))[:maximo] if cortes else [dur * (i + .5) / maximo for i in range(maximo)]
    if len(tempos) < maximo // 2 and dur: tempos = sorted(set(tempos + [dur * (i + .5) / maximo for i in range(maximo - len(tempos))]))
    saidas = []
    for i, t in enumerate(tempos):
        p = os.path.join(pasta, f"ref{n}-q{i:02d}.jpg")
        ff("-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", "-vf", "scale=540:-2", "-q:v", "3", p); saidas.append(p)
    return saidas, (len(cortes) / dur if dur else 0), dur


def paleta(ims, k=7):
    px = np.concatenate([np.array(im.convert("RGB").resize((90, 160))).reshape(-1, 3) for im in ims]).astype(np.float32)
    rng = np.random.default_rng(1); cent = px[rng.choice(len(px), k, replace=False)]
    for _ in range(15):
        d = ((px[:, None] - cent[None]) ** 2).sum(2); lab = d.argmin(1)
        cent = np.array([px[lab == j].mean(0) if (lab == j).any() else cent[j] for j in range(k)])
    peso = np.bincount(lab, minlength=k) / len(px)
    ordem = np.argsort(-peso)
    return [("#%02x%02x%02x" % tuple(int(v) for v in cent[j]), round(float(peso[j]), 3)) for j in ordem]


def luz(h): r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5)); return 0.299 * r + 0.587 * g + 0.114 * b
def sat(h): r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5)); return max(r, g, b) - min(r, g, b)


def folha(imgs, saida):
    w, h, col = 270, 480, 6
    linhas = (len(imgs) + col - 1) // col
    f = Image.new("RGB", (w * min(col, len(imgs)), h * linhas), (30, 30, 30))
    for i, p in enumerate(imgs):
        im = Image.open(p).convert("RGB"); im.thumbnail((w, h)); f.paste(im, ((i % col) * w + (w - im.width) // 2, (i // col) * h + (h - im.height) // 2))
    f.save(saida, quality=85)


def main():
    if len(sys.argv) < 3: raise SystemExit("uso: python3 scripts/referencia.py <nome-novo> <referência> [...]")
    nome = slug(sys.argv[1]); pasta = os.path.join(SKILL, "estilos", nome)
    if os.path.exists(os.path.join(pasta, "estilo.py")): raise SystemExit(f'"{nome}" já é um estilo pronto. Escolha outro nome.')
    refs = os.path.join(pasta, "referencias"); os.makedirs(refs, exist_ok=True)
    quadros, ritmo, durs = [], [], []
    for n, r in enumerate(sys.argv[2:]):
        arq = r if os.path.exists(r) else baixar_link(r, refs, n)
        if os.path.exists(r): arq = shutil.copy(r, os.path.join(refs, f"ref{n}{os.path.splitext(r)[1].lower()}"))
        if arq.lower().endswith(VID):
            q, cps, d = quadros_video(arq, refs, n); quadros += q; ritmo.append(cps); durs.append(d)
        else:
            p = os.path.join(refs, f"ref{n}-q00.jpg"); Image.open(arq).convert("RGB").save(p, quality=90); quadros.append(p)
    ims = [Image.open(p) for p in quadros]
    pal = paleta(ims)
    # textura: energia de alta frequência (grão/papel) e linhas horizontais (scanlines)
    g = np.array(ims[0].convert("L").resize((540, 960))).astype(np.float32)
    grao = float(np.abs(g - np.array(Image.fromarray(g.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)))).mean())
    fundo = max(pal, key=lambda c: c[1])[0]
    destaque = max([c for c in pal if c[0] != fundo and c[1] >= 0.02] or pal[1:], key=lambda c: sat(c[0]))[0]  # a cor mais viva, mesmo se ocupa pouco
    apoio = max([c for c in pal if c[0] not in (fundo, destaque)], key=lambda c: sat(c[0]))[0]
    escuro = luz(fundo) < 110
    texto = max(pal, key=lambda c: luz(c[0]))[0] if escuro else min(pal, key=lambda c: luz(c[0]))[0]
    cps = float(np.mean(ritmo)) if ritmo else 0.0
    analise = {"quadros": [os.path.relpath(p, pasta) for p in quadros], "paleta": pal, "fundo_provavel": fundo, "destaque_provavel": destaque,
               "fundo_escuro": escuro, "grao": round(grao, 2), "cortes_por_segundo": round(cps, 2), "duracao_videos": durs}
    json.dump(analise, open(os.path.join(pasta, "analise.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    folha(quadros, os.path.join(pasta, "folha.jpg"))
    cfg = {"fundo": {"cor": fundo, "cor2": apoio if not escuro else "rgba(255,255,255,.06)", "textura": "papel" if (grao > 6 and not escuro) else ("grao" if grao > 4 else "nenhuma")},
           "paleta": {"texto": texto, "destaque": destaque, "apoio": apoio, "papel": "#f4f1e8" if escuro else "#ffffff", "fonte": destaque},
           "fonte_titulo": "Archivo", "titulo_caixa_alta": True, "fonte_texto": "Archivo",
           "foto": {"modo": "pb", "moldura": "borda", "posicao": "topo"},
           "entrada": "corte" if cps > 0.8 else ("pop" if cps > 0.3 else "desliza"), "transicao": "faixas" if cps > 0.8 else "corte",
           "movimento_degrau": True, "efeitos": ["grao", "vinheta"] if grao > 4 else ["vinheta"],
           "legenda": {"cor": texto, "ativa": destaque, "fundo": "rgba(0,0,0,.55)" if escuro else "rgba(255,255,255,.85)", "fonte": "Archivo"},
           "carimbo": {"cor": destaque, "forma": "faixa"}, "cama": "dados" if escuro else "leve"}
    if not os.path.exists(os.path.join(pasta, "config.json")):
        json.dump(cfg, open(os.path.join(pasta, "config.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not os.path.exists(os.path.join(pasta, "sobre.json")):
        json.dump({"nome": nome, "titulo": sys.argv[1], "quando": "(preencher)", "descricao": "(preencher: 1 frase sobre a cara do estilo)",
                   "status": "rascunho", "origem": "referencia"}, open(os.path.join(pasta, "sobre.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"""
Referências analisadas: {len(quadros)} quadros em {refs}
Folha de contato (OLHE ESTA IMAGEM): {os.path.join(pasta, 'folha.jpg')}
Paleta: {", ".join(f"{c} ({p:.0%})" for c, p in pal)}
Fundo provável: {fundo} ({"escuro" if escuro else "claro"}) · destaque: {destaque} · grão: {grao:.1f} · cortes por segundo: {cps:.2f}

Rascunho criado: {os.path.join(pasta, 'config.json')} e sobre.json (status rascunho).
Próximo passo: olhe a folha, ajuste o config.json (opções em estilos/_base/config-modelo.json) e preencha o sobre.json;
depois rode: python3 scripts/estilos.py testar {nome}""")


if __name__ == "__main__":
    main()
