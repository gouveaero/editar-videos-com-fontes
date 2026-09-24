---
name: editar-videos-com-fontes
description: Editar vídeos de Gabriel falando para a câmera, com cortes naturais, ganchos alternativos, legendas, fontes reais, imagens grandes, demonstrações animadas e efeitos sonoros. Usar para produzir, revisar ou entregar esse padrão de vídeo; não para gerar apresentador ou apenas analisar um vídeo.
---

# Editar vídeos com fontes

Entregue fala íntegra, ritmo natural e elementos visuais legíveis no celular. Esta skill inclui a direção visual e os recursos executáveis necessários; não depende de outra skill de design. A referência e as instruções do vídeo atual prevalecem sobre padrões anteriores.

## Escolha o caminho mínimo

- **Edição com acabamento visual:** use [editorial_pipeline.py](scripts/editorial_pipeline.py), que estende o motor estável com enquadramento por tomada, imagens únicas, títulos, conexões, gráficos, demonstrações e sons. Leia [contrato básico](references/projeto.md) e [contrato editorial](references/editorial.md).
- **Montagem simples ou reprodução antiga:** [video_pipeline.py](scripts/video_pipeline.py) mantém o perfil original sem zoom. Os projetos anteriores continuam compatíveis.
- **Só entrega ou melhoria da skill:** preserve os vídeos aprovados. Não renderize de novo por carregar esta skill.
- **Revisão pontual:** altere a menor unidade necessária. Um defeito no corpo compartilhado deve ser corrigido em todas as variantes que o usam; um defeito exclusivo de um gancho não deve modificar os outros.

Antes de editar, localize brutos, roteiro, transcrições, fontes, referência e última versão aprovada. Use uma nova pasta de revisão; mantenha as anteriores. Não imponha sete ganchos, duração fixa, uma profissão, a paleta ou exemplos de um projeto antigo.

## Fala, respiração e relógio único

Transcreva o **áudio realmente editado**, com tempos por palavra, e preserve o JSON original. Não invente falas ou sintetize uma abertura ausente. Registre origem, entrada, saída, número de quadros e motivo dos cortes.

Na junção gancho → corpo, confira o final da última palavra, a inspiração e o início real da primeira consoante. **Uma pausa curta ainda pode conter uma respiração audível.** O tempo de palavra do ASR e um limiar de silêncio são pistas, não o ponto de corte definitivo. Use [inspect_audio.py](scripts/inspect_audio.py) para gerar trecho de escuta, forma de onda e espectrograma. Confirme a frase depois do corte; não alegue audição integral quando só houve análise técnica. Veja [cortes e som](references/audio-e-tempo.md).

Corte logo antes da fala com pequena margem que preserve a consoante inicial; não copie os 16 quadros usados em outra gravação. Um fade curto evita clique, mas não substitui retirar a inspiração. Preserve pausas expressivas e as ressalvas do argumento.

Mantenha **um relógio por componente final** para fala, legendas, imagens, estados das demonstrações, música e SFX. Para cortar o início ou mudar a velocidade, use [retime_project.py](scripts/retime_project.py): ele cria outra revisão e aplica o mesmo mapa a todas essas posições. Tempos relativos dos estados também mudam. Não misture tempos de bruto, 1× e saída final. Velocidade padrão 1×; 1,1× somente quando solicitado, com pitch preservado. Nunca acelere duas vezes um master já acelerado.

## Direção visual incorporada

Leia [direção visual](references/direcao-visual.md) quando compuser ou revisar elementos. Use o rosto como presença principal e o material de apoio para tornar uma ideia concreta.

- Meça o enquadramento de **cada tomada**, inclusive início, meio, fim e movimento mais próximo. Aproximar o rosto e remover teto indesejado é permitido. Configure escala/origem; confira cabelo, barba e fundo depois do zoom. Igualar a sensação de proximidade pode exigir escalas diferentes em brutos diferentes.
- Mostre primeiro o apresentador iniciando a ideia; introduza a imagem na palavra pertinente. Evite um flash do rosto seguido imediatamente por uma tela cheia após o gancho.
- Para obras e fotos de destaque, prefira **uma imagem grande por vez**, proporcional. Não duplique miniatura e detalhe nem encaixe duas imagens ilegíveis para preencher espaço. Capturas de publicações podem usar um recorte focado sobre a câmera ou tela inteira conforme a legibilidade.
- Títulos de ênfase ficam no espaço livre acima do rosto quando ele existe. Se o zoom ocupou esse espaço, reposicione; nunca deixe o texto atravessar cabelo, olhos ou barba. Confira novamente as legendas depois de reenquadrar.
- Hierarquia clara, tipografia local, poucos níveis de texto, espaço generoso e contraste. Uma mudança de estado deve explicar uma ação. Evite cartões decorativos repetidos, rótulos minúsculos e movimento sem função.

Os recursos em `assets/editorial/` incluem CSS, Newsreader, Source Sans 3, licenças e modelos funcionais de navegação, pêndulo e cronologia com documentos. São pontos de partida configuráveis, não conteúdo para inserir automaticamente. Teste ações e dados; identifique dados fictícios como **Exemplo ilustrativo**. Animação HTML criada localmente não deve ser chamada de captura real de um site. Não prometa funcionamento de um botão só porque ele foi desenhado.

## Fontes reais e legendas

Escolha a passagem que sustenta exatamente a fala e registre alegação/relação, URL e crédito. Preserve qualificações, hipótese e resposta pertinente. Capture a publicação real; não redesenhe uma manchete ou parágrafo como se fosse original. [prepare_evidence.py](scripts/prepare_evidence.py) e [manifesto de evidências](references/evidencias.md) preservam fonte, recorte e marcação. Se o navegador estiver indisponível, use um documento oficial real quando adequado e identifique-o corretamente.

Legenda branca, contorno escuro, até duas linhas, sem caixa, distante da barba. Destaque pontual, não a frase inteira. Use a lista de cues tanto no MP4 quanto no SRT. Saída de referência: 1080×1920/30; margens de texto de 250 px no topo e base. Veja [perfil de Gabriel](references/perfil-gabriel.md) para distinguir preferências de valores específicos de um vídeo.

## Som e verificação

Use efeitos correspondentes às ações: clique na seleção, chave no controle, transição discreta na troca, confirmação no resultado. Não sonorize cada palavra. Escolha sons locais autorizados, registre origem/licença conhecida, recorte o ataque e mantenha-os abaixo da voz. O motor gera faixas separadas e permite reduzir a música em intervalos relevantes; veja [cortes e som](references/audio-e-tempo.md). Música e SFX são opcionais; não adicione ruído para preencher silêncio.

Faça uma primeira revisão visual em lote, corrija os problemas encontrados e confirme os quadros afetados. Antes do lote final, confira uma versão principal, **todas as emendas diferentes** e os estados das demonstrações. Um corpo igual permite reaproveitar a revisão do corpo, não presumir que todos os ganchos estão bons.

Mudança no motor/estilo exige [testes e limites](references/validacao.md): invariantes, regressão antiga e checks editoriais quando afetados. Verifique decodificação completa, quadros, A/V, áudio, SRT e equivalência do corpo. Cache inclui código, fontes, mídia, enquadramento e eventos; não reaproveite um render só pelo nome.

[package_project.py](scripts/package_project.py) cria galeria e ZIP com MP4, SRT, legenda de publicação, fontes e composições. Projetos editoriais incluem motor, fontes locais, demonstrações, documentos e sons para reconstrução independente. Inspecione o pacote extraído; preserve também o plano e a revisão efetivamente feita. O registro editorial é documentação do trabalho, não um pedido de aprovação. Não publique em redes como consequência da entrega.
