# Confere que nenhuma fala foi cortada: transcreve o áudio FINAL de cada cena (depois de todos os cortes) e compara
# com o texto pedido, primeira e última palavra incluídas, e mede a folga depois da última palavra.
# Transcritor, na ordem: faster-whisper no ambiente das vozes (instalador), mlx_whisper (Mac), nenhum (só avisa).
import difflib, json, os, re, shutil, subprocess
from comum import sem_acento, windows

VENV = os.path.join(os.path.expanduser("~"), ".config", "motion-eleicao", "vozes-venv")
FOLGA = 0.25  # segundos que sobram depois da última palavra


def py_venv():
    p = os.path.join(VENV, "Scripts", "python.exe") if windows() else os.path.join(VENV, "bin", "python")
    if not os.path.exists(p): return None
    r = subprocess.run([p, "-c", "import faster_whisper"], capture_output=True)
    return p if r.returncode == 0 else None


def transcrever(wavs):
    """lista de {"palavras": [[palavra, ini, fim]], "duracao": s} na mesma ordem, ou None se não houver transcritor"""
    py = py_venv()
    if py:
        r = subprocess.run([py, os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcrever_local.py"), *wavs],
                           capture_output=True, text=True, errors="replace")
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout.strip().splitlines()[-1])
    mlx = shutil.which("mlx_whisper")
    if mlx:
        import tempfile, wave
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            for w in wavs:
                subprocess.run([mlx, w, "--language", "pt", "--word-timestamps", "True", "--output-dir", tmp, "--output-format", "json"],
                               capture_output=True)
                j = os.path.join(tmp, os.path.splitext(os.path.basename(w))[0] + ".json")
                if not os.path.exists(j): return None
                d = json.load(open(j))
                ww = wave.open(w); dur = ww.getnframes() / ww.getframerate(); ww.close()
                out.append({"duracao": dur, "palavras": [[x["word"].strip(), x["start"], x["end"]] for s in d["segments"] for x in s.get("words", [])]})
        return out
    return None


def tokens(t):
    from comum import por_extenso
    return re.findall(r"[a-z]+", sem_acento(por_extenso(t)))  # número vira palavra dos dois lados: "2012" = "dois mil e doze"


def parecido(a, b):
    if not a or not b: return False
    if a == b or a.startswith(b) or b.startswith(a): return True
    if a.isdigit() or b.isdigit(): return a.isdigit() and b.isdigit() and (a in b or b in a)
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.6


VICIOS = {"e", "eh", "ah", "hum", "uh", "hm"}


def julgar(texto, trans):
    """(ok, motivo, onde): onde = comeco (falta palavra), vicio (sobrou um "É" antes), fim (falta palavra ou folga) ou meio"""
    esp = tokens(texto); ouv = [t for w in trans["palavras"] for t in tokens(w[0])]
    if not ouv: return False, "não ouvi nada", "meio"
    if not esp: return True, "", ""
    inicio = any(parecido(esp[0], o) for o in ouv[:3])
    fim = any(parecido(esp[-1], o) for o in ouv[-3:])
    sim = difflib.SequenceMatcher(None, esp, ouv).ratio()
    ultima = trans["palavras"][-1][2]
    folga = trans["duracao"] - ultima
    if not inicio: return False, f'falta o começo (pedi "{esp[0]}", ouvi "{" ".join(ouv[:3])}")', "comeco"
    if ouv[0] in VICIOS and not parecido(esp[0], ouv[0]): return False, 'sobrou um "É" antes da primeira palavra', "vicio"
    if not fim: return False, f'falta o fim (pedi "{esp[-1]}", ouvi "{" ".join(ouv[-3:])}")', "fim"
    if sim < 0.5: return False, f"a fala não bate com o texto (só {sim:.0%} igual)", "meio"
    if folga < FOLGA - 0.05: return False, f"a última palavra está colada no corte ({folga:.2f} s de folga)", "fim"
    return True, "", ""
