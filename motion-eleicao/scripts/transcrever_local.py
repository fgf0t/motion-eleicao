# Transcreve falas com tempo por palavra usando o faster-whisper (roda no ambiente das vozes, sem internet depois do
# primeiro download do modelo "small", uns 460 MB). Usado pelo conferir.py; imprime JSON.
# uso: <python do ambiente> transcrever_local.py fala1.wav [fala2.wav ...]
import json, os, subprocess, sys, tempfile, wave
import numpy as np

BASE = os.path.join(os.path.expanduser("~"), ".config", "motion-eleicao", "modelos", "whisper")


def le16k(p):
    with tempfile.TemporaryDirectory() as tmp:
        t = os.path.join(tmp, "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ar", "16000", "-ac", "1", t], check=True)
        w = wave.open(t); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; w.close()
    return a


if __name__ == "__main__":
    from faster_whisper import WhisperModel
    if not os.path.isdir(BASE): print("  baixando o modelo de transcrição (uns 460 MB, só na primeira vez)...", file=sys.stderr, flush=True)
    m = WhisperModel("small", device="cpu", compute_type="int8", download_root=BASE)
    out = []
    for p in sys.argv[1:]:
        a = le16k(p)
        seg, _ = m.transcribe(a, language="pt", word_timestamps=True, beam_size=1, vad_filter=False)
        out.append({"arquivo": p, "duracao": len(a) / 16000,
                    "palavras": [[w.word.strip(), round(float(w.start), 3), round(float(w.end), 3)] for s in seg for w in s.words]})
    print(json.dumps(out, ensure_ascii=False))
