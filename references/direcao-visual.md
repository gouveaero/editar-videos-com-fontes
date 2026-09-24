# Direção visual para vídeo vertical

## O que o feedback mudou

A edição de polímatas (17/09/2026) demonstrou quatro falhas do perfil anterior: limite fixo de imagem deixava obras pequenas; não havia enquadramento independente dos ganchos; UI legível no monitor ficava pequena no celular; zoom novo podia colocar títulos sobre o rosto. O novo motor torna essas decisões explícitas por componente/cena. Não exige consultar a pasta desse projeto nem carregar outra skill.

## Compor para leitura, não para preencher a tela

Uma cena tem uma ideia dominante: uma obra, uma passagem da fonte, um dado ou uma ação. Fotos grandes usam `contain`, com proporção original, título curto e crédito. Não use a mesma foto inteira e recortada simultaneamente. Uma galeria pode mostrar peças em sequência. Fotos e evidências têm regras diferentes: evidência deve continuar parecendo a publicação original, sem reescrever seu texto.

A paleta de partida usa papel claro, tinta escura e dourado pontual. Ela é configurável. Newsreader diferencia títulos; Source Sans 3 organiza interfaces; a fonte de legenda continua a do perfil aprovado. Todas acompanham a skill com os arquivos de licença. Evite downloads de fontes no meio da renderização.

No canvas 1080×1920, títulos de 60–110 px, texto de apoio 32–40 px e créditos de 24–28 px são pontos de partida. O teste decisivo é a composição a 270×480 ou 360×640. Se o parágrafo virar uma textura, selecione menos conteúdo ou dê mais espaço; não reduza indefinidamente a fonte. Nas capturas, meça a altura de letra que resulta da escala.

## Quatro disposições

1. **Câmera com destaque:** um título, palavra ou diagrama na área realmente livre. Meça rosto já transformado, não apenas no bruto. Retângulos editáveis permitem levar o texto para baixo se o cabelo ocupar a parte superior.
2. **Imagem única grande:** tela inteira com uma obra/foto proporcional; legendas e crédito continuam legíveis. Alterne com o apresentador. Não corte o conteúdo principal apenas para preencher 9:16.
3. **Evidência real:** recorte focado com destaque na própria passagem, identificação verificável e tamanho suficiente. Tela inteira é melhor que uma captura ilegível no alto.
4. **Demonstração:** área de trabalho grande em cima; explicação curta e janela do apresentador abaixo. A janela usa um recorte explícito e validado. A demo nunca toma o espaço reservado às legendas.

Os templates são ferramentas, não uma sequência obrigatória. Preserve trechos de câmera limpa, principalmente ressalvas, pergunta final e convite. Evite trocar de tela no primeiro instante do corpo: deixe o apresentador iniciar o assunto, sem confundir isso com manter respiração antes da fala.

## UI que conta uma ação

Mostre um estado inicial reconhecível, a ação e sua consequência. Um botão deve mudar de estado ou abrir algo; uma cronologia deve selecionar o documento do acontecimento; o pêndulo deve mudar geometria e período coerentemente. Dados fictícios ficam identificados.

- `prototype`: estados com IDs, navegação e tempos locais; sem links que apontem para telas inexistentes.
- `pendulum`: T = 2π√(L/g), pequenos ângulos; alterar L muda comprimento desenhado e período, com fase contínua no instante de troca. A reprodução acelerada pode avançar o relógio da demonstração, mas não mudar o valor físico exibido.
- `chronology`: cada acontecimento possui título, corpo e um arquivo local de documento. Inclua a fixture no pacote; não use `href="#"` para fingir uma ligação funcional.

Teste as ações interativas e a reprodução temporal. Um snapshot prova um estado, não a navegação. Controles usam os mesmos modelos puros do playback em `assets/editorial/demo_runtime.js`.

Movimentos curtos de 100–180 ms para respostas e 200–650 ms para entradas/conexões são suficientes na maioria das cenas. Use ações GSAP determinísticas que funcionem ao buscar qualquer instante; não dependa de `setTimeout`, tempo real, autoplay ou estado acumulado de visitas anteriores. Sem animação gratuita de todos os elementos.

## Reenquadrar sem colidir

`framing.scale` e `framing.origin` são dados da tomada. 1,68× com origem 50%/80% funcionou em dois ganchos deste caso; **não é o padrão universal**. Meça cabelo e barba em amostras do movimento. O motor transforma `face_bounds` ou aceita `framing.measured_face_bounds` medido depois do ajuste. Ele não detecta rostos.

Não confunda “mesmo zoom numérico” com “mesma proximidade percebida” em câmeras/distâncias diferentes. Ao aproximar, confira texto e overlays de novo: no caso real, um título que cabia acima passou a cobrir o cabelo e precisou descer. Os testes de geometria ajudam, mas dependem das medições corretas.
