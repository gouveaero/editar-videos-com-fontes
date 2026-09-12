# Manifesto de recorte e destaque

Use um JSON por recorte. Os caminhos são relativos ao próprio JSON; as coordenadas são pixels da captura completa original, em formato `[esquerda, topo, direita, base]`, com direita e base exclusivas. Se o parágrafo quebra a frase em três linhas, use três retângulos. Selecione as coordenadas olhando a captura em sua resolução original; não estime por uma miniatura.

Exemplo de estrutura, com coordenadas ilustrativas a substituir pelas medidas reais:

```json
{
  "screenshot": "originais/declaracao.png",
  "output": "recortes/declaracao-dados.png",
  "source_url": "https://instituicao.example/declaracao",
  "source_name": "Autor — declaração pública",
  "claim": "O pesquisador questionou se seus dados poderiam ter influenciado os modelos.",
  "excerpt": "Transcrição exata do trecho selecionado, incluindo a ressalva relevante.",
  "relation": "alegação do autor, não conclusão comprovada",
  "crop": [100, 400, 1100, 800],
  "highlights": [[130, 520, 1030, 550], [130, 555, 800, 585]]
}
```

Execute `python3 scripts/prepare_evidence.py caminho/evidencia.json` a partir da pasta da skill, com Pillow disponível. O script não acessa sites: recebe uma captura que já foi obtida e conferida. Não salva sobre arquivos existentes. Produz PNG sem redimensionamento e um `.provenance.json`, para que o compositor faça a escala proporcional uma única vez.

O destaque é amarelo discreto, multiplicado sobre os pixels da linha. Não substitui nem redesenha o texto. Inspecione o resultado: fontes escuras ou páginas com padrões de fundo podem pedir outro tratamento ou somente recorte sem destaque (`highlights: []`). O registro editorial é uma anotação humana/agente; o script não prova que a fonte sustenta a afirmação.

No plano de vídeo, associe cada recorte a `start`, `end`, `asset`, `source_url`, `claim` e `relation`. A duração precisa permitir a leitura da passagem destacada; nem todo espectador precisa ler o parágrafo inteiro. Evite imagens de apoio contínuas quando o fechamento funciona melhor só com a fala.
