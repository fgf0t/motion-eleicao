# Passo a passo pra pessoa narrar os vídeos com a PRÓPRIA voz, clonada no VoiceStudio (grátis, roda no computador dela).
# uso: python3 scripts/voz_propria.py status              o que já está pronto e qual o próximo passo
#      python3 scripts/voz_propria.py instalar            como baixar e instalar o VoiceStudio neste sistema
#      python3 scripts/voz_propria.py texto               texto pra ler em voz alta (~30 s) + dicas de gravação
#      python3 scripts/voz_propria.py clonar <áudio> [nome]   cria a voz clonada a partir da gravação (mp3, m4a, ogg, wav...)
#      python3 scripts/voz_propria.py testar <id>         gera uma frase de teste com a voz (teste-da-voz.wav)
#      python3 scripts/voz_propria.py salvar <id>|sistema|kokoro|piper|gemini [voz]   guarda a escolha pros próximos vídeos
# Regra: só clone a SUA voz, ou a de alguém que autorizou por escrito.
import json, os, platform, sys, tempfile, urllib.error, urllib.request, uuid
from comum import ff, mac, windows

VS = os.environ.get("VOICESTUDIO_URL", "http://localhost:3900")
CONFIG = os.path.join(os.path.expanduser("~"), ".config", "motion-eleicao", "voz.json")
CONSENTIMENTO = "Esta é a minha voz e eu autorizo usá-la para narrar os meus próprios vídeos."
TEXTO = (CONSENTIMENTO + " Hoje eu vou contar uma coisa que pouca gente sabe. Os números oficiais mostram o que mudou "
         "no país nos últimos anos, e cada um deles tem uma fonte que qualquer pessoa pode conferir. Eu leio, eu pesquiso "
         "e eu conto do meu jeito, com calma, olhando pra quem está do outro lado. Se você não acredita em mim, tudo bem: "
         "pesquisa. A informação está aí, aberta, esperando alguém ir atrás.")


def online():
    try:
        urllib.request.urlopen(f"{VS}/v1/audio/voices", timeout=4); return True
    except Exception:
        return False


def perfis():
    d = json.load(urllib.request.urlopen(f"{VS}/v1/audio/voices", timeout=10))
    return [v for v in d.get("voices", []) if v.get("type") != "openai_alias"]


def status():
    cfg = json.load(open(CONFIG)) if os.path.exists(CONFIG) else None
    if cfg: print(f"Voz salva: {cfg}")
    else: print("Nenhuma voz escolhida ainda.")
    if online():
        ps = perfis()
        print(f"VoiceStudio aberto ({VS}). Vozes clonadas: " + (", ".join(f'{p["voice_id"]} ({p.get("name")})' for p in ps) or "nenhuma"))
        if not cfg: print("Próximo passo: " + ("python3 scripts/voz_propria.py texto (gravar)" if not ps else "testar e salvar uma das vozes acima"))
    else:
        print("VoiceStudio não está aberto (ou não está instalado). Próximo passo: python3 scripts/voz_propria.py instalar")


def instalar():
    print("VoiceStudio: grátis, de código aberto (AGPL-3.0), roda no seu computador. Página: https://github.com/debpalash/VoiceStudio")
    print("Ocupa uns 5 GB. A instalação demora alguns minutos.\n")
    if windows():
        print("No Windows, abra o PowerShell e cole:\n  irm https://voicestudio.sh/install | iex")
    else:
        print("Abra o Terminal e cole:\n  curl -fsSL https://voicestudio.sh/install | sh")
        if mac() and platform.machine() == "x86_64":
            print("\nATENÇÃO: este é um Mac Intel. O VoiceStudio só roda nele com backend remoto. Se não der, use a voz do sistema:")
            print("  python3 scripts/voz_propria.py salvar sistema")
    print("\nDepois abra o VoiceStudio (ele fica no endereço http://localhost:3900) e rode: python3 scripts/voz_propria.py status")


def texto():
    print("Leia este texto em voz alta, no seu jeito normal de falar (uns 30 segundos):\n")
    print("  " + TEXTO + "\n")
    print("""Dicas de gravação:
  - lugar silencioso, sem música, sem TV, sem ventilador; quarto com cama e cortina soa melhor que banheiro ou cozinha;
  - celular a um palmo da boca, de lado (não sopre no microfone);
  - grave no app de gravador de voz do celular ou no WhatsApp (mande o áudio pra você mesmo) e passe o arquivo pro computador;
  - leia inteiro, sem cortar; se errar, recomece a frase.
A primeira frase é o seu consentimento: ela fica registrada junto com a voz.""")


def multipart(campos, arquivos):
    limite = uuid.uuid4().hex; partes = []
    for k, v in campos.items():
        partes.append(f'--{limite}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, (nome, dados) in arquivos.items():
        partes.append(f'--{limite}\r\nContent-Disposition: form-data; name="{k}"; filename="{nome}"\r\nContent-Type: audio/wav\r\n\r\n'.encode() + dados + b"\r\n")
    partes.append(f"--{limite}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={limite}"


def post(caminho, campos, arquivos):
    corpo, tipo = multipart(campos, arquivos)
    req = urllib.request.Request(f"{VS}{caminho}", data=corpo, headers={"Content-Type": tipo}, method="POST")
    try:
        return json.load(urllib.request.urlopen(req, timeout=600))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"O VoiceStudio recusou ({e.code}): {e.read().decode()[:300]}")


def clonar(audio, nome="Minha voz", com_texto=False, consentimento=True, ref_text=None):
    if not online(): raise SystemExit("Abra o VoiceStudio primeiro (python3 scripts/voz_propria.py instalar).")
    if not os.path.exists(audio): raise SystemExit(f"Não achei o arquivo {audio}")
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "ref.wav")  # limpa: mono 24 kHz, corta silêncio das pontas, volume normal, até 40 s
        ff("-i", audio, "-t", "40", "-af", "highpass=f=70,silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-18:TP=-2",
           "-ar", "24000", "-ac", "1", wav)
        dados = open(wav, "rb").read()
        antes = {p["voice_id"] for p in perfis()}
        # sem transcrição o VoiceStudio escolhe o melhor trecho e transcreve sozinho (com transcrição o limite é 20 s)
        rt = ref_text if ref_text is not None else (TEXTO if com_texto else "")
        r = post("/profiles", {"name": nome, "ref_text": rt, "language": "pt", "kind": "clone"}, {"ref_audio": ("ref.wav", dados)})
        pid = r.get("id") or r.get("profile_id") or next((p["voice_id"] for p in perfis() if p["voice_id"] not in antes), None)
        if not pid: raise SystemExit(f"Criei o perfil mas não achei o id. Resposta: {str(r)[:300]}")
        if consentimento:  # a voz sintética do Narrador Grave não é de ninguém: não tem consentimento a registrar
            try:
                post(f"/profiles/{pid}/consent", {"consent_text": CONSENTIMENTO}, {"consent_audio": ("consentimento.wav", dados)})
            except SystemExit as e:
                print(f"  (aviso: não registrei o consentimento: {e})")
    if consentimento: print(f"Voz clonada. id: {pid}\nPróximo passo: python3 scripts/voz_propria.py testar {pid}")
    return pid


def testar(pid, saida="teste-da-voz.wav"):
    corpo = {"model": "omnivoice", "input": "Oi! Essa é a minha voz narrando. Não acredita em mim? Pesquisa.", "voice": pid, "response_format": "wav", "speed": 1.0}
    req = urllib.request.Request(f"{VS}/v1/audio/speech", data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json"})
    try:
        open(saida, "wb").write(urllib.request.urlopen(req, timeout=600).read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"O VoiceStudio não gerou o teste ({e.code}): {e.read().decode()[:300]}")
    print(f"Ouça: {os.path.abspath(saida)}\nSe gostou: python3 scripts/voz_propria.py salvar {pid}\n"
          "Se não gostou: grave de novo num lugar mais silencioso e rode o clonar outra vez.")


NARRADOR = "Narrador Grave"
# o que a amostra diz: com a transcrição junto o OmniVoice não inventa um "É" no começo das falas
REF_NARRADOR = "O desemprego fechou 2025 em cinco vírgula um por cento, o menor desde 2012, segundo o IBGE."
AMOSTRA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "voz-narrador-grave.wav")


def narrador(salva=True):
    """voz padrão: clona a amostra do Narrador Grave (voz sintética do OmniVoice, não é de ninguém) no VoiceStudio, uma vez só"""
    if not online(): return None
    achou = next((p["voice_id"] for p in perfis() if p.get("name") == NARRADOR), None)
    if not achou:
        print(f"  criando a voz padrão \"{NARRADOR}\" no seu VoiceStudio (uma vez só)...", flush=True)
        achou = clonar(AMOSTRA, NARRADOR, consentimento=False, ref_text=REF_NARRADOR)
    if salva:
        os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
        json.dump({"motor": "voicestudio", "perfil": achou, "narrador": True}, open(CONFIG, "w"))
    return achou


def salvar(escolha, voz=None):
    """sistema | kokoro [pm_alex|pm_santa|pf_dora] | piper [faber|cadu|jeff] | gemini [Algenib] | <id do VoiceStudio>"""
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    if escolha in ("sistema", "kokoro", "piper", "gemini"):
        cfg = {"motor": escolha}
        if voz: cfg["voz"] = voz
    else:
        cfg = {"motor": "voicestudio", "perfil": escolha, "propria": True}
    json.dump(cfg, open(CONFIG, "w")); print(f"Salvo em {CONFIG}: {cfg}. Os próximos vídeos usam essa voz.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "status": status()
    elif a[0] == "instalar": instalar()
    elif a[0] == "texto": texto()
    elif a[0] == "clonar": clonar(a[1], next((x for x in a[2:] if not x.startswith("--")), "Minha voz"), "--com-texto" in a)
    elif a[0] == "testar": testar(a[1])
    elif a[0] == "salvar": salvar(a[1], a[2] if len(a) > 2 else None)
    elif a[0] == "narrador": print("Narrador Grave:", narrador() or "VoiceStudio não está aberto")
    else: raise SystemExit("comando desconhecido; veja o começo de scripts/voz_propria.py")
