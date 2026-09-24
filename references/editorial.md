# Contrato editorial executável

O projeto continua `schema_version: 2`. `editorial_pipeline.py` estende o motor básico; sem cenas/framing/SFX, prefira o comando básico para reproduzir um projeto antigo. Os campos abaixo são dados, não código a copiar de um assunto anterior.

```sh
python3 scripts/editorial_pipeline.py validate /projeto/project.json
python3 scripts/editorial_pipeline.py build /projeto/project.json
python3 scripts/editorial_pipeline.py render /projeto/project.json
python3 scripts/editorial_pipeline.py verify /projeto/project.json
python3 scripts/package_project.py /projeto/project.json --caption /projeto/post.txt --review /projeto/review.json
```

`build/build.json` aponta para as composições ativas. Faça snapshots antes do lote. `render` reutiliza o motor de cortes, legendas, concatenação e QA técnico; o pacote detecta os campos editoriais automaticamente. O modo básico conserva seus invariantes e testes antigos.

## Configuração mínima ilustrativa

Acrescente ao JSON básico, substituindo conteúdo, tempos, arquivos e geometria pelos medidos no vídeo:

```json
{
  "editorial": {
    "palette": {"ink":"#142f35","paper":"#f6f3eb","gold":"#bb9250"},
    "sounds": {
      "clique": {
        "file":"sons/clique.wav",
        "source":"Banco fornecido pelo usuário; item identificado",
        "license":"Conforme metadados do arquivo; não informada quando ausente",
        "trim_in":0.02,
        "duration":0.18,
        "peak_dbfs":-27
      }
    }
  }
}
```

No **componente**:

```json
{
  "framing":{"scale":1.25,"origin":[0.5,0.8]},
  "face_bounds":[260,680,840,1320],
  "caption_highlights":["construir"],
  "scenes":[
    {"type":"word","start":1.2,"end":2.1,"title":"Estudar","rect":[60,250,1020,520]},
    {"type":"image","start":2.4,"end":4.8,"asset":"foto","title":"Legenda breve","credit":"Autor e licença"}
  ],
  "sfx":[{"sound":"clique","start":2.4,"gain":0.8}],
  "music_duck":[{"start":6,"end":8,"gain":0.35}]
}
```

Os valores de exemplo não são um preset de rosto: o zoom pode aproximar o cabelo do título, e a validação deve rejeitar essa sobreposição. Ajuste `rect` ou meça outro enquadramento. `framing.origin` é normalizado 0–1. `framing.measured_face_bounds` pode registrar a caixa já medida no quadro final, substituindo a estimativa geométrica. `face_bounds` do componente continua sendo a caixa na fonte normalizada antes do deslocamento/zoom. Não aumente tolerâncias para esconder conflito.

`rect` usa **[esquerda, topo, direita, base]**, não largura/altura. Cenas de overlay ficam entre y=250 e o limite das legendas e não podem cobrir o rosto. Cenas não se sobrepõem no mesmo componente; combinam internamente os elementos necessários. Os tempos são locais ao componente final. O gancho e o corpo conservam relógios próprios; a montagem calcula o deslocamento de cada um.

## Tipos de cena

| `type` | Campos específicos | Comportamento |
|---|---|---|
| `image` | `asset`, `title`, `credit`, `mode` opcional | Uma imagem inteira e proporcional; `full` é padrão. `overlay` usa `rect`. |
| `evidence` | `asset`, `claim`, `relation`, `mode` | Captura real; `overlay` é padrão, `full` disponível. Origem vem de `assets`. `text_height_px` permite checar legibilidade. |
| `title` | `title`, `copy` opcional | Título e apoio curtos. `on_dark: true` melhora contraste sobre roupa/fundo escuro. |
| `word` | `title` | Palavra grande, sublinhado discreto. |
| `connections` | três `labels`, `copy` | Conexão animada entre três conceitos curtos. |
| `bar` | `title`, `value`, `reference`, `reference_label`, `label` opcional | Pontuação proporcional a referência explícita; não confundir com melhora percentual. |
| `prototype` | `title`, `footer`, `copy`, `states` | Navegação e mudanças de estado testáveis. |
| `pendulum` | `title`, `footer`, `copy`, `physics` | Modelo de pêndulo com controle real e playback determinístico. |
| `chronology` | `title`, `footer`, `copy`, `events` | Acontecimentos selecionáveis com documentos reais de exemplo. |

Textos aceitam `\n` para quebra intencional e são escapados como texto, não HTML. `caption_highlights` marca termos exatos sem mudar o conteúdo da legenda. Evite realçar muitas palavras. O SRT permanece texto simples.

### Demonstrações

Todo componente que usa uma demo deve declarar `demo_crop: [x1,y1,x2,y2]`, medido **na fonte**. A imagem recortada ocupa a janela abaixo da área de trabalho; o motor verifica a caixa de rosto quando fornecida. Esse recorte não deve ser copiado de outra gravação. O rótulo “Exemplo ilustrativo” é incluído nos três modelos.

`prototype.states` contém `id`, `at` (segundos relativos), `title`, `label`/`body` opcionais, `next`/`button` para navegar; `wireframe: true` representa um esboço. Primeiro estado em `at: 0`, IDs únicos, destinos existentes.

```json
{"states":[
  {"id":"inicio","at":0,"title":"Escolha uma opção","next":"resultado","button":"Ver resultado"},
  {"id":"resultado","at":2,"title":"Resultado disponível","body":"Consequência da ação","next":"inicio","button":"Voltar"}
]}
```

`pendulum.physics`: `length_from` e `length_to` (m, positivos), `gravity` (m/s², padrão 9,81), `change_at` (segundos locais). `clock_rate` existe para retiming de uma demo já acelerada; normalmente deixe 1. O valor físico T usa L/g real; o relógio da animação pode ser acelerado sem reescrever a física.

`chronology.events`: `id`, `at`, `date`, `label`, `document: {title, body, href, label?}`. `href` aponta para um **arquivo local existente e independente** (HTML autocontido, texto ou PDF). As fixtures seguem no ZIP. Não crie links vazios ou dependências remotas para simular um documento. Para um fluxo real de cliente com outras necessidades, adapte os modelos locais e seus testes; nunca apresente dados fictícios como documento verdadeiro.

Interação e playback usam o mesmo modelo em `demo_runtime.js`. No player/teste próprio, use `tl.seek(tempo, false)` para executar os callbacks determinísticos; o padrão de GSAP suprime eventos. Em automação de navegador, não retorne o objeto timeline de `evaluate`: ele é um thenable e, pausado, pode ficar aguardando indefinidamente. Teste cliques, controle e documento em uma prévia local. No vídeo exportado, controles são pixels; entregue o HTML quando a demonstração funcional também fizer parte do pedido.

## Recursos, som e cache

Arquivos de imagem ficam em `assets` com `file`, `source_name`, `source_url`, `kind`; os mesmos requisitos de evidência básica continuam válidos. Uma fotografia grande é reduzida apenas na cópia de render; a fonte original acompanha o pacote. CSS, modelos, fontes, mídia, sons e documentos entram na assinatura de construção. Alterar enquadramento ou eventos invalida o render correspondente.

O motor usa os sons selecionados no JSON e gera faixas PCM de efeito por componente em `build/audio/`. O volume alvo incide sobre o fragmento realmente selecionado. `sfx.start` é tempo do componente final; o ataque precisa coincidir com a ação. `music_duck` só modifica a música durante os intervalos especificados, preservando a voz. Música ausente é válida. Não use o limiter para esconder uma mixagem excessiva.

## Portabilidade

O ZIP editorial contém `project/project.json`, composições com mídia, originais de apoio, documentos, sons, faixas separadas, fontes/licenças e motor em `project/skill/`. Para reconstruir após extrair:

```sh
python3 project/skill/scripts/editorial_pipeline.py render project/project.json
```

Requer Python 3.9+ com Pillow, FFmpeg/FFprobe, Node/npm e HyperFrames 0.8.33. Não requer a pasta do vídeo de polímatas, caminhos pessoais de fontes, outra skill ou DaVinci. Não promete projetos `.drp` ou edição nativa no Resolve. Inclua `edit_plan.json`, `retime.json` e `CREDITS.md` no projeto quando aplicáveis; o empacotador os leva junto.

`scripts/check_editorial.py --output /nova/pasta/qa --render` cria fixtures a partir do benchmark local, testa erros observáveis, modelos das demos, alteração de cache, retiming real, exportação e snapshots. As falas do benchmark não ilustram os textos de teste; esses MP4 são QA técnico, não material para publicar.
