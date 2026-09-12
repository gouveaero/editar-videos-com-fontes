---
name: editar-videos-com-fontes
description: Editar vídeos de Gabriel falando para a câmera, com cortes naturais, ganchos alternativos, legendas e capturas reais de fontes com passagens destacadas. Usar para repetir esse padrão de edição ou preparar sua entrega; não ativa para geração de apresentador ou simples análise de um vídeo.
---

# Editar vídeos com fontes

Produza uma montagem simples, com o apresentador em destaque, a fala coerente e as fontes funcionando como evidência visual. Estes são os padrões pessoais de Gabriel; novas instruções e a referência fornecida para cada vídeo prevalecem.

## Base executável

Esta skill inclui um motor reutilizável, não apenas instruções. Use [video_pipeline.py](scripts/video_pipeline.py) com um arquivo de projeto para especificar fontes, cortes, componentes, ganchos, cues e recortes. Adapte esses dados a cada vídeo; não reescreva o renderizador a cada trabalho. A montagem aceita qualquer quantidade de variantes e reutiliza componentes compartilhados.

- [Contrato e comandos](references/projeto.md): ler ao iniciar uma edição. Define os dois modos de entrada (brutos com cortes ou masters já editados), importação de transcrição, composição, exportação e pacote.
- [style.json](assets/style.json) e [composition.css](assets/composition.css): fonte, tamanho, contorno, posição, limites de imagens e escala. Fonte e GSAP usados na entrega aprovada estão incluídos. O motor fixa HyperFrames 0.8.33.
- [Validação](references/validacao.md): ler ao alterar o motor ou estilo. Explica os testes de falhas e a regressão com dois componentes reais e seis quadros aprovados, incluídos em `assets/benchmark/`.

Sequência normal: decidir os cortes → gerar masters → transcrever o áudio editado → importar e revisar cues → selecionar e preparar evidências → validar o projeto → gerar composições e conferir a principal → renderizar variantes → verificar MP4 → registrar revisão editorial → empacotar. Etapas já concluídas podem ser reutilizadas quando seus arquivos e parâmetros permanecem idênticos. A transcrição e a seleção editorial não são fingidas pelo motor.

Mudanças no motor, CSS, fonte ou versão do renderizador devem passar por `check_invariants.py` e `regression.py` em uma pasta de QA separada. Não rode a regressão inteira a cada vídeo sem mudança técnica. Nunca substitua os benchmarks ou aumente tolerâncias para esconder uma divergência. Nos novos vídeos, faça a validação do projeto e a revisão de suas próprias cenas.

## Escopo e entradas

Separe o pedido de edição do pedido de entrega. Quando Gabriel disser que a edição atual está aprovada e quiser somente os arquivos, a legenda ou uma melhoria futura na skill, preserve os MP4 e seus cortes. Prepare os complementos sem renderizar novamente. “Legenda para publicar” é o texto do post; diferencie das legendas sincronizadas já gravadas no vídeo.

Localize os brutos, o roteiro, a referência visual, os links e a entrega anterior. Leia transcrições existentes antes de transcrever novamente. Inspecione quadros da referência e dos brutos para identificar posições e escala do rosto; não presuma que a versão gerada anteriormente seja a referência correta.

## Fala e montagem

Transcreva o áudio real com tempos por palavra e mantenha a transcrição original junto às correções. Use o roteiro para entender a intenção, nunca para inventar palavras que não foram gravadas. Revise nomes, números e termos técnicos pelo áudio e pelas fontes.

Registre cortes e variantes em um plano editável: arquivo de origem, entrada, saída, motivo, número de quadros e sequência. Preserve frases e argumentos completos, ganchos inteiros e contexto necessário. Remova preparação, tentativas duplicadas, respirações nas emendas e silêncios excessivos; mantenha pausas naturais. Não force duração nem acelere a fala para cumprir uma estimativa não rígida. Se um gancho já apresenta dados, adapte a entrada no corpo para evitar a repetição imediata.

Monte componentes compartilhados e ganchos separados. Use FFmpeg para cortes e áudio, preferindo HyperFrames para a composição quando disponível. Leia a documentação instalada antes de usar comandos novos. Para detalhes do padrão validado e do projeto anterior, consulte [o perfil de referência](references/perfil-gabriel.md). Novos parâmetros de enquadramento, cortes ou layout precisam participar da chave de cache; não reutilize renders antigos só porque os nomes coincidem.

## Evidência visual: contexto e destaque

Escolha primeiro a frase da fonte que sustenta a fala daquele instante. Registre a relação como declaração, alegação, resposta, dado ou contexto. Na passagem sobre possível uso de dados de pesquisadores, busque o trecho da declaração do pesquisador que questiona esse uso. Uma manchete genérica ou uma frase sobre não conhecer o funcionamento do modelo não substitui essa passagem. Preserve o caráter de hipótese ou alegação e apresente a resposta da outra parte na fala correspondente.

Capture a publicação real pelo navegador ou ferramenta de captura disponível. Preserve o arquivo original. Recorte um trecho contextualizado — normalmente um pequeno bloco de parágrafo com a passagem importante — e destaque as linhas pertinentes na própria captura. Prefira isso a títulos isolados quando a fala trata de um argumento específico. Respeite os limites de reprodução aplicáveis; não suponha que uma captura permita copiar uma publicação inteira. Use material fornecido pelo usuário quando adequado.

Preserve tipografia e aparência da publicação; não reescreva a manchete como cartão HTML. Mantenha identificação da fonte no recorte quando couber sem destruir a leitura, e sempre registre URL, página/seção e créditos no projeto. Não junte pedaços descontínuos para aparentarem uma citação contínua. Inclua qualificações que mudam o sentido do trecho destacado.

Para automatizar recorte e marca-texto sem redesenhar letras, use [prepare_evidence.py](scripts/prepare_evidence.py) com o [manifesto de evidência](references/evidencias.md). O script preserva o original e registra coordenadas e hashes; ele não escolhe a frase nem verifica sua relação com a fala. Faça essa revisão editorial antes de executá-lo. Se o texto ficar pequeno na composição, selecione um trecho mais focado ou divida em dois recortes sequenciais com contexto; não comprima uma página inteira no alto.

Alterne fontes e fotos pertinentes, mantendo alguns trechos somente com apresentador e legenda. Recortes proporcionais, centralizados no alto; sem moldura, fundos adicionais, título inventado ou animação decorativa. Um marca-texto discreto pode ser estático. O tamanho depende do conteúdo e do espaço acima do rosto, não de uma caixa uniforme.

## Legendas e enquadramento

Mantenha escala original do rosto, com redimensionamento proporcional para a resolução de saída. Use apenas os ajustes verticais necessários. Não aplique zoom alternado automaticamente nas emendas.

Sincronize legendas com as palavras do áudio final; agrupe por leitura e sentido, com até duas linhas e sem órfãs desnecessárias. Use o estilo do perfil como ponto de partida e confira as tomadas próximas. Legenda branca, contorno escuro, sombra discreta, sem caixa; preserve distância da barba. Gere SRT da mesma lista de cues usada no render.

## Verificação e entrega

Confira a principal ao lado da referência antes de renderizar todas as variantes. Revise especialmente emendas, números, nomes, palavras recuperadas, relação entre fala e fonte, tamanho do texto na escala de celular e espaço ao redor do rosto. Um script de QA técnico não substitui essas decisões visuais e editoriais.

Exporte MP4, SRT, plano e composições editáveis; preserve a edição anterior. Verifique decodificação completa dos arquivos, duração, quadros, ausência de falhas e alinhamento entre áudio e vídeo. [package_project.py](scripts/package_project.py) gera galeria e ZIP com MP4, SRT, legenda de publicação, créditos e composições editáveis com sua mídia. Ele exige verificação técnica e registro da revisão efetivamente feita; esse registro não é um pedido de aprovação ao usuário. Atualize a galeria apenas com arquivos completos. Não publique nas redes como consequência implícita da entrega.

Na legenda de publicação, mantenha a tese e uma pergunta relevante, evitando transformar alegações em fatos confirmados. Dê um texto pronto para copiar; não entregue seis textos quase iguais se o usuário pediu uma legenda.
