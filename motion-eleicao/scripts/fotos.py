# Foto de cada cena que tiver "foto", nesta ordem:
#   1) o ACERVO da skill (assets/acervo/: 7 fotos livres já conferidas e recortadas), pelo nome ("acervo:cadeado") ou por tag ("sigilo");
#   2) sem foto no acervo, a cena vai sem foto (o estilo VHS desenha o objeto em código);
#   3) Wikimedia Commons só se pedir: "commons: termo de busca", "File:Nome exato.jpg" ou "buscar_fotos": true no roteiro.
# Também aceita um arquivo seu ao lado do roteiro ("minha-foto.jpg", crédito em "foto_credito").
# Guarda autor, licença e página em <projeto>/fotos/creditos.json; os créditos vão pra tela final.
# uso: python3 scripts/fotos.py roteiro.json
import json, os, re, sys, time, urllib.parse, urllib.request, shutil
from comum import aviso, ler_roteiro, passo, sem_acento

API = "https://commons.wikimedia.org/w/api.php"
UA = "motion-eleicao/1.0 (skill de video; fotos livres com credito)"
LIVRE = re.compile(r"^(public domain|pd\b.*|cc0.*|cc[ -]by(-sa)?[ -]\d.*)$", re.I)


def api(params):
    params = {"format": "json", "action": "query", "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
              "iiurlwidth": "1600", "iiextmetadatafilter": "LicenseShortName|Artist|Credit|ObjectName|ImageDescription|Categories", **params}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    for tentativa in range(5):
        try:
            time.sleep(0.4)  # o Commons limita pedidos seguidos
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            if tentativa == 4: raise SystemExit(f"Não consegui acessar o Wikimedia Commons ({e}). Confira a internet ou espere uns minutos.")
            time.sleep(3 * (tentativa + 1))


def limpa_html(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", s).strip()[:80] or "autor desconhecido"


def candidatos(d):
    out = []
    for p in (d.get("query") or {}).get("pages", {}).values():
        if not p.get("imageinfo"): continue
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        lic = (m.get("LicenseShortName") or {}).get("value", "")
        if not LIVRE.match(lic.strip()) or ii.get("mime") not in ("image/jpeg", "image/png"): continue
        if min(ii.get("width", 0), ii.get("height", 0)) < 500: continue
        out.append(dict(titulo=p["title"].replace("File:", ""), indice=p.get("index", 0), mime=ii["mime"],
                        url=ii.get("thumburl") or ii["url"], pagina=ii.get("descriptionurl", ""),
                        autor=limpa_html((m.get("Artist") or {}).get("value")), licenca=lic.strip(),
                        contexto=sem_acento(limpa_html((m.get("ImageDescription") or {}).get("value"))),
                        categorias=sem_acento((m.get("Categories") or {}).get("value", ""))))
    return out


BRASIL = ("brazil", "brasil", "brasileir", "rio de janeiro", "sao paulo", "brasilia", "agencia brasil", "senado federal", "camara dos deputados")
CAT_BRASIL = re.compile(r"(in|of|from) brazil|(do|no|de) brasil|rio de janeiro|sao paulo|brasilia|agencia brasil")


# foto nunca pode trazer informação de outra pessoa ou de outro lugar: descarta o que citar isso
NAO_NEUTRA = re.compile(r"\b(portrait|retrato|person|people|man|woman|men|women|boy|girl|child|children|crianca|homem|mulher|"
                        r"selfie|face|rosto|politician|politico|deputad|senador|president|ministro|governor|governador|mayor|prefeito|"
                        r"homenage|honou?red|award(ed)? to|plaque|placa|sign|signage|letreiro|caption|legenda|text|texto|inscription|"
                        r"inscricao|poster|cartaz|banner|faixa|logo|logotipo|trademark|marca|watermark|newspaper|jornal|screenshot|"
                        r"protest|protesto|manifesta|rally|comicio|campaign|campanha|flag of|bandeira)\b")
OUTRO_PAIS = re.compile(r"\b(hong kong|china|chinese|japan|japanese|korea|india|indian|bangladesh|chittagong|pakistan|turkey|turkish|"
                        r"united states|usa|u\.s\.|america[n]?|canada|mexico|argentin|chile|colombia|peru|venezuela|portugal|"
                        r"spain|espanha|france|franca|germany|alemanha|italy|italia|england|united kingdom|britain|ireland|scotland|"
                        r"russia|ukraine|poland|netherlands|belgium|austria|switzerland|sweden|norway|australia|africa|nigeria|egypt|"
                        r"israel|iran|iraq|syria|indonesia|philippines|vietnam|thailand|taiwan|singapore|new york|london|paris|tokyo)\b")


def neutra(c, brasil=True):
    tudo = " ".join([sem_acento(c["titulo"]), c.get("contexto", ""), c.get("categorias", "")])
    if NAO_NEUTRA.search(tudo): return False
    if brasil and OUTRO_PAIS.search(tudo) and not e_do_brasil(c): return False
    return True


def e_do_brasil(c):
    return any(b in sem_acento(c["titulo"]) or b in c.get("contexto", "") for b in BRASIL) or bool(CAT_BRASIL.search(c.get("categorias", "")))


def buscar(termo, brasil=True):
    """com brasil=True (pauta brasileira) junta buscas com "Brazil" no termo e põe na frente o que for do Brasil"""
    if termo.startswith("File:"):
        return candidatos(api({"titles": termo}))
    palavras = [w for w in sem_acento(termo).split() if len(w) > 2]
    curto = " ".join(termo.split()[:2])
    ja_brasil = any(b in sem_acento(termo) for b in BRASIL)
    tentativas = [termo] + ([f"{termo} Brazil", f"{curto} Brazil"] if brasil and not ja_brasil else []) + [curto]
    todos = {}
    for q in tentativas:
        for c in candidatos(api({"generator": "search", "gsrnamespace": "6", "gsrlimit": "30", "gsrsearch": f"{q} filetype:bitmap"})):
            todos.setdefault(c["pagina"], c)
        if len(todos) >= 25: break

    def nota(c):
        t = sem_acento(c["titulo"])
        do_brasil = e_do_brasil(c)
        return sum(3 for w in palavras if w in t) - 0.1 * c["indice"] + (1 if c["mime"] == "image/jpeg" else 0) + (4 if brasil and do_brasil else 0)
    out = sorted([c for c in todos.values() if neutra(c, brasil)], key=nota, reverse=True)
    for c in out: c["do_brasil"] = e_do_brasil(c)
    return out


def baixar(url, destino):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(destino, "wb") as f:
        shutil.copyfileobj(r, f)


ACERVO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "acervo")


def acervo():
    p = os.path.join(ACERVO, "acervo.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []


def do_acervo(termo):
    """foto do acervo pelo nome ("acervo:urna") ou pela tag que aparece no termo ("eleição", "sigilo bancário")"""
    t = sem_acento(termo.strip()); itens = acervo()
    if t.startswith("acervo:"):
        return next((a for a in itens if a["nome"] == t[7:].strip()), None)
    palavras = set(re.findall(r"[a-z0-9$]+", t))
    for a in itens:
        for tag in a["tags"]:
            tg = sem_acento(tag)
            if tg == t or (" " in tg and tg in t) or (" " not in tg and tg in palavras): return a
    return None


def gerar(r):
    pasta = os.path.join(r["_proj"], "fotos"); os.makedirs(pasta, exist_ok=True)
    arq_cred = os.path.join(pasta, "creditos.json")
    cred = json.load(open(arq_cred, encoding="utf-8")) if os.path.exists(arq_cred) else {}
    pedidas = [(i, c["foto"].strip()) for i, c in enumerate(r["cenas"]) if c.get("foto")]
    if not pedidas: return cred
    passo("Fotos (acervo conferido da skill; Commons só se pedir)")
    usadas = {v.get("pagina") for v in cred.values()}
    for i, termo in pedidas:
        k = f"c{i}"
        if k in cred and cred[k].get("termo") == termo and os.path.exists(os.path.join(pasta, cred[k]["arquivo"])):
            continue
        local = os.path.join(r["_pasta"], termo)
        if os.path.isfile(local):
            ext = os.path.splitext(local)[1].lower() or ".jpg"
            shutil.copy(local, os.path.join(pasta, k + ext))
            cred[k] = dict(termo=termo, arquivo=k + ext, autor=r["cenas"][i].get("foto_credito", "arquivo próprio"), licenca="", pagina="")
            print(f"  cena {i + 1}: arquivo seu ({termo})"); continue
        a = do_acervo(termo)
        if a:
            shutil.copy(os.path.join(ACERVO, a["arquivo"]), os.path.join(pasta, k + ".jpg"))
            cred[k] = dict(termo=termo, arquivo=k + ".jpg", titulo=a.get("titulo", ""), autor=a["autor"], licenca=a["licenca"], pagina=a["pagina"],
                           caixa=a.get("caixa"), acervo=a["nome"])
            print(f'  cena {i + 1}: acervo "{a["nome"]}" ({a["autor"]}, {a["licenca"]})'); continue
        pedir = termo.lower().startswith(("commons:", "file:")) or r.get("buscar_fotos")
        if not pedir:
            aviso(f'cena {i + 1}: "{termo}" não está no acervo; a cena vai sem foto (no VHS, desenho em código). '
                  f'Acervo: {", ".join(x["nome"] for x in acervo())}. Pra buscar no Commons: "commons: {termo}".')
            cred.pop(k, None); continue
        termo_busca = termo[8:].strip() if termo.lower().startswith("commons:") else termo
        cs = [c for c in buscar(termo_busca, brasil=r.get("pais", "Brasil") == "Brasil") if c["pagina"] not in usadas]
        if not cs:
            aviso(f'cena {i + 1}: nada livre e neutro para "{termo}" (sem pessoa, placa, texto ou outro país). '
                  'Tente um objeto neutro (cadeado, papel, urna, mesa) ou deixe a cena sem foto.')
            continue
        c = cs[0]; ext = ".png" if c["mime"] == "image/png" else ".jpg"
        if r.get("pais", "Brasil") == "Brasil" and not c.get("do_brasil"):
            aviso(f'cena {i + 1}: a foto de "{termo}" não é marcada como do Brasil; se for um lugar, confira na folha (objeto neutro tudo bem)')
        baixar(c["url"], os.path.join(pasta, k + ext))
        cred[k] = dict(termo=termo, arquivo=k + ext, titulo=c["titulo"], autor=c["autor"], licenca=c["licenca"], pagina=c["pagina"])
        usadas.add(c["pagina"])
        print(f"  cena {i + 1}: {c['titulo'][:60]}  ({c['autor']}, {c['licenca']})")
        time.sleep(0.5)
    json.dump(cred, open(arq_cred, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    folha(r, cred, pasta)
    return cred


def folha(r, cred, pasta):
    """uma imagem com a foto de cada cena (já com o foto_corte), pra conferir antes do render"""
    from PIL import Image, ImageDraw
    itens = [(int(k[1:]), v) for k, v in cred.items() if os.path.exists(os.path.join(pasta, v["arquivo"]))]
    if not itens: return
    itens.sort(); w, h = 360, 420
    f = Image.new("RGB", (w * min(4, len(itens)), (h + 40) * ((len(itens) + 3) // 4)), (30, 30, 30)); d = ImageDraw.Draw(f)
    for n, (i, v) in enumerate(itens):
        im = Image.open(os.path.join(pasta, v["arquivo"])).convert("RGB")
        caixa = (r["cenas"][i].get("foto_corte") if i < len(r["cenas"]) else None) or v.get("caixa")
        if caixa:
            W, H = im.size; im = im.crop((int(caixa[0] * W), int(caixa[1] * H), int(caixa[2] * W), int(caixa[3] * H)))
        im.thumbnail((w - 10, h - 10)); x, y = (n % 4) * w, (n // 4) * (h + 40)
        f.paste(im, (x + 5, y + 35)); d.text((x + 8, y + 8), f"cena {i + 1}" + ("  (com foto_corte)" if caixa else ""), fill=(242, 194, 48))
    saida = os.path.join(pasta, "folha.jpg"); f.save(saida, quality=85)
    print(f"  CONFIRA AS FOTOS: {saida}")


if __name__ == "__main__":
    if len(sys.argv) < 2: raise SystemExit("uso: python3 scripts/fotos.py roteiro.json")
    gerar(ler_roteiro(sys.argv[1]))
