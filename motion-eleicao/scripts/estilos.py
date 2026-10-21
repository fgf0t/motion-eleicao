# Cardápio de estilos: lista, galeria com quadro de exemplo, boas-vindas, teste e aprovação de estilo novo.
# uso: python3 scripts/estilos.py                     lista os estilos (nome, quando usar, descrição, imagem de exemplo)
#      python3 scripts/estilos.py galeria             monta estilos/galeria.jpg com o quadro de exemplo de cada estilo
#      python3 scripts/estilos.py pautas              lista as pautas prontas (fatos já checados) em pautas/
#      python3 scripts/estilos.py boas-vindas         texto de boas-vindas + cardápio (mostrar na primeira vez)
#      python3 scripts/estilos.py primeira-vez        imprime as boas-vindas só se ainda não foram mostradas
#      python3 scripts/estilos.py testar <nome>       renderiza um teste curto do estilo (teste.mp4 + exemplo.jpg)
#      python3 scripts/estilos.py aprovar <nome>      põe o estilo no cardápio (depois que a pessoa aprovar o teste)
#      python3 scripts/estilos.py exemplo <nome> <video.mp4 ou pasta do projeto> <segundo>   troca o quadro de exemplo
import json, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
from comum import ASSETS, HYPERFRAMES, SKILL, cmd_npx, estilos, ff

MARCA = os.path.join(os.path.expanduser("~"), ".config", "motion-eleicao", "boas-vindas-mostradas")
TESTE = {  # roteiro curto e neutro pra testar um estilo novo (os fatos são os dos exemplos, com fonte)
    "titulo": "teste do estilo", "voz": {"motor": "sistema", "velocidade": 1.05},
    "cenas": [
        {"fala": "Três números pra você levar pra urna.", "tela": "3 números", "foto": "acervo:urna"},
        {"fala": "O desemprego fechou 2025 em 5,1%, o menor desde 2012.", "tela": "Desemprego", "numero": "5,1%", "carimbo": "menor desde 2012",
         "fonte": "IBGE, PNAD Contínua", "foto": "acervo:mapa", "bate": "menor"},
        {"fala": "Não acredita? Pesquisa.", "tela": "Pesquisa", "detalhe": "confira as fontes"}]}


def lista(rascunhos=False):
    es = estilos(rascunhos)
    for e in es:
        ex = os.path.join(e["pasta"], "exemplo.jpg")
        marca = "" if e.get("status") == "pronto" else "  [RASCUNHO, ainda não aprovado]"
        print(f'\n{e["nome"]}  ·  {e["titulo"]}{marca}\n  quando usar: {e["quando"]}\n  {e["descricao"]}')
        print(f'  exemplo: {ex if os.path.exists(ex) else "(sem imagem ainda)"}')
    g = os.path.join(SKILL, "estilos", "galeria.jpg")
    if os.path.exists(g): print(f"\nTodos lado a lado: {g}")


def pautas():
    raiz = os.path.join(SKILL, "pautas")
    if not os.path.isdir(raiz): return
    print("Pautas prontas (fatos checados em 19-20/10/2026; confira o fatos.md de cada uma antes de postar):")
    for n in sorted(os.listdir(raiz)):
        p = os.path.join(raiz, n, "sobre.json")
        if os.path.exists(p):
            s = json.load(open(p, encoding="utf-8"))
            print(f'  {n}  ({s.get("estilo_sugerido", "")}): {s.get("resumo", "")}')


def galeria():
    es = [e for e in estilos() if os.path.exists(os.path.join(e["pasta"], "exemplo.jpg"))]
    if not es: return None
    w, h, cab = 360, 640, 70
    folha = Image.new("RGB", (w * len(es), h + cab), (24, 24, 26)); d = ImageDraw.Draw(folha)
    fonte = ImageFont.truetype(os.path.join(ASSETS, "fonts", "Archivo.ttf"), 34)
    for i, e in enumerate(es):
        im = Image.open(os.path.join(e["pasta"], "exemplo.jpg")).convert("RGB").resize((w - 8, h - 8))
        folha.paste(im, (i * w + 4, cab))
        d.text((i * w + 14, 16), e["nome"], fill=(242, 194, 48), font=fonte)
    saida = os.path.join(SKILL, "estilos", "galeria.jpg"); folha.save(saida, quality=88)
    return saida


def boas_vindas(marcar=True):
    print("""
Oi! Esta skill faz vídeo motion 9:16 sobre a eleição (Reels, TikTok, Shorts) a partir de uma pauta.

COMO PEDIR
  "faz um vídeo sobre <pauta> no estilo <estilo>"
  ex.: "faz um vídeo sobre a queda do desemprego no estilo dados"
  Se você já tiver as fontes, mande junto. Se não, eu pesquiso e mostro de onde veio cada número.

QUANTO TEMPO
  Uns 3 a 6 minutos por vídeo de 30 a 45 segundos (a maior parte é o render).

O QUE É GRÁTIS
  Tudo: voz, fotos de licença livre do Wikimedia Commons com crédito na tela, animação, trilha e efeitos sonoros
  feitos em código. Nada é pago por vídeo.

VOZ
  Começa com a voz padrão da skill (Narrador Grave, ou a Kokoro se você não tiver o VoiceStudio).
  Mas fica bem melhor com a SUA voz:
  soa mais natural e passa mais confiança pra quem assiste. É grátis e eu te ensino passo a passo
  (instalar o VoiceStudio, gravar 30 segundos, ouvir um teste). É só pedir "quero usar a minha voz".

REGRAS
  Todo fato com fonte. Ninguém é chamado de criminoso sem condenação. A tela final avisa que a voz é sintética.
  Não é pra impulsionar (pagar pra promover).

PAUTAS PRONTAS
  Já tem pautas com os fatos checados e as fontes, prontas pra virar vídeo. Escolha uma ou mande a sua.

ESTILO NOVO
  Mande uma referência (imagem, print, link do Pinterest, Instagram ou YouTube) e diga "cria um estilo assim".
  Eu analiso, monto o estilo, renderizo um teste curto e ele só entra no cardápio quando você aprovar.

ESTILOS""")
    lista()
    print()
    pautas()
    if marcar:
        os.makedirs(os.path.dirname(MARCA), exist_ok=True); open(MARCA, "w").write("ok")


def testar(nome):
    pasta = os.path.join(SKILL, "estilos", nome)
    if not os.path.isdir(pasta): raise SystemExit(f"Não existe a pasta estilos/{nome}")
    t = os.path.join(pasta, "teste"); os.makedirs(t, exist_ok=True)
    rot = dict(TESTE, estilo=nome); json.dump(rot, open(os.path.join(t, "roteiro.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, os.path.join(SKILL, "scripts", "fazer.py"), os.path.join(t, "roteiro.json")])
    if r.returncode: raise SystemExit("O teste falhou (veja a mensagem acima).")
    video = os.path.join(t, "teste-do-estilo.mp4")
    shutil.copy(video, os.path.join(pasta, "teste.mp4"))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout or 10)
    exemplo(nome, video, dur * 0.45)
    print(f"\nTESTE: {os.path.join(pasta, 'teste.mp4')}\nQUADRO: {os.path.join(pasta, 'exemplo.jpg')}\n"
          f"Mostre pra pessoa. Se ela aprovar: python3 scripts/estilos.py aprovar {nome}")


def exemplo(nome, origem, seg):
    saida = os.path.join(SKILL, "estilos", nome, "exemplo.jpg")
    if os.path.isdir(origem):  # pasta de projeto HyperFrames: tira o quadro pelo próprio motor
        tmp = os.path.join(origem, ".quadro")
        subprocess.run([cmd_npx(), "--yes", HYPERFRAMES, "snapshot", origem, "-o", tmp, "--at", f"{float(seg):.2f}", "--no-end"], capture_output=True)
        png = [f for f in os.listdir(tmp) if f.endswith(".png")][0]
        Image.open(os.path.join(tmp, png)).convert("RGB").resize((540, 960), Image.LANCZOS).save(saida, quality=90)
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        ff("-ss", f"{float(seg):.2f}", "-i", origem, "-frames:v", "1", "-vf", "scale=540:960", "-q:v", "3", saida)
    galeria()
    print("ok", saida)


def aprovar(nome):
    p = os.path.join(SKILL, "estilos", nome, "sobre.json")
    s = json.load(open(p, encoding="utf-8")); s["status"] = "pronto"
    json.dump(s, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    shutil.rmtree(os.path.join(SKILL, "estilos", nome, "teste"), ignore_errors=True)
    galeria(); print(f'"{nome}" entrou no cardápio.')


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: lista(rascunhos=True)
    elif a[0] == "galeria": print(galeria())
    elif a[0] == "pautas": pautas()
    elif a[0] == "boas-vindas": boas_vindas(marcar="--instalador" not in a)
    elif a[0] == "primeira-vez":
        if not os.path.exists(MARCA): boas_vindas()
    elif a[0] == "testar": testar(a[1])
    elif a[0] == "aprovar": aprovar(a[1])
    elif a[0] == "exemplo": exemplo(a[1], a[2], a[3])
    else: raise SystemExit("comando desconhecido; veja o começo de scripts/estilos.py")
