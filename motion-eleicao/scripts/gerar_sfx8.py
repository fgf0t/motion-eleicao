# Gera os efeitos 8-bit (estilo sfxr: moeda, pulo, bip, blip, erro, explosão, glitch, vitória) como WAV.
# São feitos em código (onda quadrada com envelope), sem direito autoral. A montagem já gera sozinha;
# este script é pra quem quiser os arquivos soltos.
# uso: python3 scripts/gerar_sfx8.py pasta_destino
import os, sys
from comum import salvar_wav
from sons import sfx8

if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else "sfx8"
    os.makedirs(pasta, exist_ok=True)
    for nome, onda in sfx8().items():
        salvar_wav(os.path.join(pasta, f"{nome}.wav"), onda); print("ok", nome)
