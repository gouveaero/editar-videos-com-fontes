# Corte, velocidade e desenho de som

## Inspiração não é silêncio

O erro mais persistente deste projeto foi mexer no fim do gancho quando o ruído estava no início do corpo. Inspecione ambos os lados da junção antes de cortar. Um limiar de silêncio pode ignorar uma inspiração audível; o ASR pode atribuir o início da palavra ao intervalo de respiração. O corte deve seguir o áudio real.

```sh
python3 scripts/inspect_audio.py /caminho/master.mp4 --output /nova/pasta/entrada --start 0 --duration 3
```

O resultado inclui `listen.wav`, `waveform.png`, `spectrum.png` e procedência. Ouça o trecho, observe o início da voz e preserve a primeira consoante. Um ponto 20–50 ms antes da fala pode funcionar, mas respiração, consoantes surdas e ruído variam. Espectrograma, VAD e ASR são evidências auxiliares, não detecção infalível. Compare a junção completa depois da alteração; uma transcrição independente da primeira frase ajuda a detectar palavra mutilada, mas não prova sozinha que a edição soa natural.

No caso de polímatas, remover 0,533 s do início compartilhado resolveu o ruído; a frase inteira foi recuperada no teste. Esse número é um registro de caso, não uma receita. Fade curto de 6–20 ms ajuda a evitar clique. Não use fade para apenas abaixar uma inspiração que deveria sair da montagem.

## Uma transformação de tempo

Todos os tempos do projeto editorial são **segundos da versão final do componente**. Os estados internos são segundos relativos ao início de sua cena. Cortes originais continuam no plano de fontes, com relógio identificado.

```sh
python3 scripts/retime_project.py /projeto/project.json --component corpo \
  --head-frames 16 --output /nova/revisao --reason "Inspiração medida antes da fala"
```

Esse comando é um exemplo, não um corte automático. Ele valida o plano antes de gravar, cria outra pasta, recorta áudio/vídeo pelo mesmo número de quadros e aplica `(tempo_antigo - início) / velocidade` a cues, palavras, cenas, estados, efeitos e redução de música. A duração final é arredondada para 30 fps e o áudio recebe a mesma quantidade exata de amostras. Todos os ganchos que referenciam o corpo passam a usar o novo corpo.

Se o corte atravessar uma palavra segundo o ASR, o helper recusa. Após conferir que o ASR colocou o tempo errado, o agente pode passar `--boundary-note "Evidência e revisão do ponto de fala"`; isso registra a decisão técnica, não exige pedir nova permissão ao usuário. Palavras inteiramente removidas continuam sendo erro; corrija a transcrição a partir do áudio antes de continuar. Cortes atravessando uma animação exigem editar essa cena explicitamente para não destruir sua fase inicial.

Para velocidade solicitada:

```sh
python3 scripts/retime_project.py /projeto/project.json --speed 1.1 \
  --output /nova/revisao --reason "Velocidade 1,1× solicitada"
```

Sem `--component`, a velocidade vale para todos os componentes. O helper usa `atempo`, sem alterar pitch. Só use sobre masters no estado conhecido: o JSON `retime.json` registra fonte/hash, corte, razão e fator. Nunca aplicar 1,1× novamente a uma saída que já o recebeu. Música de fundo é uma cama independente, não precisa imitar a velocidade da voz; o arquivo e ganho originais são preservados, e as reduções seguem o novo relógio.

## Efeitos correspondentes à ação

Procure primeiro no banco local indicado por Gabriel. O caminho conhecido deste caso é `/Users/gabriel/Documents/EFEITOS SONOROS`; não exija sua existência em outro computador. Se houver `manifest.json`, use os metadados. Registre `source` e `license`; quando a licença não estiver especificada, escreva isso, sem inventar “CC0” ou “royalty free”. Não redistribua todo o banco: empacote os sons usados/declarados.

Seleção por significado: clique para selecionar, chave para mudar um controle, confirmação discreta para um resultado, transição curta para entrada/troca de tela. Fotografia pode receber um obturador suave se combinar com o conteúdo. Não aplique efeitos a toda palavra ou toda emenda. Em ressalvas e na pergunta final, menos som pode ser melhor.

`sound_design.py`, chamado pelo motor editorial, mede o pico do fragmento escolhido, remove apenas o trecho definido por `trim_in`, aplica ganho e microfades e gera uma faixa PCM separada por componente. Escolha um ataque sem silêncio antes dele. `peak_dbfs=-27` é um ponto de partida; os sons deste caso ficaram entre −25 e −29 dBFS. Ajuste pela voz real. A mixagem final conserva a voz e limita picos; limiter não compensa um efeito irritante ou alto demais.

`music_duck` em cada componente permite reduzir a cama em trechos importantes. Os intervalos só alteram a música. Ouça as transições; use recorte/faixa com envelope suave para fades longos em projetos que precisem deles. O preset por intervalo é uma redução simples, não um compressor de sidechain.

## Revisão de emendas em todas as variantes

Crie amostras de aproximadamente 1 s antes e 2 s depois de cada junção diferente. Confira palavra final, inspiração, palavra inicial e sincronismo. O corpo pode ter sua revisão compartilhada, mas as junções com ganchos diferentes precisam ser vistas/ouvidas. Uma correção no início do corpo deve propagar-se a todas as variantes; não entregar apenas a primeira corrigida.
