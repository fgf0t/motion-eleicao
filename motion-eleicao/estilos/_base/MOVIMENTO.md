# Regras de movimento

Leia antes de escrever ou mudar animação: efeito novo num `estilo.py`, câmera, transição, ou um estilo novo que
precise de código além do `config.json`. Adaptado pra vídeo de duas fontes com licença MIT: as skills oficiais do GSAP
(GreenSock, github.com/greensock/gsap-skills) e a skill `animate` do Emil Kowalski (github.com/emilkowalski/skills).
As duas foram escritas pra interface de site; aqui fica só o que vale pra vídeo 9:16 renderizado quadro a quadro.

## 1. Antes de animar: pra quê?

Diga em uma palavra o motivo do movimento: **chegada** (algo entra), **ênfase** (a palavra que importa),
**ligação** (de onde veio, pra onde vai), **troca** (uma cena vira outra) ou **ritmo** (acompanha a batida ou a fala).
Sem motivo, não anima: deixa parado. Número, citação e fonte são pra ler; não fazem enfeite enquanto estão na tela.
A fonte nunca se mexe depois de entrar.

## 2. Só transform e opacidade

- Mova com `x`, `y`, `xPercent`, `yPercent`, `scale`, `rotation`, `rotationX/Y`. Nunca com `left`, `top`, `width`,
  `height`, `margin` ou `padding`. O quarto permitido é `clipPath` (revelar texto, cortina, máquina de escrever).
- `filter: blur()` só em transição curta (até 0,2 s), nunca em camada que fica na tela.
- Nada nasce do zero: entrada por escala começa em `0.9` a `0.97` com opacidade 0, ou de **cima pra baixo**
  (`scale: 1.3` a `2.6` com opacidade 0, o "carimbo"). Nunca `scale: 0`.

## 3. Curva (ease)

Use só os nomes documentados do GSAP. Nada de inventar `cubic-bezier`.

| situação | ease |
|---|---|
| entrada (texto, foto, cartão) | `power3.out` (padrão) ou `power2.out` |
| coisa que anda na tela de um ponto a outro, câmera | `power3.inOut` ou `sine.inOut` |
| impacto que bate e para (carimbo, etiqueta batendo) | `power4.in` curto (0,10 a 0,18 s) e o som no fim |
| saída rápida antes do corte | `power2.in` (0,2 a 0,3 s) |
| movimento contínuo (aproximação lenta da foto, persiana, rolagem) | `none` |
| pixel, VHS, máquina de escrever | `steps(n)` |
| salto com graça (selo, ícone) | `back.out(1.7)` a `back.out(2)`, só em coisa pequena |

`power4.in` e `power2.in` aqui não contradizem o "nunca ease-in" do Emil: na interface o problema é atrasar a resposta
ao clique. No vídeo, a aceleração até o contato é o que faz o impacto parecer peso, e a saída acelerada some antes do corte.
Fora desses dois casos, entrada é sempre `.out`.

## 4. Duração

| o quê | duração |
|---|---|
| carimbo, impacto, glitch | 0,10 a 0,18 s |
| entrada de texto ou cartão | 0,25 a 0,45 s |
| troca de cena | 0,3 a 0,6 s |
| movimento de câmera entre quadros | 0,6 a 1,2 s |
| aproximação lenta da foto | a cena inteira |

O texto tem que estar parado e legível pelo menos 1,2 s antes da fala acabar. Se a fala é curta, encurte a entrada,
não a leitura.

## 5. Várias coisas entrando

Nunca tudo de uma vez: uma de cada vez, com 0,06 a 0,12 s entre elas (no vídeo o olho precisa de um pouco mais que
os 30 a 80 ms de interface). Itens de lista que respondem à fala entram na palavra, não em escada automática.
Use `stagger` quando é a mesma animação em vários elementos, em vez de vários tweens com atraso manual.

## 6. Linha do tempo (GSAP)

- Tudo numa `gsap.timeline()` com tempos absolutos (o 3º argumento): a montagem sincroniza com a fala e o render
  procura quadro a quadro. Nada de `delay` encadeado nem `setTimeout`.
- Quando dois `fromTo()` mexem na mesma propriedade do mesmo elemento, o segundo leva `immediateRender: false`;
  sem isso o primeiro some antes de aparecer.
- Sai do jeito que entrou: o que entrou pela direita sai pela direita (ou some no lugar, num corte).
- Nada de `repeat: -1` solto: loop tem fim dentro da cena.

## 7. Conferir

Antes de entregar, olhe os quadros no meio de cada entrada (o `estilos.py testar` gera a folha). Procure: texto ainda
se mexendo quando a fala acaba, duas coisas entrando juntas, fonte tremendo, algo saindo de escala zero.
