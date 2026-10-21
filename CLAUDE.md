# Instalar a skill motion-eleicao

Se a pessoa pedir pra instalar (ou só abriu esta pasta e não sabe o que fazer), instale a skill:

1. Diga em uma frase o que vai acontecer: o instalador confere e instala Python, Node.js, ffmpeg, o HyperFrames e as
   vozes grátis, e copia a skill pro Claude Code e pro Codex. Leva de 5 a 20 minutos e baixa uns 2 GB.
2. Rode o instalador desta pasta:
   - Mac ou Linux: `bash instalar.sh`
   - Windows (PowerShell): `powershell -ExecutionPolicy Bypass -File instalar.ps1`
   Rode em segundo plano se o seu ambiente permitir, porque demora.
3. Se o instalador pedir a senha do computador (Homebrew no Mac, `sudo` no Linux) ou uma janela de permissão do
   Windows, você não consegue digitar por ela: peça pra pessoa abrir o Terminal (ou o PowerShell) nesta pasta, rodar
   o mesmo comando e digitar a senha. Depois continue daqui.
4. No fim ele pergunta se quer instalar o VoiceStudio; rodando por aqui, sem teclado, ele entende que não (dá pra fazer
   depois, pela skill, quando a pessoa quiser a própria voz).
5. No fim, confira que existe `~/.claude/skills/motion-eleicao/SKILL.md` e diga pra pessoa:
   "Pronto. Agora é só pedir: faz um vídeo." Se este chat não enxergar a skill nova, peça pra ela fechar e abrir o
   Claude Code de novo.

Não edite nenhum arquivo desta pasta durante a instalação.
