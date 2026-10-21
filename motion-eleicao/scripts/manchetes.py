# Manchetes de matérias como "prova" na tela: lê do link só o título, a linha fina, o veículo e a data
# (metadados da página) e o estilo desenha o recorte de jornal em código. Não usa print nem a foto da matéria
# (a foto é do fotógrafo); o texto citado vai com "Reprodução: veículo, data" na tela.
# Na cena: "manchete": "https://..." ou {"url": "...", "titulo": "...", "veiculo": "...", "data": "..."} (os campos
# escritos à mão valem mais que os lidos da página; use quando o site bloquear a leitura).
# uso: python3 scripts/manchetes.py roteiro.json
import html, json, os, re, sys, urllib.request
from urllib.parse import urlparse
from comum import aviso, ler_roteiro, passo, sem_acento
from validar import ACUSA

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
VEICULOS = {"cnnbrasil": "CNN Brasil", "cartacapital": "CartaCapital", "congressoemfoco": "Congresso em Foco", "metropoles": "Metrópoles",
            "agenciabrasil": "Agência Brasil", "gov": "gov.br", "folha": "Folha de S.Paulo", "estadao": "Estadão", "oglobo": "O Globo",
            "g1": "g1", "uol": "UOL", "band": "Band", "sbtnews": "SBT News", "aosfatos": "Aos Fatos", "poder360": "Poder360",
            "correiobraziliense": "Correio Braziliense", "gazetadopovo": "Gazeta do Povo", "infomoney": "InfoMoney", "exame": "Exame",
            "agazeta": "A Gazeta", "itatiaia": "Itatiaia", "jornaldebrasilia": "Jornal de Brasília", "bahianoticias": "Bahia Notícias"}
MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def meta(pagina, *nomes):
    for n in nomes:
        for padrao in (rf'<meta[^>]+(?:property|name|itemprop)=["\']{re.escape(n)}["\'][^>]*content=["\']([^"\']+)',
                       rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name|itemprop)=["\']{re.escape(n)}["\']'):
            m = re.search(padrao, pagina, re.I)
            if m: return html.unescape(m.group(1)).strip()
    return ""


def veiculo_do_link(url):
    host = urlparse(url).netloc.lower().replace("www.", "").replace("m.", "", 1)
    for k, v in VEICULOS.items():
        if k in host.split("."): return v
    return host.split(".")[0].capitalize()


def ler(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
    pagina = urllib.request.urlopen(req, timeout=30).read(600000).decode("utf-8", "replace")
    titulo = meta(pagina, "og:title", "twitter:title") or html.unescape(re.search(r"<title>(.*?)</title>", pagina, re.S | re.I).group(1)).strip()
    titulo = re.split(r"\s+[|\-–]\s+(?=[^|\-–]{2,40}$)", titulo)[0]  # tira " | Nome do site" do fim
    linha = meta(pagina, "og:description", "description", "twitter:description")
    if titulo.endswith(("...", "…")) and linha.startswith(titulo.rstrip(".… ")): titulo, linha = linha, ""
    data = meta(pagina, "article:published_time", "datePublished", "date", "pubdate", "DC.date.issued")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", data or "")
    if not m:
        m = re.search(r'"datePublished"\s*:\s*"(\d{4})-(\d{2})-(\d{2})', pagina)
    if not m:
        m = re.search(r"/(20\d{2})[/-](\d{2})[/-](\d{2})/", url)  # muitos sites põem a data no próprio link
    data = f"{int(m.group(3))} {MES[int(m.group(2)) - 1]} {m.group(1)}" if m else ""
    # a linha fina não entra sozinha (às vezes traz frase de acusação); escreva "linha" à mão se quiser
    return {"titulo": titulo, "veiculo": meta(pagina, "og:site_name") or veiculo_do_link(url), "data": data}


def gerar(r):
    pedidas = [(i, c["manchete"]) for i, c in enumerate(r["cenas"]) if c.get("manchete")]
    if not pedidas: return {}
    passo("Manchetes (título e data das matérias)")
    pasta = os.path.join(r["_proj"], "manchetes"); os.makedirs(pasta, exist_ok=True)
    arq = os.path.join(pasta, "manchetes.json")
    feitas = json.load(open(arq, encoding="utf-8")) if os.path.exists(arq) else {}
    for i, m in pedidas:
        m = {"url": m} if isinstance(m, str) else dict(m)
        k = f"c{i}"
        if k in feitas and feitas[k].get("url") == m.get("url") and all(feitas[k].get(x) == m[x] for x in ("titulo", "veiculo", "data") if m.get(x)):
            continue
        lido = {}
        if m.get("url") and not m.get("titulo"):
            try:
                lido = ler(m["url"])
            except Exception as e:
                aviso(f'cena {i + 1}: não consegui ler a matéria ({e}). Escreva o título à mão em "manchete": {{"url", "titulo", "veiculo", "data"}}.')
                continue
        final = {**lido, **{x: m[x] for x in ("titulo", "linha", "veiculo", "data") if m.get(x)}, "url": m.get("url", "")}
        if not final.get("veiculo") and m.get("url"): final["veiculo"] = veiculo_do_link(m["url"])
        if not final.get("titulo"): aviso(f"cena {i + 1}: a matéria não tem título legível; escreva à mão."); continue
        texto = sem_acento(final["titulo"] + " " + final.get("linha", ""))
        ruim = [p for p in ACUSA + ["roubou", "matou", "assassin"] if re.search(rf"\b{p}", texto)]
        if ruim:
            aviso(f'cena {i + 1}: a manchete usa "{ruim[0]}" (acusação). Não entra; escolha outra matéria ou escreva o título à mão.')
            continue
        feitas[k] = final
        print(f'  cena {i + 1}: {final["veiculo"]}, {final.get("data", "")}: {final["titulo"][:80]}')
    json.dump(feitas, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return feitas


if __name__ == "__main__":
    if len(sys.argv) < 2: raise SystemExit("uso: python3 scripts/manchetes.py roteiro.json")
    gerar(ler_roteiro(sys.argv[1]))
