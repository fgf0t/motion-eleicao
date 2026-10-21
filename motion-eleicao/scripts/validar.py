# Confere o roteiro.json antes de gastar tempo com voz e render.
# Barra o que fere as regras eleitorais (fato sem fonte, acusação sem condenação) e o que quebra a montagem.
# uso: python3 scripts/validar.py caminho/roteiro.json
import os, re, subprocess, sys
from comum import estilos, ler_roteiro, sem_acento

# palavras que acusam de crime: só com condenação definitiva e a fonte dela em "condenacao"
ACUSA = ["criminoso", "criminosa", "bandido", "bandida", "ladrao", "ladra", "assassino", "assassina", "corrupto", "corrupta",
         "miliciano", "miliciana", "estuprador", "traficante", "quadrilha", "genocida", "golpista", "estelionatario"]
CAMPOS_TEXTO = ("fala", "tela", "numero", "detalhe", "carimbo", "citacao", "ressalva")


def tem_audio(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", p], capture_output=True, text=True)
    return bool(r.stdout.strip())


def validar(r):
    erros, avisos = [], []
    todos = {e["nome"]: e for e in estilos(rascunhos=True)}
    if r.get("estilo") not in todos:
        prontos = [e["nome"] for e in todos.values() if e.get("status") == "pronto"]
        erros.append(f'"estilo" tem que ser um destes: {", ".join(prontos)} (veio "{r.get("estilo")}")')
    elif todos[r["estilo"]].get("status") != "pronto":
        avisos.append(f'o estilo "{r["estilo"]}" ainda é rascunho (não foi aprovado)')
    cenas = r.get("cenas")
    if not isinstance(cenas, list) or not 3 <= len(cenas) <= 9:
        erros.append('"cenas" tem que ser uma lista de 3 a 9 cenas')
        return erros, avisos
    tem_fonte = False
    for i, c in enumerate(cenas, 1):
        if not isinstance(c, dict) or not str(c.get("fala", "")).strip():
            erros.append(f"cena {i}: falta a \"fala\" (o que a voz diz)"); continue
        if len(c["fala"]) > 240:
            erros.append(f"cena {i}: fala longa demais ({len(c['fala'])} letras). Quebre em duas cenas (máx. 240).")
        if len(str(c.get("tela", ""))) > 60:
            avisos.append(f"cena {i}: \"tela\" passa de 60 letras, vai ficar miúdo. Use 1 a 5 palavras.")
        fato = any(c.get(k) for k in ("numero", "carimbo", "citacao", "grafico", "linha_tempo"))  # lista: cada item tem a própria fonte
        if c.get("fonte") or c.get("manchete") or any(x.get("fonte") for x in c.get("lista") or []): tem_fonte = True
        if fato and not (c.get("fonte") or c.get("manchete")):
            erros.append(f"cena {i}: tem número, carimbo, citação, gráfico ou linha do tempo e não tem \"fonte\". Todo fato precisa de fonte (veículo ou órgão + data).")
        for item in c.get("lista") or []:
            if not item.get("fonte"):
                erros.append(f"cena {i}: item da lista \"{item.get('q', '')[:40]}\" sem fonte.")
        texto = " ".join(str(c.get(k, "")) for k in CAMPOS_TEXTO) + " " + " ".join(f"{x.get('q', '')} {x.get('a', '')}" for x in c.get("lista") or [])
        for p in ACUSA:
            if re.search(rf"\b{p}s?\b", sem_acento(texto)) and not c.get("condenacao"):
                erros.append(f'cena {i}: usa "{p}". Só pode chamar alguém de criminoso com condenação definitiva; nesse caso ponha a fonte em "condenacao". '
                             'Sem isso, troque por fato verificável: "denunciado pelo MP", "investigado", "réu", "acusado".')
        if c.get("clipe"):
            if not os.path.exists(os.path.join(r["_pasta"], str(c["clipe"]))):
                erros.append(f'cena {i}: não achei o clipe "{c["clipe"]}" (o caminho é a partir da pasta do roteiro).')
            elif c.get("fala_do_clipe") and not tem_audio(os.path.join(r["_pasta"], c["clipe"])):
                erros.append(f'cena {i}: "fala_do_clipe" está ligado, mas o clipe "{c["clipe"]}" não tem som.')
        elif c.get("fala_do_clipe"):
            erros.append(f'cena {i}: "fala_do_clipe" precisa de "clipe" (o vídeo do Flow com a narração).')
        if "foto" in c and not isinstance(c["foto"], str):
            erros.append(f'cena {i}: "foto" tem que ser um texto (o que buscar) ou o nome de um arquivo seu.')
    if not tem_fonte:
        erros.append("nenhuma cena tem \"fonte\". Vídeo sem fonte não sai.")
    v = r.get("voz") or {}
    if v.get("motor", "auto") not in ("auto", "sistema", "kokoro", "piper", "voicestudio", "gemini"):
        erros.append('"voz.motor" tem que ser "sistema", "kokoro", "piper", "voicestudio" ou "gemini"')
    if v.get("motor") == "voicestudio" and not v.get("perfil"):
        erros.append('voz VoiceStudio sem "perfil" (o id da SUA voz clonada). Veja com: python3 scripts/voz.py --listar')
    if r.get("impulsionar"):
        erros.append("esta skill não prepara conteúdo para impulsionamento pago. Tire o campo \"impulsionar\".")
    return erros, avisos


if __name__ == "__main__":
    if len(sys.argv) < 2: raise SystemExit("uso: python3 scripts/validar.py roteiro.json")
    e, a = validar(ler_roteiro(sys.argv[1]))
    for x in a: print("  aviso:", x)
    for x in e: print("  ERRO:", x)
    print("roteiro ok" if not e else f"{len(e)} erro(s): corrija o roteiro.json e rode de novo")
    sys.exit(1 if e else 0)
