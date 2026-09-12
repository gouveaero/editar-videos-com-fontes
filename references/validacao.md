# O que sustenta a consistência

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
