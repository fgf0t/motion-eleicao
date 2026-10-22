---
name: motion-eleicao
description: Faz vídeo motion 9:16 sobre a eleição (Reels, TikTok, Shorts) de graça, a partir de uma pauta. Use quando a pessoa pedir "faz um vídeo sobre...", "vídeo motion", "vídeo sobre a eleição", "vídeo de campanha", "estilo dossiê", "estilo VHS", "estilo pesquise", "vídeo com dados", "estilo pixel", "quais estilos tem?", ou mandar uma referência pedindo "cria um estilo assim". Você pesquisa os fatos com fonte e escreve um roteiro.json; os scripts fazem voz, fotos livres, montagem e render sozinhos.
---

# motion-eleicao

Você só faz duas coisas: **pesquisar os fatos** e **escrever o `roteiro.json`**. Depois roda um comando.
Os scripts desta pasta fazem o resto sozinhos (narração, fotos livres do Wikimedia Commons, retícula,
animação no HyperFrames, render). Não edite os scripts nem o HTML gerado.

A pasta desta skill é a pasta onde está este `SKILL.md` (no Claude Code: `~/.claude/skills/motion-eleicao`;
no Codex: `~/.codex/skills/motion-eleicao`). Abaixo ela aparece como `SKILL`: nos comandos, troque `SKILL`
pelo caminho completo dessa pasta.

## Passo 0. Primeira vez

Rode `python3 SKILL/scripts/estilos.py primeira-vez`. Ele só imprime alguma coisa na primeira vez que a skill é usada
neste computador. Se imprimir as boas-vindas, mostre esse texto pra pessoa
(com as suas palavras, curto) junto com a imagem `SKILL/estilos/galeria.jpg`. Se não imprimir nada, siga.

## Passo 1. Entender o pedido

Você precisa de: a **pauta** (o assunto) e o **estilo**. Se a pessoa não disse o estilo, escolha pelo cardápio e diga
qual escolheu. Pergunte só se a pauta não estiver clara.

**Cardápio**: `python3 SKILL/scripts/estilos.py` lista cada estilo com nome, quando usar, uma frase e a imagem de
exemplo (`SKILL/estilos/<nome>/exemplo.jpg`). Se a pessoa perguntar "quais estilos tem?", rode e mostre a lista e a
imagem `SKILL/estilos/galeria.jpg`. Os estilos que vêm com a skill:

| estilo | quando usar |
|---|---|
| `dossie` | denúncia, contradição, "o que ele disse x o que fez" |
| `vhs` | caso grave, tom sério e sombrio |
| `pesquise` | "não acredita em mim? pesquisa", perguntas e respostas |
| `dados` | 2 a 4 números oficiais (economia, emprego, segurança) |
| `pixel` | explicar dados e regras passo a passo, com ícones, linha do tempo ou gráfico |

**Pautas prontas**: se a pessoa pediu um vídeo sem dizer a pauta, rode `python3 SKILL/scripts/estilos.py pautas` e pergunte:
"Quer fazer sobre uma destas (fatos já checados) ou sobre outra pauta?", mostrando a lista com uma linha cada.
Se ela escolher uma, use `SKILL/pautas/<nome>/roteiro.json` (copie pra pasta dela, pode trocar o estilo) e leia o
`fatos.md` junto: os fatos foram checados em 19 e 20/10/2026 e podem mudar; avise e, se puder, confira de novo.
As falas das pautas não têm nome de político (o Gemini bloqueia); com outra voz, pode pôr o nome se ela quiser.

Se a pessoa mandou **referência** (imagem, print, vídeo ou link) pedindo um estilo novo, vá pra "Estilo novo" no fim.

## Passo 2. Pesquisar (regra eleitoral, não pule)

- Todo fato, número e citação precisa de **fonte**: veículo ou órgão + data (ex.: `"IBGE, PNAD Contínua, 4º tri 2025"`,
  `"Folha de S.Paulo, 12/10/2026"`). Se a pessoa já mandou os fatos com fonte, use esses. Se não, pesquise na web
  (se puder) e confira. Se não achar fonte, **não use o fato**.
- Nunca chame ninguém de criminoso, ladrão, bandido, corrupto, miliciano, assassino sem **condenação definitiva**.
  Use o fato verificável: "denunciado pelo Ministério Público", "investigado", "réu", "acusado", "condenado em 1ª instância".
- Não invente número, data, frase nem cena. Citação só se for literal e com fonte.
- O vídeo é conteúdo orgânico: **não** é pra impulsionamento pago.

## Passo 3. Escrever o roteiro.json

Crie uma pasta pro vídeo dentro da pasta onde a pessoa está trabalhando (ex.: `videos/desemprego/`) e salve lá
o `roteiro.json`. Comece copiando o exemplo do estilo escolhido em `SKILL/exemplos/` (`dossie-*.json`,
`vhs-*.json`, `pesquise-*.json`, `dados-*.json`, `pixel-*.json`) e troque o conteúdo todo pelo da pauta.
**Apague todos os fatos do exemplo**: só entra no vídeo o que veio da pauta e da sua pesquisa.

```json
{
  "titulo": "desemprego em queda",
  "estilo": "dados",
  "chapeu": "2º turno · 25/10",
  "cenas": [
    {"fala": "Três números pra você levar pra urna.", "tela": "3 números", "foto": "ballot box Brazil"},
    {"fala": "O desemprego fechou 2025 em 5,1%, o menor desde 2012.", "tela": "Desemprego", "numero": "5,1%",
     "carimbo": "menor desde 2012", "fonte": "IBGE, PNAD Contínua", "foto": "carteira de trabalho"},
    {"fala": "Não acredita? Pesquisa. Dia 25, vota sabendo.", "tela": "Vota sabendo", "detalhe": "Dia 25 · 2º turno"}
  ],
  "assinatura": "Feito por @seu_perfil, eleitor · sem impulsionamento"
}
```

### Regras do roteiro

- **4 a 7 cenas** (o vídeo fica entre 20 e 45 segundos; não precisa encher). Uma ideia por cena.
- `fala`: o que a voz diz. Frase curta, falada, até 25 palavras. Pode escrever número com algarismo ("5,1%", "2025").
- `tela`: 1 a 4 palavras, o título grande da cena. Não repita a fala inteira.
- A **primeira cena** é o gancho (pergunta ou afirmação forte, sem número).
- A **última cena** é o fecho, com a chamada que a pessoa pedir (se ela não pediu, use uma neutra como
  "Confira as fontes antes de repassar."). Chamada curta ("Dia 25, vota sabendo."), com `tela` curta e `detalhe` opcional.
  Na última cena não ponha número nem foto.
- `numero`, `carimbo` e `citacao` **exigem** `fonte`. O script recusa o roteiro se faltar.

### Campos de cada cena (só `fala` é obrigatório)

| campo | o que é | exemplo |
|---|---|---|
| `fala` | texto narrado (vira a legenda) | `"O desemprego caiu pra 5,1%."` |
| `tela` | título grande, 1 a 4 palavras | `"Desemprego"` |
| `numero` | o número que bate na tela | `"5,1%"`, `"R$ 6 mi"`, `"8,7 mi"` |
| `detalhe` | linha pequena de apoio | `"no fim de 2025"` |
| `carimbo` | selo curto que bate no fim da fala | `"menor desde 2012"`, `"negado"` |
| `fonte` | fonte do fato da cena | `"IBGE, PNAD Contínua"` |
| `citacao` + `quem` | frase literal entre aspas e quem disse (com data) | `"Não tenho nada a esconder."`, `"Fulano, debate da Band, 18/10/2026"` |
| `lista` | respostas que aparecem uma a uma: `[{"q": "...", "a": "...", "fonte": "..."}]` | ver `exemplos/` |
| `foto` | foto do **acervo** da skill: `"acervo:cadeado"` (lista abaixo). Commons só se a pessoa pedir: `"commons: termo"` ou `"File:Nome.jpg"`. Ou um arquivo dela ao lado do roteiro | `"acervo:urna"` |
| `manchete` | estilo `vhs`: link da matéria; a skill lê só o título, o veículo e a data e desenha o recorte de jornal (sem a foto da matéria), com "Reprodução: veículo, data" na tela. Manchete que acusa sem condenação é recusada | `"https://www.poder360.com.br/..."` |
| `desenho` | estilo `vhs`, cena sem foto: objeto desenhado em código (porta, corredor, mesa, envelope, cadeado, cracha, medalha, cartuchos, martelo, predio, arquivo, relogio, urna, casa); sem isso ele escolhe pela cena | `"medalha"` |
| `foto_corte` | corta a foto antes de usar (frações x0, y0, x1, y1): tira placa, texto, logo | `[0.2, 0.33, 0.8, 0.97]` |
| `seta` | só no estilo `dados`: `"cima"` ou `"baixo"` | `"baixo"` |
| `ressalva` | estilos `dados` e `pixel`: nota honesta em amarelo | `"Mas o feminicídio subiu 4%."` |
| `icone` | só no `pixel`: carrinho, documento, bolo, calendario, moedas, cifrao, lupa, pessoa, casa, urna, predio, cadeado, dinheiro, balanca, alerta, grafico (sem isso ele escolhe pela fala) | `"moedas"` |
| `grade` | só no `pixel`: ícones em grade com alguns destacados em amarelo | `{"icone": "pessoa", "total": 20, "destaque": 1, "texto": "1 em cada 20"}` |
| `escada` | só no `pixel`: boneco subindo uma escada (melhora, subida) | `true` |
| `grafico` | só no `pixel`, exige `fonte`: linha em degraus com dados REAIS da fonte | `{"rotulos": ["2004", "2026"], "series": [{"nome": "com ganho real", "valores": [260, 1621], "rotulo_final": "R$ 1.621"}]}` |
| `linha_tempo` | só no `pixel`, exige `fonte`: marcos em ordem | `[{"ano": "2023", "texto": "lei aprovada"}, {"ano": "2024", "texto": "em vigor"}]` |
| `bate` | palavra da fala em que o número ou carimbo entra | `"menor"` |
| `clipe` | vídeo 9:16 gerado no Flow (ver "Modo Flow"), salvo ao lado do roteiro; cobre a cena com o título, a fonte e "cena gerada por IA" | `"clipes/c1.mp4"` |
| `fala_do_clipe` | `true` quando a narração da cena vem de dentro do `clipe` (voz do Flow); a `fala` tem que ser o que o clipe diz | `true` |
| `fala_voz` | só se a voz pronunciar errado: o texto que a voz lê (a legenda continua com `fala`) | `"Assembleia do Rio"` no lugar de `"Alerj"` |

`bate` é opcional: sem ele, o número entra quando a fala diz o número e o carimbo entra no fim da fala.
Se a busca da `foto` não achar nada livre, o script avisa e a cena sai sem foto (o vídeo continua).

Campos do topo: `titulo` (vira o nome do arquivo), `estilo`, `chapeu` (opcional, etiqueta do topo no `dossie`),
`data_vhs` (data na tela do `vhs`, ex. `"02.02.2021"`), `assinatura` (opcional) e `voz` (só se a pessoa pedir outra voz pra este vídeo, ver abaixo).

**Fotos: regra da skill.** A foto nunca pode trazer informação de outra pessoa ou de outro lugar: nada de rosto,
placa, legenda, texto legível ou lugar de outro país. Por isso a ordem é:
1. **Acervo conferido** (`SKILL/assets/acervo/`, já recortado e com crédito): `acervo:martelo` (justiça, júri, recurso),
   `acervo:cadeado` (sigilo, segredo), `acervo:cartuchos` (bala, munição, polícia), `acervo:urna` (eleição, voto),
   `acervo:mapa` (Brasil, dados nacionais, fome, pobreza), `acervo:plenario` (só Alerj / Palácio Tiradentes, Rio) e
   `acervo:praia` (só Copacabana, Rio, ou pauta de praia).
2. **Sem foto**: o estilo `vhs` desenha o objeto em código (campo `desenho`); os outros estilos ficam só com texto e grafismo.
3. **Commons** só se a pessoa pedir uma foto específica: `"commons: termo"` (a busca prefere o Brasil e descarta pessoa,
   placa, texto e outro país) ou `"File:Nome exato.jpg"`. Sempre confira na folha de fotos (Passo 4).
Não use foto de pessoa, nem de político.

### Voz

Não ponha `voz` no roteiro: vale a voz que a pessoa escolheu (passo "Voz da pessoa" abaixo). Só ponha se ela pedir
outra voz pra este vídeo:
- `{"motor": "sistema"}`: voz do computador;
- `{"motor": "kokoro", "voz": "pm_alex"}` (ou `pm_santa`, `pf_dora`): voz neural grátis no computador; o modelo
  (340 MB) baixa no primeiro uso. Ela lê sigla como palavra: use `fala_voz` com a sigla soletrada ("í bê gê é");
- `{"motor": "piper", "voz": "faber"}` (ou `cadu`, `jeff`): voz neural grátis e leve (60 MB por voz);
- `{"motor": "gemini", "voz": "Algenib"}`: a mais natural, com chave grátis (ver README); o vídeo inteiro sai num pedido só;
- `{"motor": "voicestudio", "perfil": "ID"}`: a voz da própria pessoa.
`velocidade` 1.05 a 1.1 fica mais ágil. Pra guardar uma delas como padrão: `python3 SKILL/scripts/voz_propria.py salvar kokoro pm_alex`.

## Voz da pessoa (na primeira vez que ela pedir um vídeo)

Rode `python3 SKILL/scripts/voz_propria.py status`. Se já tem voz salva, siga. Se não tem, a skill escolhe sozinha
(não precisa pôr `voz` no roteiro): com o VoiceStudio aberto, usa o **Narrador Grave** (voz sintética padrão, que ela
cria no VoiceStudio da pessoa na primeira vez; não é a voz de ninguém); sem VoiceStudio, usa a voz neural **Kokoro**;
por último, a voz do computador. Diga:
"Vou narrar com a voz padrão da skill. Mas fica bem melhor com a sua própria voz: soa mais natural e passa mais
confiança pra quem assiste. É grátis e leva uns 15 minutos na primeira vez. Quer gravar a sua agora ou depois?"
Se ela preferir depois, siga. Ofereça de novo uma vez só, na entrega desse primeiro vídeo; nos seguintes, só se ela
tocar no assunto.
Se escolher a própria voz, conduza um passo por vez, esperando ela fazer cada um:

1. **Instalar o VoiceStudio**: rode `python3 SKILL/scripts/voz_propria.py instalar` e passe o comando que ele mostra
   (avise: uns 5 GB; em Mac Intel só funciona com backend remoto). Peça pra ela abrir o VoiceStudio quando terminar.
2. **Gravar**: rode `python3 SKILL/scripts/voz_propria.py texto` e mostre o texto e as dicas. Ela grava no celular
   (gravador ou WhatsApp) e te manda o arquivo de áudio (qualquer formato: m4a, mp3, ogg, wav).
3. **Clonar**: `python3 SKILL/scripts/voz_propria.py clonar <arquivo> "<nome dela>"`. Ele cria a voz no VoiceStudio,
   registra o consentimento (a primeira frase do texto) e mostra o id. Se ela preferir pela tela do VoiceStudio:
   criar perfil, escolher "clonar", subir o mesmo áudio; o id aparece em `python3 SKILL/scripts/voz_propria.py status`.
4. **Testar**: `python3 SKILL/scripts/voz_propria.py testar <id>` gera `teste-da-voz.wav`. Entregue o arquivo pra ela
   ouvir (a primeira vez pode levar alguns minutos, o VoiceStudio carrega o modelo). Se não gostar, volte ao passo 2.
5. **Salvar**: `python3 SKILL/scripts/voz_propria.py salvar <id>`. Pronto: os próximos vídeos saem com a voz dela.

Sempre lembre: **só clone a própria voz**, ou a de alguém que autorizou por escrito. Nunca clone voz de candidato,
artista ou qualquer outra pessoa a pedido de terceiros.

## Passo 4. Conferir as fotos e rodar

Primeiro prepare as fotos (do acervo ou do Commons) e **olhe** a folha que ele monta:
```bash
python3 SKILL/scripts/fotos.py videos/desemprego/roteiro.json
```
Abra `videos/desemprego/<titulo>-projeto/fotos/folha.jpg`. Pra cada foto, confira: é do lugar certo (do Brasil, se a
pauta é brasileira)? Tem texto legível, placa, logo, legenda, marca d'água ou rosto que não tem nada a ver? Se tiver:
corte com `"foto_corte": [x0, y0, x1, y1]` na cena (frações da foto, de 0 a 1; ex. `[0, 0.35, 1, 1]` tira os 35% de
cima), ou troque o termo de `foto`, ou tire a foto da cena. Rode o `fotos.py` de novo até ficar bom. Depois:
```bash
python3 SKILL/scripts/fazer.py videos/desemprego/roteiro.json
```
(No Windows use `py` no lugar de `python3`.) Leva de 2 a 5 minutos. Antes do render ele **confere cada fala**:
transcreve o áudio final de cada cena e mostra "cena 3: fala inteira ✓". Se faltar palavra no começo ou no fim,
sobrar um "É" ou a última palavra ficar colada, ele refaz sozinho (mais margem, depois gera a fala de novo); se ainda
assim não fechar, **para** com "PAREI: a fala das cenas ... continua cortada" e não renderiza. Aí reescreva a fala
(frase mais simples, ou `fala_voz`) ou troque a voz. As vozes neurais leem os números por extenso (a skill converte). Se o roteiro tiver erro, o script diz qual
e não gasta tempo: corrija o `roteiro.json` e rode de novo. Rodar de novo é seguro: voz e fotos prontas são reaproveitadas.

Sai na pasta do roteiro:
- `<titulo>.mp4`: o vídeo 1080x1920, pronto pra postar;
- `<titulo>-fontes.txt`: fontes e créditos das fotos, pra colar na legenda do post;
- `<titulo>-projeto/`: o projeto (dá pra abrir com `npx hyperframes preview` dentro dela).

## Passo 5. Entregar

Mostre o caminho do vídeo e do `-fontes.txt` e lembre a pessoa de:
1. assistir antes de postar e conferir cada número com a fonte;
2. marcar "conteúdo feito com IA" na plataforma (a tela final já diz que a voz é sintética);
   no primeiro vídeo com a voz do computador, recomende trocar pela voz dela ("quero usar a minha voz"): fica mais natural
   e mais confiável;
3. não impulsionar (não pagar pra promover).

Na entrega do **primeiro** vídeo, se você consegue operar um navegador (Claude in Chrome, o navegador do app do Claude
ou outro que você tenha), ofereça uma vez: "Quer testar o modo Flow? Eu opero o seu navegador no Google Flow e gero
cenas em vídeo pro próximo, com narração. Gasta mais token, mas às vezes o Flow tem créditos grátis."
Se você não opera navegador, não ofereça. Se ela topar, siga "Modo Flow" abaixo.

## Modo Flow (opcional: cenas em vídeo geradas no Google Flow)

Peças mais robustas: algumas cenas viram vídeo de 8 s gerado no Flow (Google), com a narração dentro. Você opera o
navegador da pessoa; a montagem, a conferência das falas e o render continuam iguais.

**Antes de começar**, diga e espere ela responder:
1. Custo: cada clipe gasta créditos do Flow (uns 10 no Veo Lite, mais 1 da imagem de referência) e bastante token seu.
   Diga quantos clipes pretende fazer (2 a 4 por vídeo; todas as cenas, se for usar a voz do Flow em tudo) e o total de créditos.
2. Voz: "Sigo com a voz do Flow?" Se sim, a narração de cada clipe vem de dentro dele (`fala_do_clipe`), e as cenas sem
   clipe usam o Gemini com a mesma voz (`{"motor": "gemini", "voz": "Algenib"}`, chave grátis, ver README), pra não
   misturar vozes. Se não, os clipes entram mudos e a narração é a voz de sempre.
3. Conta: ela entra no Flow com a conta Google dela. **Você nunca digita senha** nem aceita termos por ela.

**Quem escolhe é a pessoa.** Mostre as cenas do roteiro e sugira onde um clipe faria sentido (o gancho, um lugar, um
objeto em movimento); cena de número, gráfico, lista ou citação costuma ficar melhor com o desenho do estilo. Ela decide
quais cenas viram clipe (ou nenhuma).

**O que vem do Flow é matéria-prima, não o vídeo pronto.** A montagem trata cada clipe na linguagem do estilo: no `vhs`
vira fita (esverdeado, chiado, desvio de cor, com PLAY e data por cima), no `dossie` e no `pesquise` vira preto e branco
granulado, no `pixel` vira pixel, no `dados` fica escuro atrás dos números. Mesmo assim, peça já perto da cara do estilo:
comece o pedido pelo campo `flow` de `SKILL/estilos/<estilo>/sobre.json` (estilo sem `flow`: descreva pela `descricao`).
Imagem do Flow também serve: salve ao lado do roteiro e use como `"foto": "flow-c3.png"` com `"foto_credito": "imagem gerada por IA (Google Flow)"`;
ela passa pelo mesmo tratamento das fotos e o crédito aparece na tela. Nas cenas de clipe a montagem tira os efeitos sonoros do estilo (bip, glitch, moeda): ali o som é a narração e a trilha.

**Regras dos clipes** (além das regras do Passo 2):
- Nada de pessoa real reconhecível: nem político, nem candidato, nem rosto de ninguém em close. Cena de objeto, lugar
  ou mãos. Imitar candidato com IA é proibido pela lei eleitoral.
- Nome de político na fala derruba a geração no Flow: escreva "o senador", "o candidato"; o nome vai na `tela`.
- Peça sem texto, sem letreiro, sem logo, sem bandeira de partido e sem número de candidato (a IA inventa letras erradas).
- A fala do clipe tem que caber em 8 s: até umas 18 palavras.
- O vídeo final marca "cena gerada por IA" em cada clipe, e a pessoa marca "feito com IA" na plataforma.

**Passo a passo no navegador:**
1. Abra https://labs.google/flow numa aba nova e peça pra ela entrar com a conta Google, se não estiver. Clique em
   "Novo projeto". Os pedidos vão no campo "O que você quer criar?" do agente, à direita; Enter envia.
2. Pra cada cena escolhida, **duas mensagens**, esperando cada uma terminar (olhe a tela a cada 10 a 20 s):
   primeiro a imagem de referência (`Gere 1 imagem com o Nano Banana 2.1, formato 9:16, <flow do estilo>: <a cena>. Sem pessoas, sem texto.`),
   depois o vídeo a partir dela (Veo 3.1 Lite, 8 s; o Veo Lite só põe voz se tiver imagem de referência).
   Pedindo os dois numa mensagem só, o agente costuma parar depois da imagem.
   Antes de gerar o vídeo o agente pergunta se aprova o custo: clique em "Aprovar" só se a pessoa já aceitou esse gasto
   (nunca em "Sempre aprovar"). Se ele oferecer sozinho um vídeo que você não pediu (sem a narração), clique em
   "Rejeitar" e mande o seu pedido. Com muita fila ele avisa que agendou: o vídeo aparece no projeto minutos depois.
   Pedido do vídeo, em português:
   `Vídeo 9:16 de 8 s, <flow do estilo>, câmera lenta se aproximando. <a cena>. Sem pessoas, sem texto na tela. Narração em português do Brasil,
   voz masculina grave (Algenib), falando exatamente: "<fala da cena>". Sem música.`
   Texto longo: clique no campo e digite (colar de uma vez às vezes falha). Se o Veo falhar duas vezes na mesma cena,
   tente o Omni Flash ou troque a cena; falha não gasta crédito.
3. Baixe cada vídeo: clique nele, no ícone de baixar (seta pra baixo, no alto) e em "720p". Ele cai na pasta Downloads;
   mova pra `clipes/c<N>.mp4` na pasta do roteiro (N = número da cena) e não deixe cópia em Downloads.
4. **Assista cada clipe** (tire 2 ou 3 quadros com ffmpeg e olhe): tem rosto, texto inventado ou logo? Refaça ou corte a cena.
   A fala tem que bater com a `fala` do roteiro; se o clipe disse diferente, escreva na `fala` o que ele disse de fato
   (se ainda for verdade e tiver fonte) ou gere de novo.
5. No roteiro: `"clipe": "clipes/c1.mp4"` na cena e, com a voz do Flow, `"fala_do_clipe": true`. Rode o `fazer.py`
   normalmente: ele confere as falas dos clipes também. Se parar em "PAREI" numa cena de clipe, gere o clipe de novo.

## Consertos rápidos

| problema | o que fazer |
|---|---|
| a voz pronuncia uma palavra errado | ponha `fala_voz` na cena com a grafia que soa certo |
| a foto veio errada | troque o termo de `foto` (em inglês) ou use `"File:Nome exato.jpg"` do commons.wikimedia.org; rode de novo |
| texto grande demais | encurte `tela` (1 a 4 palavras) |
| o número entra na hora errada | ponha `bate` com a palavra da fala em que ele deve entrar |
| "Não consegui falar com o VoiceStudio" | abra o VoiceStudio ou troque `motor` pra `sistema` |
| quer só ver sem renderizar | `python3 SKILL/scripts/fazer.py roteiro.json --sem-render` |

Mais efeitos sonoros: os sons vêm com a skill (gerados em código ou CC0). Se a pessoa quiser outro, com a chave grátis
dela do Freesound: `python3 SKILL/scripts/baixar_sons.py "whoosh fast" whoosh` (só baixa CC0; ver README).

Exemplos completos de cada estilo: `SKILL/exemplos/`.

**Mexer em animação**: antes de escrever ou mudar qualquer movimento em código (efeito novo num `estilo.py`, câmera,
transição, estilo novo que precise de mais que o `config.json`), leia `SKILL/estilos/_base/MOVIMENTO.md`: pra quê
animar, só transform e opacidade, qual curva e quanto tempo, uma coisa de cada vez.

## Estilo novo a partir de referências

Quando a pessoa mandar referências (links de Pinterest, Instagram, YouTube, imagens, prints ou um vídeo) e pedir um
estilo novo. Copie a **linguagem visual** (cores, texturas, tipografia, movimento), nunca o conteúdo, a marca, o logo
nem o @ de quem fez a referência.

1. Escolha um nome curto (ex.: `colagem-punk`) e rode:
   `python3 SKILL/scripts/referencia.py colagem-punk <ref1> [<ref2> ...]`
   (arquivo no computador ou link; ele baixa, tira quadros dos vídeos, mede paleta, grão e ritmo de corte).
2. **Olhe** a folha de contato `SKILL/estilos/<nome>/folha.jpg` (abra a imagem). Descreva pra pessoa, em 3 a 5 linhas:
   paleta, fundo e textura, tipografia, como as coisas entram e como troca de cena.
3. Ajuste `SKILL/estilos/<nome>/config.json` pra ficar parecido. Em `SKILL/estilos/_base/config-modelo.json`,
   o bloco `_opcoes` explica o que cada valor faz; use só esses valores. A paleta automática pode errar (uma cor forte
   que ocupa pouco espaço, como um amarelo de tarja, às vezes fica de fora): confira olhando a folha e corrija.
   Pra colagem, use `"fonte_titulo": "Recortada"`, `"camadas"` (retalhos, amassado, formas, tarjas) e `"foto": {"modo": "tiras"}`.
   Se a referência pede um movimento que as opções não têm e você for escrever código, siga `SKILL/estilos/_base/MOVIMENTO.md`.
4. Preencha `SKILL/estilos/<nome>/sobre.json`: `titulo`, `quando` (quando usar) e `descricao` (1 frase). Deixe
   `"status": "rascunho"`.
5. Rode `python3 SKILL/scripts/estilos.py testar <nome>`: renderiza um teste de uns 15 s (`teste.mp4`) e o quadro
   `exemplo.jpg` (o conteúdo do teste é sempre o mesmo, só pra comparar a cara). Abra o `exemplo.jpg` e compare com a
   `folha.jpg`. Se estiver claramente diferente, ajuste o config e teste de novo, no máximo 2 vezes por conta própria.
   Depois mostre o teste pra pessoa e diga o que ficou parecido e o que não dá pra imitar com as opções.
6. Se ela pedir mudança, ajuste o `config.json` e teste de novo. **Só quando ela aprovar**:
   `python3 SKILL/scripts/estilos.py aprovar <nome>`. Aí ele entra no cardápio e na galeria.

