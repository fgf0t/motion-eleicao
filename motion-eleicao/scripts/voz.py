# Narração: uma fala por cena, em WAV 48 kHz mono.
# Motores: "sistema" (voz do computador, grátis), "kokoro" e "piper" (vozes neurais grátis no computador),
#          "voicestudio" (a SUA voz clonada, grátis, local), "gemini" (Gemini TTS, chave gratuita do Google AI Studio).
# uso: python3 scripts/voz.py roteiro.json        gera as falas que faltam
#      python3 scripts/voz.py --listar            mostra as vozes disponíveis
import hashlib, json, os, subprocess, sys, tempfile, urllib.request, urllib.error, base64
from comum import SR, aviso, ff, ler_roteiro, mac, windows, passo

VOICESTUDIO = os.environ.get("VOICESTUDIO_URL", "http://localhost:3900")
CONF = os.path.join(os.path.expanduser("~"), ".config", "motion-eleicao")
VENV = os.path.join(CONF, "vozes-venv")  # ambiente do Kokoro e do Piper, criado pelo instalador

PS_FALA = r"""
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$nome = $env:MC_VOZ
$v = $s.GetInstalledVoices() | Where-Object { $_.Enabled -and ($_.VoiceInfo.Name -eq $nome -or ($nome -eq '' -and $_.VoiceInfo.Culture.Name -eq 'pt-BR')) } | Select-Object -First 1
if (-not $v) { $v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -eq 'pt-BR' } | Select-Object -First 1 }
if ($v) { $s.SelectVoice($v.VoiceInfo.Name) } else { Write-Error 'Nenhuma voz pt-BR instalada no Windows'; exit 2 }
$s.Rate = [int]$env:MC_RATE
$s.SetOutputToWaveFile($env:MC_SAIDA)
$s.Speak([IO.File]::ReadAllText($env:MC_TEXTO, [Text.Encoding]::UTF8))
$s.Dispose()
"""
PS_LISTA = r"""
Add-Type -AssemblyName System.Speech
(New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name + ' | ' + $_.VoiceInfo.Culture.Name }
"""


def fala_sistema(texto, saida, voz, vel):
    with tempfile.TemporaryDirectory() as tmp:
        txt = os.path.join(tmp, "fala.txt"); open(txt, "w", encoding="utf-8").write(texto)
        bruto = os.path.join(tmp, "bruto.aiff" if mac() else "bruto.wav")
        if mac():
            subprocess.run(["say", "-v", voz or "Luciana", "-r", str(int(185 * vel)), "-f", txt, "-o", bruto], check=True)
        elif windows():
            env = dict(os.environ, MC_VOZ=voz or "", MC_RATE=str(round((vel - 1) * 10)), MC_SAIDA=bruto, MC_TEXTO=txt)
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", PS_FALA], check=True, env=env)
        else:
            subprocess.run(["espeak-ng", "-v", voz or "pt-br", "-s", str(int(165 * vel)), "-f", txt, "-w", bruto], check=True)
        ff("-i", bruto, "-ar", str(SR), "-ac", "1", saida)


def tira_vicio(wav, texto):
    """o OmniVoice às vezes abre a fala com um "É" que não está no texto: um som curto isolado antes da primeira palavra.
    Se a fala começa com um trecho de menos de 0,45 s seguido de pausa, e o texto não começa com "é"/"e", corta ele."""
    import numpy as np, wave as wv
    primeira = (texto.strip().split() or [""])[0].lower().strip(",.!?:;\"'")
    if primeira in ("é", "e", "eh", "ah", "hum"): return False
    w = wv.open(wav); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32); w.close()
    fr = int(0.02 * sr); n = len(a) // fr
    if n < 20: return False
    rms = np.sqrt((a[:n * fr].reshape(n, fr) ** 2).mean(axis=1)); lim = rms.max() * 0.08
    on = rms > lim; k = int(np.argmax(on))
    fim_blob = k
    while fim_blob < n and on[fim_blob]: fim_blob += 1
    pausa = fim_blob
    while pausa < n and not on[pausa]: pausa += 1
    if (fim_blob - k) * 0.02 < 0.45 and (pausa - fim_blob) * 0.02 >= 0.12 and pausa < n:
        corte = max(fim_blob, pausa - 3) * fr
        with tempfile.TemporaryDirectory() as tmp:
            t = os.path.join(tmp, "c.wav"); ff("-ss", f"{corte / sr:.3f}", "-i", wav, t); os.replace(t, wav)
        return True
    return False


def fala_voicestudio(texto, saida, perfil, vel):
    corpo = {"model": "omnivoice", "input": texto, "voice": perfil, "response_format": "wav", "speed": vel}
    req = urllib.request.Request(f"{VOICESTUDIO}/v1/audio/speech", data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json"})
    try:
        dados = urllib.request.urlopen(req, timeout=600).read()
    except urllib.error.URLError as e:
        raise SystemExit(f"Não consegui falar com o VoiceStudio em {VOICESTUDIO} ({e}). Abra o VoiceStudio e tente de novo, "
                         'ou troque "motor" para "sistema" no roteiro.')
    with tempfile.TemporaryDirectory() as tmp:
        bruto = os.path.join(tmp, "vs.wav"); open(bruto, "wb").write(dados)
        ff("-i", bruto, "-ar", str(SR), "-ac", "1", saida)


def fala_local(motor, texto, saida, voz, vel):
    """Kokoro ou Piper, rodando no ambiente próprio (o modelo baixa na primeira vez)"""
    py = os.path.join(VENV, "Scripts", "python.exe") if windows() else os.path.join(VENV, "bin", "python")
    if not os.path.exists(py):
        raise SystemExit(f'A voz "{motor}" ainda não está instalada. Rode o instalador da skill de novo '
                         '(ele prepara as vozes neurais) ou troque "motor" para "sistema".')
    with tempfile.TemporaryDirectory() as tmp:
        txt = os.path.join(tmp, "fala.txt"); open(txt, "w", encoding="utf-8").write(texto)
        bruto = os.path.join(tmp, "bruto.wav")
        r = subprocess.run([py, os.path.join(os.path.dirname(os.path.abspath(__file__)), "voz_local.py"), motor, voz or "-", str(vel), txt, bruto])
        if r.returncode or not os.path.exists(bruto) or os.path.getsize(bruto) < 1000:
            raise SystemExit(f'A voz "{motor}" falhou. Rode o instalador de novo ou use "motor": "sistema".')
        ff("-i", bruto, "-ar", str(SR), "-ac", "1", saida)


def chave_gemini():
    k = os.environ.get("GEMINI_API_KEY")
    p = os.path.join(os.path.expanduser("~"), ".config", "motion-eleicao", "chave-gemini")
    if not k and os.path.exists(p): k = open(p).read().strip()
    if not k:
        raise SystemExit("Falta a chave do Gemini. Crie uma grátis em https://aistudio.google.com/apikey e salve em " + p)
    return k


def pedido_gemini(texto, voz, vel):
    """um pedido ao Gemini TTS; devolve PCM 16 bits, 24 kHz, mono"""
    estilo = "Narrador de documentário em português do Brasil, voz firme e clara" + (", ritmo rápido" if vel > 1.05 else "") + ". Leia exatamente:"
    corpo = {"contents": [{"parts": [{"text": f"{estilo} {texto}"}]}],
             "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voz or "Algenib"}}}}}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent",
                                 data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": chave_gemini()})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:300]
        if e.code == 429: msg = "acabou a cota grátis do dia (uns 10 pedidos). Tente amanhã ou use outra voz. " + msg
        raise SystemExit(f"Gemini TTS recusou ({e.code}): {msg}")
    return base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])


def salva_pcm(pcm, saida):
    with tempfile.TemporaryDirectory() as tmp:
        bruto = os.path.join(tmp, "g.pcm"); open(bruto, "wb").write(pcm)
        ff("-f", "s16le", "-ar", "24000", "-ac", "1", "-i", bruto, "-ar", str(SR), "-ac", "1", saida)


def cortes_por_silencio(pcm, n):
    """onde cortar um áudio com n falas: no meio dos n-1 silêncios mais longos (em amostras de 24 kHz)"""
    import numpy as np
    a = np.frombuffer(pcm, np.int16).astype(np.float32); fr = 480  # 20 ms
    m = len(a) // fr; rms = np.sqrt((a[:m * fr].reshape(m, fr) ** 2).mean(axis=1)); lim = rms.max() * 0.04
    fala = np.nonzero(rms > lim)[0]
    if len(fala) == 0: return None
    pausas, ini = [], None
    for k in range(fala[0], fala[-1] + 1):
        if rms[k] <= lim:
            if ini is None: ini = k
        elif ini is not None:
            pausas.append((k - ini, ini, k)); ini = None
    longas = sorted(sorted(pausas, reverse=True)[:n - 1], key=lambda p: p[1])
    if len(longas) < n - 1 or (longas and min(p[0] for p in longas) * 0.02 < 0.35): return None
    return [((p[1] + p[2]) // 2) * fr for p in longas]


def gemini_lote(textos, saidas, voz, vel):
    """todas as falas num pedido só (a cota grátis é de uns 10 pedidos por dia), cortadas pelo silêncio entre elas"""
    if len(textos) > 1:
        lote = ("Leia as frases abaixo, uma de cada vez, fazendo uma pausa longa de dois segundos entre uma frase e a outra:\n\n"
                + "\n\n".join(textos))
        pcm = pedido_gemini(lote, voz, vel)
        cortes = cortes_por_silencio(pcm, len(textos))
        if cortes:
            pedacos, ini = [], 0
            for c in cortes + [len(pcm) // 2]:
                pedacos.append(pcm[ini * 2:c * 2]); ini = c
            # confere: cada pedaço tem que ter duração parecida com o tamanho do texto
            seg = [len(p) / 48000 for p in pedacos]; letras = [len(t) for t in textos]
            taxa = [s / l for s, l in zip(seg, letras)]
            if max(taxa) / min(taxa) < 3.0:
                for p, sd in zip(pedacos, saidas): salva_pcm(p, sd)
                return
        aviso("não deu pra separar as falas do pedido único; pedindo uma por uma (gasta mais cota)")
    for t, sd in zip(textos, saidas): salva_pcm(pedido_gemini(t, voz, vel), sd)


def gerar(r):
    v = r.get("voz") or {}
    if v.get("motor", "auto") == "auto":  # padrão: Narrador Grave no VoiceStudio; sem ele, Kokoro; por último o sistema
        import voz_propria
        pid = voz_propria.narrador(salva=False)
        py = os.path.join(VENV, "Scripts", "python.exe") if windows() else os.path.join(VENV, "bin", "python")
        if pid: v = {**v, "motor": "voicestudio", "perfil": pid, "narrador": True}
        elif os.path.exists(py): v = {**v, "motor": "kokoro", "voz": v.get("voz") or "pm_alex"}
        else: v = {**v, "motor": "sistema"}
        r["voz"] = v
    motor, vel = v.get("motor", "sistema"), float(v.get("velocidade", 1.0))
    pasta = os.path.join(r["_proj"], "voz"); os.makedirs(pasta, exist_ok=True)
    passo(f"Voz ({motor})")
    faltam = []
    for i, c in enumerate(r["cenas"]):
        texto = c.get("fala_voz") or c["fala"]  # "fala_voz" corrige pronúncia sem mudar a legenda
        if motor in ("voicestudio", "kokoro", "piper"):
            from comum import por_extenso
            texto = por_extenso(texto)  # as vozes neurais erram algarismo ("2012" sai "2020"); por extenso elas acertam
        chave = hashlib.sha1(json.dumps([texto, motor, v.get("voz"), v.get("perfil"), vel]).encode()).hexdigest()[:12]
        saida, marca = os.path.join(pasta, f"c{i}.wav"), os.path.join(pasta, f"c{i}.chave")
        if os.path.exists(saida) and os.path.exists(marca) and open(marca).read() == chave:
            continue
        print(f"  cena {i + 1}: {texto[:70]}", flush=True)
        if motor == "gemini": faltam.append((texto, saida, marca, chave)); continue
        if motor == "voicestudio":
            fala_voicestudio(texto, saida, v["perfil"], vel)
            import shutil
            shutil.copy(saida, os.path.join(pasta, f"c{i}.orig.wav"))  # guarda sem corte: a conferência pode desfazer
            if not os.path.exists(os.path.join(pasta, f"c{i}.sem_vicio")) and tira_vicio(saida, texto):
                print("    (cortei um \"É\" que a voz pôs no começo)")
        elif motor in ("kokoro", "piper"): fala_local(motor, texto, saida, v.get("voz"), vel)
        else: fala_sistema(texto, saida, v.get("voz"), vel)
        open(marca, "w").write(chave)
    if faltam:
        gemini_lote([f[0] for f in faltam], [f[1] for f in faltam], v.get("voz"), vel)
        for _, _, marca, chave in faltam: open(marca, "w").write(chave)


def listar():
    print("Vozes do sistema em português do Brasil:")
    try:
        if mac():
            out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
            for l in out.splitlines():
                if "pt_BR" in l: print("  ", l.split("#")[0].strip())
        elif windows():
            out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LISTA], capture_output=True, text=True).stdout
            for l in out.splitlines():
                if "pt-BR" in l: print("  ", l.strip())
        else:
            print("   pt-br (espeak-ng)")
    except Exception as e:
        aviso(f"não consegui listar ({e})")
    print(f"\nVozes do VoiceStudio ({VOICESTUDIO}):")
    try:
        d = json.load(urllib.request.urlopen(f"{VOICESTUDIO}/v1/audio/voices", timeout=5))
        perfis = [x for x in d.get("voices", []) if x.get("type") != "openai_alias"]
        for x in perfis: print(f"   perfil: {x.get('voice_id')}  ({x.get('name')})")
        if not perfis: print("   nenhuma voz clonada ainda. Clone a sua no VoiceStudio (veja o README).")
    except Exception:
        print("   VoiceStudio não está aberto (ou não está instalado).")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--listar": listar()
    elif len(sys.argv) > 1: gerar(ler_roteiro(sys.argv[1]))
    else: raise SystemExit("uso: python3 scripts/voz.py roteiro.json | --listar")
