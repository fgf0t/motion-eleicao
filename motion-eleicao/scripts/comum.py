# Coisas que todos os scripts usam: caminhos, leitura do roteiro, ffmpeg, áudio.
import json, os, re, shutil, subprocess, sys, unicodedata, wave
import numpy as np

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL, "assets")
HYPERFRAMES = "hyperframes@0.8.172"


def estilos(rascunhos=False):
    """estilos do cardápio: cada pasta em estilos/ com sobre.json (os rascunhos só entram se pedir)"""
    out = []
    raiz = os.path.join(SKILL, "estilos")
    for nome in sorted(os.listdir(raiz)):
        p = os.path.join(raiz, nome, "sobre.json")
        if nome.startswith(("_", ".")) or not os.path.exists(p): continue
        s = json.load(open(p, encoding="utf-8")); s["pasta"] = os.path.join(raiz, nome)
        if s.get("status") == "pronto" or rascunhos: out.append(s)
    return out
SR = 48000


def aviso(msg): print(f"  ! {msg}", flush=True)
def passo(msg): print(f"\n== {msg}", flush=True)


def ff(*a):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *a], capture_output=True, text=True, errors="replace")
    if r.returncode:
        raise SystemExit(f"ffmpeg falhou: {r.stderr.strip()[:600]}")


def ler_roteiro(caminho):
    caminho = os.path.abspath(caminho)
    try:
        r = json.load(open(caminho, encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"O roteiro não é um JSON válido: {e}")
    if not r.get("voz"):  # sem voz no roteiro: usa a escolhida com scripts/voz_propria.py salvar
        cfg = os.path.join(os.path.expanduser("~"), ".config", "motion-eleicao", "voz.json")
        r["voz"] = json.load(open(cfg)) if os.path.exists(cfg) else {"motor": "auto"}  # auto: Narrador Grave, Kokoro ou sistema
    r["_arquivo"] = caminho
    r["_pasta"] = os.path.dirname(caminho)
    nome = r.get("titulo") or os.path.splitext(os.path.basename(caminho))[0]
    r["_nome"] = slug(nome)
    r["_proj"] = os.path.join(r["_pasta"], f"{r['_nome']}-projeto")
    return r


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "video"


def sem_acento(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def ler_wav(p):
    w = wave.open(p)
    sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
    a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    if ch > 1: a = a.reshape(-1, ch).mean(axis=1)
    return a, sr


def salvar_wav(p, a, sr=SR):
    a = np.clip(a, -1, 1)
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((a * 32767).astype(np.int16).tobytes()); w.close()


def duracao_wav(p):
    w = wave.open(p); return w.getnframes() / w.getframerate()


def duracao_video(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def cmd_npx():
    for n in ("npx", "npx.cmd"):
        c = shutil.which(n)
        if c: return c
    raise SystemExit("Não achei o npx (Node.js). Rode o instalador da skill de novo.")


def windows(): return sys.platform.startswith("win")
def mac(): return sys.platform == "darwin"


# ---------- números por extenso (as vozes neurais erram algarismo: "2012" sai "2020") ----------
_UN = "zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete dezoito dezenove".split()
_DEZ = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
_CEM = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"]


def extenso(n):
    n = int(n)
    if n < 20: return _UN[n]
    if n < 100: return _DEZ[n // 10] + ("" if n % 10 == 0 else " e " + _UN[n % 10])
    if n == 100: return "cem"
    if n < 1000: return _CEM[n // 100] + ("" if n % 100 == 0 else " e " + extenso(n % 100))
    if n < 1000000:
        m, r = divmod(n, 1000)
        cab = "mil" if m == 1 else extenso(m) + " mil"
        if r == 0: return cab
        return cab + (" e " if r < 100 or r % 100 == 0 else " ") + extenso(r)
    m, r = divmod(n, 1000000)
    cab = ("um milhão" if m == 1 else extenso(m) + " milhões")
    return cab if r == 0 else cab + " e " + extenso(r)


def por_extenso(texto):
    """troca algarismos por palavras: 2012, 5,1%, R$ 6 mil, 8,7 milhões, 1º"""
    t = re.sub(r"(\d)\s*mi\b", r"\1 milhões", texto); t = re.sub(r"(\d)\s*bi\b", r"\1 bilhões", t)

    def reais(m):
        mult = m.group(2) or ""
        return m.group(1) + mult + (" de reais" if re.search(r"milh|bilh", mult) else " reais")
    t = re.sub(r"R\$\s*([\d.]+(?:,\d+)?)(\s+(?:milhões|milhão|bilhões|bilhão|mil)\b)?", reais, t)
    t = re.sub(r"(\d+)º", lambda m: {"1": "primeiro", "2": "segundo", "3": "terceiro"}.get(m.group(1), extenso(m.group(1)) + "º"), t)

    def num(m):
        inteiro, dec = m.group(1).replace(".", ""), m.group(2)
        s = extenso(inteiro)
        if dec: s += " vírgula " + (" ".join(_UN[int(d)] for d in dec) if dec.startswith("0") or len(dec) > 2 else extenso(dec))
        return s + (" por cento" if m.group(3) else "")
    return re.sub(r"(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?:\s*(%))?", num, t)
