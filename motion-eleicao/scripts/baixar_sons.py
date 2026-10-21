# Baixa mais efeitos sonoros do Freesound, só com licença CC0 (domínio público), usando a chave grátis da própria pessoa.
# Chave: crie em https://freesound.org/apiv2/apply (conta grátis) e salve em ~/.config/motion-eleicao/chave-freesound
# (ou na variável FREESOUND_API_KEY).
# O som baixado vai pra assets/sfx-extra/<nome>.wav e passa a valer em todos os vídeos (substitui o de mesmo nome).
# uso: python3 scripts/baixar_sons.py "<busca em inglês>" <nome>      ex.: python3 scripts/baixar_sons.py "whoosh fast" whoosh
#      python3 scripts/baixar_sons.py "<busca>" --listar            mostra as 10 primeiras opções sem baixar
import csv, json, os, sys, tempfile, urllib.parse, urllib.request
from comum import ASSETS, ff

API = "https://freesound.org/apiv2/search/text/"


def chave():
    k = os.environ.get("FREESOUND_API_KEY")
    p = os.path.join(os.path.expanduser("~"), ".config", "motion-eleicao", "chave-freesound")
    if not k and os.path.exists(p): k = open(p).read().strip()
    if not k: raise SystemExit("Falta a chave do Freesound. Crie grátis em https://freesound.org/apiv2/apply e salve em " + p)
    return k


def buscar(q):
    params = {"query": q, "filter": 'license:"Creative Commons 0" duration:[0.05 TO 6]', "sort": "rating_desc",
              "fields": "id,name,username,license,previews,url,duration", "page_size": 10, "token": chave()}
    return json.load(urllib.request.urlopen(API + "?" + urllib.parse.urlencode(params), timeout=30))["results"]


if __name__ == "__main__":
    if len(sys.argv) < 3: raise SystemExit(__doc__ or "uso: python3 scripts/baixar_sons.py \"busca\" nome")
    q, nome = sys.argv[1], sys.argv[2]
    rs = [r for r in buscar(q) if "creativecommons.org/publicdomain/zero" in r["license"]]
    if not rs: raise SystemExit("Nada CC0 com essa busca. Tente outras palavras em inglês.")
    if nome == "--listar":
        for r in rs: print(f'  {r["id"]}  {r["duration"]:.1f}s  {r["name"]}  ({r["username"]})')
        sys.exit(0)
    r = rs[0]
    pasta = os.path.join(ASSETS, "sfx-extra"); os.makedirs(pasta, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = os.path.join(tmp, "s.mp3")
        urllib.request.urlretrieve(r["previews"]["preview-hq-mp3"], mp3)
        ff("-i", mp3, "-ar", "48000", "-ac", "1", os.path.join(pasta, f"{nome}.wav"))
    cred = os.path.join(pasta, "CREDITOS.csv"); novo = not os.path.exists(cred)
    with open(cred, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novo: w.writerow(["arquivo", "id", "nome", "autor", "licenca", "url"])
        w.writerow([f"{nome}.wav", r["id"], r["name"], r["username"], "CC0", r["url"]])
    print(f'ok: {nome}.wav <- "{r["name"]}" de {r["username"]} (CC0) {r["url"]}')
