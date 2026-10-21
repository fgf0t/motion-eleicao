# Faz o vídeo inteiro a partir do roteiro.json: confere, narra, busca fotos, monta e renderiza.
# Pode rodar de novo à vontade: o que já está pronto (voz, fotos) não é refeito.
# uso: python3 scripts/fazer.py caminho/roteiro.json [--sem-render]
import os, subprocess, sys, time
from comum import HYPERFRAMES, cmd_npx, ff, ler_roteiro, passo
import shutil
import validar, voz, fotos, manchetes, montar, conferir
from comum import aviso


def render(r):
    passo("Render (HyperFrames)")
    D = r["_proj"]; bruto = os.path.join(D, "renders", "bruto.mp4")
    os.makedirs(os.path.dirname(bruto), exist_ok=True)
    if os.path.exists(bruto): os.remove(bruto)
    t0 = time.time()
    p = subprocess.run([cmd_npx(), "--yes", HYPERFRAMES, "render", "--fps", "30", "--video-bitrate", "12M", "--quiet", "--output", bruto],
                       cwd=D, capture_output=True, text=True, errors="replace")
    if p.returncode or not os.path.exists(bruto):
        print((p.stdout or "")[-1500:], (p.stderr or "")[-1500:])
        raise SystemExit("O render falhou. Rode de novo; se repetir, rode o instalador da skill (ele prepara o navegador do HyperFrames).")
    final = os.path.join(r["_pasta"], f"{r['_nome']}.mp4")
    ff("-i", bruto, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", final)
    os.remove(bruto)
    print(f"  pronto em {time.time() - t0:.0f} s")
    return final


def conferir_falas(r, ctx):
    """transcreve o áudio final de cada cena; devolve as cenas com fala cortada (None se não há transcritor)"""
    passo("Conferindo as falas (nenhuma pode sair cortada)")
    wavs = [os.path.join(ctx.A, "a", f"c{L['i']}.wav") for L in ctx.L]
    tr = conferir.transcrever(wavs)
    if tr is None:
        aviso("não achei transcritor pra conferir as falas. Rode o instalador de novo (ele põe o faster-whisper) e confira ouvindo.")
        return None
    falhas = {}
    for L, t in zip(ctx.L, tr):
        c = L["c"]; ok, motivo, onde = conferir.julgar(c.get("fala_voz") or c["fala"], t)
        print(f"  cena {L['i'] + 1}: fala inteira ✓" if ok else f"  cena {L['i'] + 1}: PROBLEMA, {motivo}", flush=True)
        if not ok: falhas[L["i"]] = onde
    return falhas


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args: raise SystemExit("uso: python3 scripts/fazer.py roteiro.json [--sem-render]")
    r = ler_roteiro(args[0])
    passo("Conferindo o roteiro")
    erros, avisos = validar.validar(r)
    for a in avisos: print("  aviso:", a)
    if erros:
        for e in erros: print("  ERRO:", e)
        raise SystemExit("Corrija o roteiro.json e rode de novo.")
    os.makedirs(r["_proj"], exist_ok=True)
    voz.gerar(r)
    fotos.gerar(r)
    manchetes.gerar(r)
    ctx = montar.montar(r)
    pasta_voz = os.path.join(r["_proj"], "voz")
    for tentativa in range(3):
        falhas = conferir_falas(r, ctx)
        if not falhas: break
        if tentativa == 0:  # 1) mais margem; se faltou o começo, desfaz o corte do "É"; se sobrou "É", corta de novo
            print("  refazendo essas cenas com mais margem...")
            for i, onde in falhas.items():
                open(os.path.join(pasta_voz, f"c{i}.margem"), "w").write("0.3")
                orig = os.path.join(pasta_voz, f"c{i}.orig.wav")
                if onde == "comeco" and os.path.exists(orig):
                    shutil.copy(orig, os.path.join(pasta_voz, f"c{i}.wav"))
                    open(os.path.join(pasta_voz, f"c{i}.sem_vicio"), "w").write("1")
                elif onde == "vicio" and os.path.exists(orig):
                    c = r["cenas"][i]; t = c.get("fala_voz") or c["fala"]
                    shutil.copy(orig, os.path.join(pasta_voz, f"c{i}.wav")); voz.tira_vicio(os.path.join(pasta_voz, f"c{i}.wav"), t)
        elif tentativa == 1:  # 2) gera a fala de novo
            print("  gerando a fala dessas cenas de novo...")
            for i in falhas:
                for ext in (".wav", ".chave", ".orig.wav", ".sem_vicio"):
                    p = os.path.join(pasta_voz, f"c{i}{ext}")
                    if os.path.exists(p): os.remove(p)
            voz.gerar(r)
        else:
            raise SystemExit(f"PAREI: a fala das cenas {', '.join(str(i + 1) for i in falhas)} continua cortada depois de refazer duas vezes. "
                             "Escreva a fala de outro jeito (ou use \"fala_voz\") ou troque a voz (cena com \"fala_do_clipe\": gere o clipe de novo no Flow), e rode de novo. O vídeo não foi renderizado.")
        ctx = montar.montar(r)
    if "--sem-render" in sys.argv:
        print(f"\nProjeto montado em {r['_proj']} (sem render)."); return
    final = render(r)
    print(f"\nVÍDEO: {final}\nFONTES E CRÉDITOS PRO POST: {os.path.join(r['_pasta'], r['_nome'] + '-fontes.txt')}")


if __name__ == "__main__":
    main()
