# Vozes neurais grátis que rodam no próprio computador, sem internet depois do primeiro download:
#   kokoro : Kokoro-82M (Apache 2.0). Vozes pt-BR: pf_dora (feminina), pm_alex e pm_santa (masculinas).
#   piper  : Piper (MIT). Vozes pt_BR: faber, cadu, jeff (medium), edresson (low).
# Roda dentro do ambiente próprio criado pelo instalador (~/.config/motion-eleicao/vozes-venv); o voz.py chama
# este script lá. Os modelos são baixados na primeira vez em ~/.config/motion-eleicao/modelos/.
# uso: <python do ambiente> voz_local.py kokoro|piper <voz> <velocidade> <texto.txt> <saida.wav>
import os, sys, urllib.request

BASE = os.path.join(os.path.expanduser("~"), ".config", "motion-eleicao", "modelos")
KOKORO = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
PIPER = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR"
PIPER_QUAL = {"faber": "medium", "cadu": "medium", "jeff": "medium", "edresson": "low"}


def baixa(url, destino, tamanho):
    if os.path.exists(destino): return destino
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    print(f"  baixando {os.path.basename(destino)} ({tamanho}, só na primeira vez)...", flush=True)
    tmp = destino + ".parcial"; urllib.request.urlretrieve(url, tmp); os.replace(tmp, destino)
    return destino


def kokoro(voz, vel, texto, saida):
    m = baixa(f"{KOKORO}/kokoro-v1.0.onnx", os.path.join(BASE, "kokoro-v1.0.onnx"), "310 MB")
    v = baixa(f"{KOKORO}/voices-v1.0.bin", os.path.join(BASE, "voices-v1.0.bin"), "27 MB")
    import espeakng_loader
    # o espeak-ng não aceita caminho de dados com mais de 160 letras: entra na pasta e passa o caminho relativo
    os.chdir(os.path.dirname(espeakng_loader.get_data_path())); os.environ["ESPEAK_DATA_PATH"] = "espeak-ng-data"
    import soundfile as sf
    from kokoro_onnx import Kokoro
    audio, sr = Kokoro(m, v).create(texto, voice=voz or "pm_alex", speed=vel, lang="pt-br")
    sf.write(saida, audio, sr)


def piper(voz, vel, texto, saida):
    import wave, importlib.util
    from piper import PiperVoice, SynthesisConfig
    voz = voz or "faber"; q = PIPER_QUAL.get(voz, "medium"); nome = f"pt_BR-{voz}-{q}"
    m = baixa(f"{PIPER}/{voz}/{q}/{nome}.onnx", os.path.join(BASE, f"{nome}.onnx"), "60 MB")
    baixa(f"{PIPER}/{voz}/{q}/{nome}.onnx.json", m + ".json", "5 KB")
    os.chdir(os.path.dirname(importlib.util.find_spec("piper").origin))  # caminho curto pro espeak-ng (máx. 160 letras)
    pv = PiperVoice.load(m, espeak_data_dir="espeak-ng-data")
    with wave.open(saida, "wb") as w:
        pv.synthesize_wav(texto, w, syn_config=SynthesisConfig(length_scale=1.0 / max(0.5, vel)))


if __name__ == "__main__":
    motor, voz, vel, txt, saida = sys.argv[1:6]
    txt, saida = os.path.abspath(txt), os.path.abspath(saida)
    texto = open(txt, encoding="utf-8").read().strip()
    (kokoro if motor == "kokoro" else piper)(voz if voz != "-" else None, float(vel), texto, saida)
