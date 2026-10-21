# Trata as fotos em código, sem IA: retícula de jornal, recorte de fundo branco, borda de papel.
#   branca : pontos claros sobre transparente (estilos "pesquise" e "dados", fundo preto)
#   jornal : pontos de tinta sobre papel creme, com borda branca de recorte
#   pb     : preto e branco contrastado com grão, pra polaroide (estilo "dossie")
#   vhs    : só redimensiona; o visual de fita é feito no CSS (estilo "vhs")
#   pixel  : foto pequena com poucas cores, ampliada sem suavizar na tela (estilo "pixel")
# uso: python3 scripts/reticula.py foto.jpg saida.png --modo jornal --largura 900
import argparse, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

CELULA = 8  # px por ponto no tamanho final


def fundo_branco(im):
    """a foto é um objeto sobre fundo claro liso? (bordas claras e uniformes)"""
    c = np.array(im.convert("L")).astype(np.float32)
    borda = np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]])
    return (np.median(borda) > 170 and borda.std() < 25) or (borda > 215).mean() > 0.85


def mascara_fundo(im):
    """transparente onde o fundo claro encosta na borda (preenchimento a partir das bordas)"""
    c = np.array(im.convert("RGB")).astype(np.int16)
    borda = np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]])
    claro = np.abs(c - np.median(borda, axis=0)).max(axis=2) < 26
    h, w = claro.shape
    vis = np.zeros_like(claro)
    pilha = [(0, x) for x in range(0, w, 7)] + [(h - 1, x) for x in range(0, w, 7)] + [(y, 0) for y in range(0, h, 7)] + [(y, w - 1) for y in range(0, h, 7)]
    while pilha:
        y, x = pilha.pop()
        if y < 0 or x < 0 or y >= h or x >= w or vis[y, x] or not claro[y, x]: continue
        vis[y, x] = True
        pilha += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    obj = ~vis
    # tira pedacinhos soltos: fica só o que for maior que 3% do maior pedaço (busca numa versão reduzida)
    pq = np.array(Image.fromarray((obj * 255).astype(np.uint8)).resize((max(1, w // 4), max(1, h // 4)), Image.NEAREST)) > 0
    rot = np.zeros(pq.shape, np.int32); tam = [0]
    for sy, sx in zip(*np.nonzero(pq)):
        if rot[sy, sx]: continue
        tam.append(0); k = len(tam) - 1; fila = [(sy, sx)]; rot[sy, sx] = k
        while fila:
            y, x = fila.pop(); tam[k] += 1
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < pq.shape[0] and 0 <= xx < pq.shape[1] and pq[yy, xx] and not rot[yy, xx]:
                    rot[yy, xx] = k; fila.append((yy, xx))
    if len(tam) > 1:
        bons = [k for k in range(1, len(tam)) if tam[k] >= 0.03 * max(tam)]
        manter = np.array(Image.fromarray(np.isin(rot, bons).astype(np.uint8) * 255).resize((w, h), Image.NEAREST).filter(ImageFilter.MaxFilter(9))) > 0
        obj &= manter
    return Image.fromarray(np.where(obj, 255, 0).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.5))


def borda_rasgada(w, h, margem, semente):
    """máscara retangular com borda irregular, como papel recortado à mão"""
    rng = np.random.default_rng(semente)
    pts = []
    for lado in range(4):
        n = 14
        for k in range(n):
            f = k / n
            j = margem * (0.35 + rng.random() * 0.9)
            if lado == 0: pts.append((f * w, j))
            elif lado == 1: pts.append((w - j, f * h))
            elif lado == 2: pts.append((w - f * w, h - j))
            else: pts.append((j, h - f * h))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def pontos(cinza, alfa, cor, angulo, sobre=None, escala=2):
    """retícula: um ponto por célula de uma grade girada; raio segue o tom (claro = ponto grande se cor clara)"""
    W, H = cinza.size
    S = escala
    blur = np.array(cinza.filter(ImageFilter.GaussianBlur(CELULA * 0.45))).astype(np.float32) / 255
    al = np.array(alfa).astype(np.float32) / 255
    out = Image.new("RGBA", (W * S, H * S), sobre or (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    a = math.radians(angulo); ca, sa = math.cos(a), math.sin(a)
    diag = int(math.hypot(W, H) / CELULA) + 2
    claro = sum(cor[:3]) > 380
    for i in range(-diag, diag):
        for j in range(-diag, diag):
            x = W / 2 + (i * ca - j * sa) * CELULA
            y = H / 2 + (i * sa + j * ca) * CELULA
            if not (0 <= x < W and 0 <= y < H): continue
            m = al[int(y), int(x)]
            if m < 0.35: continue
            v = blur[int(y), int(x)]
            tom = v if claro else 1 - v
            r = (CELULA / 2) * 1.2 * (tom ** 0.85)
            if r < 0.45: continue
            d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=(*cor[:3], int(255 * min(1, m * 1.2))))
    return out.resize((W, H), Image.LANCZOS)


def tratar(origem, saida, modo="branca", largura=900, caixa=None, semente=1):
    im = Image.open(origem); im = ImageOps.exif_transpose(im).convert("RGB")
    if caixa:
        W, H = im.size; im = im.crop((int(caixa[0] * W), int(caixa[1] * H), int(caixa[2] * W), int(caixa[3] * H)))
    if modo == "vhs":
        im.thumbnail((1400, 1400), Image.LANCZOS); im.save(saida, quality=90); return im.size
    if modo == "pixel":
        larg = max(48, largura // 8)
        im = ImageOps.autocontrast(im, cutoff=1).resize((larg, max(1, int(im.height * larg / im.width))), Image.BOX)
        im = im.quantize(colors=20, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
        im.save(saida); return im.size
    im = im.resize((largura, max(1, int(im.height * largura / im.width))), Image.LANCZOS)
    W, H = im.size
    recorta = fundo_branco(im)
    cinza = ImageOps.autocontrast(im.convert("L"), cutoff=2)
    if modo == "pb":
        g = np.array(ImageOps.autocontrast(cinza, cutoff=4)).astype(np.float32)
        g += np.random.default_rng(semente).normal(0, 14, g.shape)
        Image.fromarray(g.clip(0, 255).astype(np.uint8)).convert("RGB").save(saida, quality=90); return (W, H)
    if modo == "branca":
        alfa = mascara_fundo(im) if recorta else Image.new("L", (W, H), 255)
        out = pontos(cinza, alfa, (242, 242, 236), 0)
        if not recorta:  # bordas suaves pra foto inteira sumir no preto
            b = Image.new("L", (W, H), 0); ImageDraw.Draw(b).rectangle((W * .04, H * .04, W * .96, H * .96), fill=255)
            b = np.array(b.filter(ImageFilter.GaussianBlur(min(W, H) * .06))).astype(np.float32) / 255
            out.putalpha(Image.fromarray((np.array(out.getchannel("A")).astype(np.float32) * b).astype(np.uint8)))
        out.save(saida); return out.size
    # jornal: tinta sobre papel creme, recorte com borda branca de papel
    pad = 26
    tela = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    if recorta:
        forma = Image.new("L", tela.size, 0); forma.paste(mascara_fundo(im), (pad, pad))
    else:
        forma = Image.new("L", tela.size, 0); forma.paste(borda_rasgada(W, H, 10, semente), (pad, pad))
    papel_branco = forma.filter(ImageFilter.MaxFilter(25 if recorta else 17))
    branco = Image.new("RGBA", tela.size, (252, 250, 243, 255)); tela.paste(branco, (0, 0), papel_branco)
    creme = Image.new("RGBA", (W, H), (239, 229, 204, 255))
    ret = pontos(cinza, Image.new("L", (W, H), 255), (42, 33, 27), 45, sobre=None)
    creme.alpha_composite(ret)
    tela.paste(creme, (pad, pad), forma.crop((pad, pad, pad + W, pad + H)))
    tela.save(saida); return tela.size


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("origem"); p.add_argument("saida")
    p.add_argument("--modo", default="branca", choices=["branca", "jornal", "pb", "vhs", "pixel"])
    p.add_argument("--largura", type=int, default=900)
    a = p.parse_args()
    print(tratar(a.origem, a.saida, a.modo, a.largura))
