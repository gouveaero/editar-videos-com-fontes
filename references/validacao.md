# O que sustenta a consistência

## Camada editorial integrada

`python3 scripts/check_editorial.py --output /nova/pasta/editorial-qa --render` testa recusa de texto sobre o rosto, destinos de navegação inexistentes, documento ausente, SFX fora da duração, cenas sobrepostas e física inválida. Testa o mapa comum de tempo em cortes/velocidade/cues/palavras/estados/sons, bloqueio de palavra cortada, mudança da assinatura de cache ao alterar zoom, período físico do pêndulo, navegação e seleção de documentos. Executa um retiming FFmpeg real e verifica quadros/amostras; depois renderiza e decodifica as fixtures.

Inspecione os snapshots, inclusive início, meio e fim das demos e o rosto na janela. Testes dos modelos não substituem testar os controles na prévia. Para a fixture, `check_demo_ui.cjs` abre Chrome headless novo e executa cliques reais, slider, abertura do documento e busca para trás: `node scripts/check_demo_ui.cjs /caminho/puppeteer-core /caminho/chrome /qa/project.json`. Use os caminhos do runtime local disponível; o teste não controla a sessão de navegação do usuário. Meça pico e escute o mix; confira amostras de cada emenda gancho/corpo. Verifique que todas as variantes usam o mesmo corpo corrigido e que legendas/efeitos foram deslocados junto.

Teste o ZIP extraído em outro diretório: construa as composições com o motor incluído, abra documentos e confirme fontes/mídia/sons online. O pacote não pode depender de `revisao_06`, da pasta da skill instalada ou do banco original de efeitos.

O motor básico e seus benchmarks continuam sendo a prova de compatibilidade. Não altere os quadros de referência ou tolerâncias para fazer a nova camada passar. O preset editorial tem aparência própria; seus testes visuais são separados.


## Verificações reproduzíveis

`scripts/check_invariants.py` exercita falhas observáveis: zoom adicional, componente inexistente, imagens sobre o cabelo, legendas sobre a barba, procedência ausente, captura ilegível na escala final, cues sobrepostas, palavras inventadas na exibição e tentativa de sobrescrever legendas revisadas. Também verifica a importação de tempos reais por palavra e a invalidação do cache quando muda o enquadramento.

`scripts/regression.py --output /nova/pasta/qa` usa dois componentes REAIS da entrega aprovada: a abertura principal e o gancho mais próximo sobre superpotência. Os arquivos locais necessários estão em `assets/benchmark/`; não dependem da pasta antiga ou de links na internet. A regressão renderiza novamente, monta MP4 e SRT, decodifica as saídas e compara seis quadros com os originais incluídos. A variante `combined` exercita também a concatenação de dois componentes.

O comparador usa imagens 540×960, erro médio absoluto de até 2/255 por canal e até 3/255 na região das legendas. A tolerância admite pequenas diferenças de codec; não admite deliberadamente mudanças de enquadramento ou tipografia. A folha `comparison.jpg` mostra aprovado à esquerda e reprodução à direita. Inspecione-a: um número pequeno não prova que todo detalhe está correto. Se uma alteração de estilo for intencional, registre-a e revise novos quadros antes de trocar o padrão; não relaxe o limite só para fazer o teste passar.

Os benchmarks contêm cópias locais da gravação de Gabriel, fontes e recortes já utilizados. São material privado de teste dentro da skill. Não são exemplos de conteúdo para inserir em novos vídeos e não precisam ser enviados a serviços externos. A captura e as falas de um novo vídeo vêm do novo projeto.

## Revisão editorial e visual por vídeo

Mesmo com a regressão aprovada, revise:

1. Fala: frases completas, contexto, nomes, números, entrada de cada gancho e conclusão. Confira o áudio; uma transcrição plausível pode estar errada.
2. Evidência: o trecho destacado sustenta exatamente a fala? Preserva a ressalva e o caráter de alegação? A resposta aparece no ponto adequado? URL e recorte correspondem?
3. Enquadramento: inspecione início, meio, fim e movimento mais próximo de cada tomada, além das emendas. Meça o envelope de cabelo/barba e registre `face_bounds`; confirme com imagens. A translação não deve esconder conteúdo importante no rodapé.
4. Legibilidade: confira a composição em escala de celular, especialmente parágrafos destacados. Prefira focar/dividir o trecho a reduzir letras indiscriminadamente.
5. Entrega: decodificação integral, duração e alinhamento A/V, SRT da mesma lista de cues, teste de reprodução e links da galeria. Preserve a versão anterior.

Registre a revisão em um arquivo do projeto com amostras de tempo, caminhos dos quadros examinados, problemas encontrados e correções feitas. Não preencha uma lista de “OK” por ter executado um comando. A regressão prova reprodução dos casos testados, não a escolha correta de trechos em qualquer vídeo futuro.

## Limites explícitos

O motor não escolhe automaticamente a melhor tomada, não decide qual parágrafo prova uma alegação, não inventa transcrição e não faz detecção contínua de rosto. Essas etapas são realizadas pelo agente com os brutos, fontes e referência. Sua função é estabilizar a execução das decisões: layout, tipografia, escala, cortes especificados, sincronização e exportação. Nenhuma quantidade de arquivos elimina a necessidade dessa revisão.
