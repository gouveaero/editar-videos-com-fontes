# Contrato básico do projeto e comandos

Este documento descreve o modo original de `video_pipeline.py`. Para o acabamento integrado com zoom, imagens grandes, demos e SFX, use [editorial.md](editorial.md) e `editorial_pipeline.py`. O contrato de fontes, componentes, quadros, legendas e variantes continua igual; as restrições de zoom 1 e imagens pequenas abaixo são exclusivas do modo básico.

O motor recebe dados; não contém nomes de notícias, tomadas ou durações de Gabriel no código. A versão do formato é `schema_version: 2`. Caminhos relativos são resolvidos a partir do JSON. Escolha sempre uma pasta de revisão nova; o diretório `output` é exclusivo para derivados. Os MP4 aprovados não são entradas a sobrescrever.

## Estrutura mínima

Exemplo de formato para um master já editado de 3 segundos. Os arquivos citados devem existir e os tempos devem vir do áudio real:

```json
{
  "schema_version": 2,
  "output": "build",
  "components": {
    "abertura": {
      "frames": 90,
      "master": "media/abertura.mp4",
      "captions": "captions/abertura.json",
      "shift_y": -80,
      "close": false,
      "face_bounds": [200, 740, 900, 1450],
      "evidence": [{
        "start": 0.1, "end": 2.8, "asset": "declaracao",
        "claim": "Afirmação exata dita neste intervalo.",
        "relation": "alegação atribuída ao autor"
      }]
    }
  },
  "assets": {
    "declaracao": {
      "file": "evidencias/declaracao-destacada.png",
      "source_url": "https://instituicao.example/declaracao",
      "source_name": "Nome do autor e da publicação",
      "kind": "screenshot",
      "text_height_px": 36
    }
  },
  "variants": [{"id": "principal", "title": "Principal", "components": ["abertura"]}]
}
```

`frames` é a duração exata a 30 fps. Variantes concatenam os IDs de componentes na ordem escolhida; o número de variantes não é fixo. `shift_y` é uma translação negativa em pixels, sem zoom. `close` escolhe o limite de 340 px para imagens. `face_bounds` é o envelope `[esquerda, topo, direita, base]` que engloba cabelo e barba no quadro 1080×1920 ANTES da translação. Meça nas tomadas; os números do exemplo não são uma detecção de rosto. Use um envelope que cubra a movimentação observada, e revise também as emendas. Sua ausência gera aviso de revisão manual, não uma falsa aprovação automática.

`kind` aceita `screenshot`, `photo` ou `diagram`. `text_height_px` é a altura observada das letras na captura original; quando fornecida, o motor rejeita escala que reduza essa altura para menos de 24 px. Isso detecta um caso de texto pequeno, mas não prova leitura boa em todos os celulares. Para novos recortes de parágrafos, meça e forneça esse valor. Para fotos, omita.

Cada legenda é um objeto `{ "start": 0.1, "end": 1.4, "text": "Fala realmente gravada.", "display_text": "Fala realmente\ngravada." }`. `display_text` é opcional; só pode mudar quebras de linha. O motor mede largura com a fonte incluída e rejeita texto que não caiba em duas linhas. O SRT usa as mesmas cues do render.

## Partindo dos brutos

Em vez de `master`, forneça `cuts` no componente e `sources` na raiz:

```json
{
  "sources": {"corpo": "brutos/corpo.mp4"},
  "cuts": [
    {"source": "corpo", "in": 13.0, "out": 22.67, "reason": "Frase completa; retirada apenas a preparação anterior."}
  ]
}
```

O fragmento acima ilustra os campos: `cuts` pertence ao componente, e `sources` à raiz. `frames` deve ser a soma de `round((out-in)*30)` dos cortes. O motor normaliza volume, mantém áudio estéreo 48 kHz, usa fades de 6–8 ms nas emendas e não aplica zoom. Gravação com proporção diferente de 9:16 pede decisão explícita de reenquadramento e outro perfil, em vez de distorção automática.

Primeiro gere masters. Transcreva cada master pelo áudio editado com tempos por palavra (Whisper local quando disponível); preserve o JSON bruto. Depois importe os tempos e revise nomes/números:

```sh
python3 scripts/video_pipeline.py masters /caminho/projeto.json
python3 scripts/import_words.py /caminho/projeto.json abertura /caminho/whisper-abertura.json
```

O importador não roda ASR e não sobrescreve cues existentes. Ele agrupa palavras por pausa, pontuação e largura. Os cortes de preparação e a seleção das melhores tomadas continuam sendo decisões editoriais, registradas no plano.

## Compor, renderizar e verificar

Execute a partir da pasta da skill (ou use caminhos absolutos dos scripts):

```sh
python3 scripts/video_pipeline.py validate /caminho/projeto.json
python3 scripts/video_pipeline.py build /caminho/projeto.json
python3 scripts/video_pipeline.py render /caminho/projeto.json
python3 scripts/video_pipeline.py verify /caminho/projeto.json
```

`build.json` aponta para as composições ativas. Use o diretório retornado para um snapshot no HyperFrames e revise a principal antes da exportação em lote. `render` também gera masters faltantes, composições e variantes. `verify` decodifica integralmente e verifica formato, quadros, duração, alinhamento inicial A/V e integridade. Em qualquer falha, leia o relatório e corrija a entrada ou implementação; não remova a verificação para concluir a entrega.

Os diretórios de composição são identificados por hash do código, CSS, fonte, GSAP, estilo, mídia, cues e programação de imagens. Renders só são reutilizados quando seu hash ainda coincide com o recibo. Arquivos finais ficam em `build/versions/`, com MP4, SRT e JSON de cues. `delivery.json` e `technical_qa.json` registram a saída e seus checks.

Música é opcional: `"music": {"file": "audio/trilha.wav", "gain": 0.1}`. O ganho é linear, não LUFS; depende do nível do arquivo. Ouça o mix. Sem esse campo, a fala segue sem música. O motor aplica fade de entrada e saída na trilha. A troca entre duas camas musicais da primeira edição não está embutida no motor geral.

## Ambiente fixado

`assets/style.json` contém o perfil; `assets/composition.css`, a composição; `assets/ArialBold.ttf` e `assets/gsap.min.js`, os recursos usados na entrega aprovada. `assets/runtime-lock.json` registra as versões testadas. O comando chama **HyperFrames 0.8.33**, não `latest`. FFmpeg/ffprobe e Pillow precisam existir no ambiente. A troca de versão do renderizador, fonte ou CSS deve passar pela regressão antes de ser adotada como novo padrão.

É possível alterar valores em `style` no JSON, mas mudanças devem ser intencionais e comparadas com a referência. O motor atual se restringe a 1080×1920/30 e zoom 1; outro formato exige um perfil separado e validação correspondente.

## Galeria, ZIP e projeto portátil

Após a verificação técnica e a revisão das cenas, use:

```sh
python3 scripts/package_project.py /caminho/projeto.json --caption /caminho/post.txt --review /caminho/review.json
```

`review.json` é uma lista com um registro por variante: `id`, `speech_note`, `visual_note`, `evidence_note` e `checked_frames` (lista de caminhos de quadros, relativos ao próprio arquivo de revisão). Escreva as observações após conferir os materiais; isso é registro do trabalho do agente, não confirmação adicional do usuário. O empacotador verifica que os quadros existem e que há notas, mas não substitui a inspeção real.

O resultado contém `assistir.html`, `delivery.zip`, os MP4 e SRT, o texto do post e créditos. O ZIP inclui composições HyperFrames com fonte, imagens, JavaScript e vídeo de cada componente, além de um `project.json` com caminhos relativos. Pode ser editado sem a pasta original da primeira entrega. Para remontar por JSON, use a skill instalada; para editar cada composição, use seu `index.html` no HyperFrames.
