# Instalador da skill motion-eleicao (Windows 10 e 11).
# Confere e instala o que falta (Python, Node 22+, ffmpeg, HyperFrames), copia a skill pro Claude Code e pro Codex
# e mostra como clonar a sua voz no VoiceStudio.
# uso (PowerShell): powershell -ExecutionPolicy Bypass -File instalar.ps1
$ErrorActionPreference = "Continue"
$Aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$Skill = Join-Path $Aqui "motion-eleicao"
$HF = "hyperframes@0.8.172"
function Ok($m) { Write-Host "  ok  $m" -ForegroundColor Green }
function Falta($m) { Write-Host "  ..  $m" -ForegroundColor Yellow }
function Erro($m) { Write-Host "  ERRO $m" -ForegroundColor Red }
function Tem($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function Recarrega-Path { $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") }

Write-Host "`n== motion-eleicao: instalando ==`n"
if (-not (Tem "winget")) { Erro "winget não encontrado. Atualize o 'Instalador de Aplicativo' na Microsoft Store e rode de novo."; exit 1 }

# ---------- Python ----------
if (-not (Tem "py")) { Falta "Python 3"; winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements; Recarrega-Path }
if (Tem "py") { Ok ("Python " + (py -c "import sys; print(sys.version.split()[0])")) } else { Erro "Python não ficou disponível. Feche e abra o PowerShell e rode de novo."; exit 1 }
py -c "import numpy, PIL" 2>$null
if ($LASTEXITCODE -ne 0) { Falta "bibliotecas numpy e pillow"; py -m pip install --user -q numpy pillow }
py -c "import numpy, PIL" 2>$null
py -m pip install --user -q yt-dlp 2>$null
if ($LASTEXITCODE -eq 0) { Ok "numpy e pillow" } else { Erro "não consegui instalar numpy e pillow (py -m pip install --user numpy pillow)"; exit 1 }

# ---------- Node 22+ ----------
$nv = 0; if (Tem "node") { $nv = [int](node -e "console.log(process.versions.node.split('.')[0])") }
if ($nv -lt 22) { Falta "Node.js 22 ou mais novo"; winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements; Recarrega-Path }
if (Tem "node") { Ok ("Node " + (node -v)) } else { Erro "Node não ficou disponível. Feche e abra o PowerShell e rode de novo."; exit 1 }

# ---------- ffmpeg ----------
if (-not (Tem "ffmpeg")) { Falta "ffmpeg"; winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements; Recarrega-Path }
if (Tem "ffmpeg") { Ok "ffmpeg" } else { Erro "ffmpeg não ficou disponível. Feche e abra o PowerShell e rode de novo."; exit 1 }

# ---------- HyperFrames + navegador de render ----------
Falta "HyperFrames (motor de vídeo) e o navegador que ele usa pra renderizar"
npx --yes $HF browser ensure | Out-Null
if ($LASTEXITCODE -eq 0) { Ok "HyperFrames pronto" } else { Erro "HyperFrames não preparou o navegador. Rode: npx --yes $HF browser ensure"; exit 1 }

# ---------- nome antigo (motion-campanha): leva configuração, voz, modelos e estilos próprios pro nome novo ----------
if ((Test-Path "$HOME\.config\motion-campanha") -and -not (Test-Path "$HOME\.config\motion-eleicao")) { Move-Item "$HOME\.config\motion-campanha" "$HOME\.config\motion-eleicao" }
foreach ($r in @("$HOME\.claude\skills", "$HOME\.codex\skills")) {
  if (Test-Path "$r\motion-campanha") {
    if (-not (Test-Path "$r\motion-eleicao")) { Move-Item "$r\motion-campanha" "$r\motion-eleicao" } else { Remove-Item -Recurse -Force "$r\motion-campanha" }
  }
}

# ---------- vozes neurais grátis (Kokoro e Piper), num ambiente Python só delas ----------
$Venv = "$HOME\.config\motion-eleicao\vozes-venv"
$VPy = Join-Path $Venv "Scripts\python.exe"
& $VPy -c "import kokoro_onnx, piper, faster_whisper" 2>$null
if ($LASTEXITCODE -ne 0) {
  Falta "vozes neurais e conferidor de falas (uns 250 MB; os modelos baixam no primeiro uso: Kokoro 340 MB, Piper 60 MB, conferidor 460 MB)"
  if (-not (Tem "uv")) { irm https://astral.sh/uv/install.ps1 | iex; Recarrega-Path; $env:Path += ";$HOME\.local\bin" }
  New-Item -ItemType Directory -Force -Path "$HOME\.config\motion-eleicao" | Out-Null
  if (-not (Test-Path $VPy)) { uv venv -q -p 3.12 $Venv | Out-Null }; uv pip install -q -p $VPy kokoro-onnx soundfile piper-tts faster-whisper | Out-Null
}
& $VPy -c "import kokoro_onnx, piper" 2>$null
if ($LASTEXITCODE -eq 0) { Ok "vozes neurais (Kokoro e Piper)" } else { Falta "vozes neurais não instalaram (opcional; a voz do sistema continua funcionando)" }
& $VPy -c "import faster_whisper" 2>$null
if ($LASTEXITCODE -eq 0) { Ok "conferidor de falas" } else { Falta "conferidor de falas não instalou: confira as falas ouvindo" }

# ---------- copia a skill pro Claude Code e pro Codex ----------
foreach ($d in @("$HOME\.claude\skills", "$HOME\.codex\skills")) {
  New-Item -ItemType Directory -Force -Path $d | Out-Null
  $alvo = Join-Path $d "motion-eleicao"
  $guarda = Join-Path $env:TEMP ("mc-" + [guid]::NewGuid())
  New-Item -ItemType Directory -Force -Path $guarda | Out-Null
  if (Test-Path $alvo) {  # estilos criados pela pessoa e sons baixados sobrevivem à reinstalação
    Get-ChildItem (Join-Path $alvo "estilos") -Directory | Where-Object { (Test-Path (Join-Path $_.FullName "sobre.json")) -and ((Get-Content (Join-Path $_.FullName "sobre.json") -Raw) -match '"origem":\s*"referencia"') } | ForEach-Object { Copy-Item -Recurse $_.FullName $guarda }
    $extra = Join-Path $alvo "assets\sfx-extra"; if (Test-Path $extra) { Copy-Item -Recurse $extra (Join-Path $guarda "_sfx-extra") }
    Remove-Item -Recurse -Force $alvo
  }
  Copy-Item -Recurse $Skill $alvo
  Get-ChildItem $guarda -Directory | ForEach-Object {
    if ($_.Name -eq "_sfx-extra") { Copy-Item -Recurse $_.FullName (Join-Path $alvo "assets\sfx-extra") } else { Copy-Item -Recurse $_.FullName (Join-Path $alvo "estilos") }
  }
  Remove-Item -Recurse -Force $guarda
  Get-ChildItem -Path $alvo -Recurse -Force -Filter "._*" | Remove-Item -Force
  Ok "skill copiada em $alvo"
}

# ---------- voz ----------
Add-Type -AssemblyName System.Speech
$pt = (New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -eq "pt-BR" }
if ($pt) { Ok ("voz do sistema em português: " + $pt[0].VoiceInfo.Name) }
else { Falta "instale a voz em português: Configurações > Hora e idioma > Idioma e região > Português (Brasil) > Opções > Fala" }

Write-Host "`n== Voz própria (opcional, grátis): VoiceStudio =="
Write-Host "   Você grava 10 a 20 segundos da SUA voz e a narração sai com ela. Nunca clone a voz de outra pessoa sem permissão."
Write-Host "   Página: https://github.com/debpalash/VoiceStudio  (ocupa uns 5 GB)"
Start-Process "https://github.com/debpalash/VoiceStudio"
$resp = Read-Host "   Instalar o VoiceStudio agora? (s/N)"
if ($resp -eq "s" -or $resp -eq "S") { irm https://voicestudio.sh/install | iex }

Write-Host "`n== Pronto =="
py "$HOME\.claude\skills\motion-eleicao\scripts\estilos.py" boas-vindas --instalador
Write-Host "`n   Galeria dos estilos: $HOME\.claude\skills\motion-eleicao\estilos\galeria.jpg"
Write-Host "   Abra o Claude Code (ou o Codex) numa pasta sua e peça, por exemplo:"
Write-Host "   faz um vídeo sobre a queda do desemprego no estilo dados`n"
