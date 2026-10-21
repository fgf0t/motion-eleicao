#!/usr/bin/env bash
# Instalador da skill motion-eleicao (Mac e Linux).
# Confere e instala o que falta (Python, Node 22+, ffmpeg, HyperFrames), copia a skill pro Claude Code e pro Codex
# e mostra como clonar a sua voz no VoiceStudio.
# uso: bash instalar.sh
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
SKILL="$AQUI/motion-eleicao"
HF="hyperframes@0.8.172"
ok()   { printf "  \033[32mok\033[0m  %s\n" "$1"; }
falta(){ printf "  \033[33m..\033[0m  %s\n" "$1"; }
erro() { printf "  \033[31mERRO\033[0m %s\n" "$1"; }
SO="$(uname -s)"; ARQ="$(uname -m)"

echo; echo "== motion-eleicao: instalando =="; echo

# ---------- gerenciador de pacotes ----------
tem() { command -v "$1" >/dev/null 2>&1; }
brew_pronto() {  # no Mac, só instala o Homebrew se faltar alguma coisa
  tem brew && return 0
  falta "Homebrew (instalador de programas do Mac). Vai pedir a senha do computador."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  [ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
  [ -x /usr/local/bin/brew ] && eval "$(/usr/local/bin/brew shellenv)"
  tem brew
}
instala() {  # instala um pacote pelo gerenciador do sistema
  if [ "$SO" = "Darwin" ]; then brew_pronto && brew install "$1"
  elif tem apt-get; then sudo apt-get update -qq && sudo apt-get install -y "$1"
  elif tem dnf; then sudo dnf install -y "$1"
  elif tem pacman; then sudo pacman -S --noconfirm "$1"
  else erro "não sei instalar $1 neste sistema. Instale na mão e rode de novo."; return 1; fi
}

# ---------- Python 3 + numpy + pillow ----------
if tem python3; then ok "Python $(python3 -c 'import sys; print(sys.version.split()[0])')"
else falta "Python 3"; instala python3 || exit 1; fi
if ! python3 -c "import numpy, PIL" 2>/dev/null; then
  falta "bibliotecas numpy e pillow"
  python3 -m pip install --user -q numpy pillow 2>/dev/null || python3 -m pip install --user -q --break-system-packages numpy pillow 2>/dev/null \
    || { [ "$SO" != "Darwin" ] && instala python3-numpy && instala python3-pil; }
fi
python3 -m yt_dlp --version >/dev/null 2>&1 || python3 -m pip install --user -q yt-dlp 2>/dev/null || python3 -m pip install --user -q --break-system-packages yt-dlp 2>/dev/null
python3 -m yt_dlp --version >/dev/null 2>&1 && ok "yt-dlp (baixar referências de vídeo)" || falta "yt-dlp não instalou (opcional: só pra baixar referência de vídeo por link)"
python3 -c "import numpy, PIL" 2>/dev/null && ok "numpy e pillow" || { erro "não consegui instalar numpy e pillow (python3 -m pip install --user numpy pillow)"; exit 1; }

# ---------- Node 22+ ----------
versao_node() { node -e 'console.log(process.versions.node.split(".")[0])' 2>/dev/null || echo 0; }
if [ "$(versao_node)" -lt 22 ]; then
  falta "Node.js 22 ou mais novo"
  if [ "$SO" = "Darwin" ]; then instala node
  else
    curl -fsSL -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
    export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm install 22 && nvm alias default 22
  fi
fi
[ "$(versao_node)" -ge 22 ] && ok "Node $(node -v)" || { erro "Node 22+ não ficou disponível. Feche e abra o terminal e rode de novo."; exit 1; }

# ---------- ffmpeg (e espeak-ng no Linux, pra voz do sistema) ----------
tem ffmpeg || { falta "ffmpeg"; instala ffmpeg; }
tem ffmpeg && ok "ffmpeg" || { erro "ffmpeg não instalou"; exit 1; }
if [ "$SO" != "Darwin" ]; then tem espeak-ng || { falta "espeak-ng (voz do sistema no Linux)"; instala espeak-ng; }; fi

# ---------- HyperFrames + navegador de render ----------
falta "HyperFrames (motor de vídeo) e o navegador que ele usa pra renderizar"
npx --yes "$HF" browser ensure >/dev/null 2>&1 && ok "HyperFrames pronto" || { erro "HyperFrames não preparou o navegador. Rode: npx --yes $HF browser ensure"; exit 1; }

# ---------- nome antigo (motion-campanha): leva configuração, voz, modelos e estilos próprios pro nome novo ----------
if [ -d "$HOME/.config/motion-campanha" ] && [ ! -d "$HOME/.config/motion-eleicao" ]; then mv "$HOME/.config/motion-campanha" "$HOME/.config/motion-eleicao"; fi
for raiz in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
  if [ -d "$raiz/motion-campanha" ]; then
    [ -d "$raiz/motion-eleicao" ] || mv "$raiz/motion-campanha" "$raiz/motion-eleicao"
    rm -rf "$raiz/motion-campanha"
  fi
done

# ---------- vozes neurais grátis (Kokoro e Piper) e o conferidor de falas (faster-whisper), num ambiente Python só deles ----------
VENV="$HOME/.config/motion-eleicao/vozes-venv"
if [ ! -x "$VENV/bin/python" ] || ! "$VENV/bin/python" -c "import kokoro_onnx, piper, faster_whisper" 2>/dev/null; then
  falta "vozes neurais e conferidor de falas (uns 250 MB; os modelos baixam no primeiro uso: Kokoro 340 MB, Piper 60 MB, conferidor 460 MB)"
  tem uv || { curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1; export PATH="$HOME/.local/bin:$PATH"; }
  mkdir -p "$HOME/.config/motion-eleicao"
  [ -x "$VENV/bin/python" ] || uv venv -q -p 3.12 "$VENV" >/dev/null 2>&1
  uv pip install -q -p "$VENV/bin/python" kokoro-onnx soundfile piper-tts faster-whisper >/dev/null 2>&1
fi
"$VENV/bin/python" -c "import kokoro_onnx, piper" 2>/dev/null && ok "vozes neurais (Kokoro e Piper)" || falta "vozes neurais não instalaram (opcional; a voz do sistema continua funcionando)"
"$VENV/bin/python" -c "import faster_whisper" 2>/dev/null && ok "conferidor de falas (confere que nenhuma fala sai cortada)" || falta "conferidor de falas não instalou: confira as falas ouvindo"

# ---------- copia a skill pro Claude Code e pro Codex ----------
for destino in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
  mkdir -p "$destino"
  guarda="$(mktemp -d)"  # estilos criados pela pessoa e sons baixados sobrevivem à reinstalação
  if [ -d "$destino/motion-eleicao" ]; then
    for e in "$destino/motion-eleicao/estilos"/*/; do
      [ -f "$e/sobre.json" ] && grep -Eq '"origem": *"referencia"' "$e/sobre.json" && cp -R "${e%/}" "$guarda/"
    done
    [ -d "$destino/motion-eleicao/assets/sfx-extra" ] && cp -R "$destino/motion-eleicao/assets/sfx-extra" "$guarda/_sfx-extra"
  fi
  rm -rf "$destino/motion-eleicao"; cp -R "$SKILL" "$destino/motion-eleicao"
  for e in "$guarda"/*/; do
    [ -d "$e" ] || continue; e="${e%/}"
    if [ "$(basename "$e")" = "_sfx-extra" ]; then cp -R "$e" "$destino/motion-eleicao/assets/sfx-extra"; else cp -R "$e" "$destino/motion-eleicao/estilos/"; fi
  done
  rm -rf "$guarda"
  find "$destino/motion-eleicao" -name '._*' -delete 2>/dev/null
  ok "skill copiada em $destino/motion-eleicao"
done

# ---------- voz ----------
echo
if [ "$SO" = "Darwin" ]; then
  if say -v '?' | grep -q "^Luciana"; then ok "voz do sistema em português: Luciana"
  elif say -v '?' | grep -q pt_BR; then ok "voz do sistema em português: $(say -v '?' | grep pt_BR | head -1 | awk '{print $1}') (ponha o nome em \"voz\" no roteiro)"
  else falta "baixe uma voz em português: Ajustes do Sistema > Acessibilidade > Conteúdo Falado > Voz do Sistema > Gerenciar Vozes > Português (Brasil)"; fi
fi
echo
echo "== Voz própria (opcional, grátis): VoiceStudio =="
echo "   Você grava 10 a 20 segundos da SUA voz e a narração sai com ela. Nunca clone a voz de outra pessoa sem permissão."
echo "   Página: https://github.com/debpalash/VoiceStudio  (ocupa uns 5 GB)"
[ "$SO" = "Darwin" ] && [ "$ARQ" = "x86_64" ] && echo "   Atenção: em Mac Intel o VoiceStudio só roda com backend remoto. Pode usar a voz do sistema."
if [ -z "${SEM_NAVEGADOR:-}" ]; then
  ( tem open && open "https://github.com/debpalash/VoiceStudio" ) || ( tem xdg-open && xdg-open "https://github.com/debpalash/VoiceStudio" ) 2>/dev/null
fi
printf "   Instalar o VoiceStudio agora? (s/N) "; { read -r resp </dev/tty; } 2>/dev/null || resp=n; echo
if [ "$resp" = "s" ] || [ "$resp" = "S" ]; then curl -fsSL https://voicestudio.sh/install | sh; fi

echo
echo "== Pronto =="
python3 "$HOME/.claude/skills/motion-eleicao/scripts/estilos.py" boas-vindas --instalador
echo
echo "   Galeria dos estilos: $HOME/.claude/skills/motion-eleicao/estilos/galeria.jpg"
echo "   Abra o Claude Code (ou o Codex) numa pasta sua e peça, por exemplo:"
echo "   faz um vídeo sobre a queda do desemprego no estilo dados"
echo
