# editar-videos-com-fontes

Skill pessoal de edição de vídeos com apresentador, cortes naturais, legendas sincronizadas, fontes reais, imagens grandes, demonstrações animadas e efeitos sonoros. Inclui direção visual, tipografia e componentes próprios, sem depender da Impeccable ou de outra skill de design. Motor local em Python, FFmpeg e HyperFrames, com testes de regressão.

Os testes incluem dois componentes gravados por Gabriel e seis quadros de referência. Esses arquivos são fixtures de regressão; não são modelos de conteúdo para inserir em novos vídeos.

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
- Fontes, GSAP, estilos e modelos das demonstrações estão incluídos em `assets/`. As fontes Newsreader e Source Sans 3 acompanham suas licenças OFL.

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

O primeiro render pode baixar HyperFrames via npm. O processamento dos vídeos ocorre localmente.

## Editar e exportar

O [contrato básico](references/projeto.md) explica mídia, cortes e legendas. Para o acabamento atual, use o [contrato editorial](references/editorial.md): enquadramento por tomada, imagens grandes, títulos, gráficos, protótipo navegável, pêndulo, cronologia com documentos e efeitos sonoros. Leia também [direção visual](references/direcao-visual.md) e [cortes e som](references/audio-e-tempo.md).

```sh
python3 scripts/editorial_pipeline.py validate /caminho/projeto.json
python3 scripts/editorial_pipeline.py render /caminho/projeto.json
python3 scripts/editorial_pipeline.py verify /caminho/projeto.json
python3 scripts/package_project.py /caminho/projeto.json --caption /caminho/post.txt --review /caminho/review.json
```

O pacote editorial inclui MP4, SRT, galeria, texto de publicação, composições editáveis, mídia, fontes, sons, documentos e o motor necessário para reconstrução. Não exige DaVinci Resolve. O modo básico `video_pipeline.py` continua disponível para montagens simples e reprodução de projetos anteriores.

`prepare_evidence.py` recorta capturas e destaca passagens sem redesenhar as letras; `import_words.py` importa tempos por palavra. `inspect_audio.py` gera trechos de escuta, forma de onda e espectrograma para decidir cortes de respiração. `retime_project.py` cria outra revisão, deslocando fala, legendas, cenas e sons pelo mesmo mapa de tempo. A velocidade padrão é 1×; aceleração depende do pedido.

## Verificar alterações no motor

```sh
python3 scripts/check_invariants.py
python3 scripts/regression.py --output qa-output
python3 scripts/check_editorial.py --output editorial-qa --render
```

Os testes incluem colisões com o rosto, tamanho e tempos das legendas, procedência, preservação de pixels no marca-texto e invalidação do cache. A regressão reproduz dois componentes reais, compara seis quadros com a entrega aprovada e verifica três MP4, incluindo concatenação.

A verificação editorial também cobre colisões com o rosto, navegação, documentos, física, sons, cache e sincronização após cortes e mudança de velocidade. Os controles das demos e a reconstrução do pacote têm verificações próprias descritas em [validacao.md](references/validacao.md).

Os resultados anteriores estão em [validation-results.json](references/validation-results.json) e [editorial-validation.json](references/editorial-validation.json). Eles registram o código testado naquele momento; não substituem executar os testes após mudanças. Critérios e limites em [validacao.md](references/validacao.md).

## Organização

- `scripts/`: edição, composição, importação, evidências, pacote e testes.
- `assets/editorial/`: estilos, fontes e modelos funcionais do modo editorial.
- `assets/style.json` e `assets/composition.css`: padrão visual original preservado.
- `assets/benchmark/`: materiais de regressão.
- `references/`: contrato, perfil, evidências e validação.

A seleção de falas e fontes requer revisão editorial. A automação estabiliza a execução das decisões e verifica os casos cobertos pelos testes.

## Recursos de terceiros

Os recursos mantêm seus direitos e condições originais: Arial Bold, GSAP (aviso de licença no próprio arquivo), capturas das publicações e a foto de datacenter de Carl Lender, CC BY 2.0. URLs e identificação das fontes estão no manifesto de benchmark. A disponibilidade neste repositório não altera as licenças desses recursos. Newsreader e Source Sans 3 incluem os respectivos arquivos OFL em `assets/editorial/fonts/`.
