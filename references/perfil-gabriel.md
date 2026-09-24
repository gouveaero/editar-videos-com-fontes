# Perfil visual e projetos de referência

## Preferências incorporadas em 17/09/2026

Use o modo editorial para o acabamento mais recente: uma imagem grande por vez, títulos legíveis no espaço livre, interfaces com hierarquia e ação real, sons discretos ligados aos eventos e enquadramento individual dos ganchos. Corte a inspiração real antes do corpo compartilhado em todas as variantes, depois de inspecionar o áudio.

Valores do caso de polímatas — 1,68× de zoom, 0,533 s de corte, sete ganchos e velocidade 1,1× — foram decisões daquele pedido. Não são valores automáticos para outra gravação. Velocidade 1× por padrão; o usuário decide acelerar.

A skill contém os modelos, fontes, lógica e testes necessários em `assets/editorial` e `scripts/editorial_*`; não depende dos arquivos do projeto antigo ou de outra skill de design. Leia [direção visual](direcao-visual.md) e [cortes e som](audio-e-tempo.md).

## Perfil original preservado (10/09/2026)

As restrições de zoom e tamanhos abaixo descrevem a reprodução desse vídeo antigo, não proíbem o novo modo editorial.

Ponto de partida do vídeo de IA aprovado em 10/09/2026, sem transformar suas durações ou seis ganchos em exigências universais:

- Saída vertical 1080×1920, 30 fps.
- Legenda Arial Bold 70 px, branca, contorno escuro 7 px, sombra `0 4px 8px #000, 0 0 5px #000`; largura 900 px, esquerda 90 px, topo 1485 px, altura mínima 155 px, entrelinha 1,1, alinhamento central e no máximo duas linhas. Sem caixa ou borda retangular. Ajustar se outra gravação ou referência pedir.
- Imagem de evidência com largura máxima 960 px e altura máxima 480 px; nas tomadas próximas, 340 px de altura. Sem distorção e sem forçar o mesmo tamanho para conteúdos diferentes. O limite inferior usado como ponto de partida foi y=555 ou y=415 nas próximas; verificar o cabelo em cada tomada.
- Sem o zoom adicional de 2,5% da primeira tentativa. A revisão só deslocou o apresentador verticalmente. Não copiar valores de deslocamento entre pessoas e gravações diferentes.
- Legendas sincronizadas a partir de Whisper no áudio gravado, com correções documentadas. Brutos e transcrições originais preservados.

Melhoria solicitada para FUTURAS edições: usar blocos maiores e legíveis das publicações, com a passagem que sustenta a fala marcada sobre a captura. Na discussão sobre possível uso de dados, preferir o trecho específico da declaração do pesquisador. Essa melhoria ainda não foi aplicada aos seis MP4 aprovados; não os alterar só por carregar esta skill.

Os componentes, recortes e quadros necessários ao teste de regressão estão incluídos em `assets/benchmark/`. O motor recebe os caminhos dos novos brutos pelo JSON de projeto; não depende da pasta da primeira edição. Para editar a entrega original completa, use o projeto local preservado separadamente.
