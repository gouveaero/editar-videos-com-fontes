# editar-videos-com-fontes

Skill pessoal de edição de vídeos com apresentador, legendas sincronizadas e capturas reais de fontes. Motor local em Python, FFmpeg e HyperFrames, com perfil visual e testes de regressão.

Este repositório é **privado** e inclui dois componentes gravados por Gabriel e seis quadros de referência necessários aos testes. Esses arquivos não são modelos de conteúdo para inserir em novos vídeos.

## Instalar a skill

Para uma instalação nova no Codex:

```sh
git clone git@github.com:gouveaero/editar-videos-com-fontes.git ~/.codex/skills/editar-videos-com-fontes
```

Se a pasta já existe, preserve-a e clone em outro diretório antes de comparar as versões. Para Claude Code, o diretório de instalação é `~/.claude/skills/editar-videos-com-fontes`.

Invoque com `$editar-videos-com-fontes` ou consulte [SKILL.md](SKILL.md).

## Dependências

- Python 3.10+ e Pillow (versão usada nos testes em `requirements.txt`).
- FFmpeg e ffprobe no PATH; ambiente testado com FFmpeg 8.1.1.
- Node.js/npm para executar HyperFrames **0.8.33**, fixado pelo motor.
- Fonte e GSAP usados na composição estão incluídos em `assets/`.

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

O primeiro render pode baixar HyperFrames via npm. O processamento dos vídeos ocorre localmente.

## Editar e exportar

O [contrato do projeto](references/projeto.md) explica o JSON, as fontes de mídia, os cortes e as legendas.

```sh
python3 scripts/video_pipeline.py validate /caminho/projeto.json
python3 scripts/video_pipeline.py render /caminho/projeto.json
python3 scripts/video_pipeline.py verify /caminho/projeto.json
python3 scripts/package_project.py /caminho/projeto.json --caption /caminho/post.txt --review /caminho/review.json
```

O pacote inclui MP4, SRT, galeria, texto de publicação e composições editáveis com mídia. `prepare_evidence.py` recorta capturas e destaca passagens sem redesenhar as letras; `import_words.py` importa tempos por palavra do áudio editado.

## Verificar alterações no motor

```sh
python3 scripts/check_invariants.py
python3 scripts/regression.py --output qa-output
```

Os testes incluem colisões com o rosto, tamanho e tempos das legendas, procedência, preservação de pixels no marca-texto e invalidação do cache. A regressão reproduz dois componentes reais, compara seis quadros com a entrega aprovada e verifica três MP4, incluindo concatenação.

Os resultados da validação anterior estão em [validation-results.json](references/validation-results.json). Eles registram o código testado naquele momento; não substituem executar os testes após mudanças. Critérios e limites em [validacao.md](references/validacao.md).

## Organização

- `scripts/`: edição, composição, importação, evidências, pacote e testes.
- `assets/style.json` e `assets/composition.css`: padrão visual.
- `assets/benchmark/`: materiais de regressão privados.
- `references/`: contrato, perfil, evidências e validação.

A seleção de falas e fontes requer revisão editorial. A automação estabiliza a execução das decisões e verifica os casos cobertos pelos testes.

## Recursos de terceiros

Os recursos mantêm seus direitos e condições originais: Arial Bold, GSAP (aviso de licença no próprio arquivo), capturas das publicações e a foto de datacenter de Carl Lender, CC BY 2.0. URLs e identificação das fontes estão no manifesto de benchmark. O armazenamento neste repositório privado não concede permissão para redistribuir publicamente esses recursos.
