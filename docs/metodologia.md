# Metodologia Estatística

**Projeto:** Simulação de Monte Carlo para Escolha Estatística de Jogadores — Copa do Mundo 2026  
**Autor:** Diogo Rego - Estudante de Estatística UFPB

## Fundamentação

Este projeto propõe uma metodologia estatística autoral para comparar jogadores de futebol a partir de estatísticas observadas e estimar probabilidades relativas de seleção em um elenco hipotético. A abordagem combina engenharia de variáveis, normalização por posição, penalização por baixa amostra e simulação de Monte Carlo.

A fonte de dados é o conjunto público **Football Players Stats (2025-2026)**, publicado no Kaggle por Hubert Sidorowicz, com estatísticas derivadas do FBref.[^1] A aplicação utiliza essas estatísticas como insumo quantitativo, sem afirmar que o modelo reproduz critérios reais de treinadores, federações ou comissões técnicas.

> A simulação de Monte Carlo é usada aqui como instrumento de análise de incerteza. Em vez de tratar o índice de desempenho como valor fixo e definitivo, o modelo permite que cada jogador varie ao redor de sua média estimada, respeitando uma incerteza maior para atletas com menos minutos observados.

## Etapa 1 — Preparação dos dados

A preparação dos dados começa com a padronização de variáveis essenciais, incluindo nome do jogador, nacionalidade, clube, liga, idade, minutos, partidas e posição. As posições originais são simplificadas em cinco grupos operacionais: `GK`, `DF`, `MF`, `FW` e `OUT`. A simulação utiliza os quatro primeiros grupos por representarem as funções principais de uma composição de elenco.

| Grupo | Significado | Uso na simulação |
|---|---|---|
| `GK` | Goleiro | Seleção por vagas de goleiros. |
| `DF` | Defensor | Seleção por vagas defensivas. |
| `MF` | Meio-campista | Seleção por vagas de meio-campo. |
| `FW` | Atacante | Seleção por vagas ofensivas. |
| `OUT` | Outros ou posição não classificada | Mantido na base, mas excluído do elenco simulado. |

As estatísticas de contagem são convertidas para métricas por 90 minutos quando necessário. Essa decisão reduz o viés de comparação entre atletas com diferentes tempos de jogo, embora o próprio modelo também penalize jogadores com poucos minutos para evitar superestimação por amostra reduzida.

## Etapa 2 — Normalização por posição

Cada métrica relevante é normalizada dentro do grupo posicional do jogador. Essa escolha é importante porque as distribuições de estatísticas variam fortemente entre goleiros, defensores, meio-campistas e atacantes. Comparar diretamente gols de um zagueiro com gols de um atacante, por exemplo, produziria uma leitura distorcida do desempenho relativo.

A normalização utilizada é uma escala min-max por posição:

```text
x_norm = (x - mínimo_posição) / (máximo_posição - mínimo_posição)
```

Quando todos os atletas de uma posição possuem o mesmo valor em determinada métrica, a variável normalizada recebe valor zero para evitar divisão por zero. O resultado é uma escala interpretável entre 0 e 1.

## Etapa 3 — Construção dos subíndices

O modelo calcula quatro subíndices principais: ataque, meio-campo, defesa e goleiro. Cada subíndice é uma combinação ponderada de variáveis coerentes com a função esportiva analisada. Os pesos foram definidos de forma autoral e documentada para favorecer interpretabilidade.

| Subíndice | Variáveis principais | Interpretação |
|---|---|---|
| `score_ataque` | Participação em gols, gols, assistências, finalizações no alvo, eficiência e cruzamentos. | Mede impacto ofensivo direto e geração de ameaça. |
| `score_meio` | Assistências, cruzamentos, faltas sofridas, participação em gols, desarmes e interceptações. | Mede criação, conexão entre setores e equilíbrio. |
| `score_defesa` | Desarmes vencidos, interceptações, cruzamentos, volume, experiência, idade atlética e disciplina. | Mede contribuição defensiva e consistência operacional. |
| `score_goleiro` | Percentual de defesas, jogos sem sofrer gols, gols sofridos por 90 minutos, volume e experiência. | Mede desempenho específico para goleiros. |

## Etapa 4 — Índice de desempenho

O índice de desempenho base é escolhido conforme a posição principal do jogador. Goleiros são avaliados prioritariamente pelo subíndice de goleiro, defensores pelo subíndice defensivo, meio-campistas pelo subíndice de meio-campo e atacantes pelo subíndice ofensivo. O valor final é convertido para escala 0–100 após aplicação de penalização por baixa amostra.

A penalização por baixa amostra considera 900 minutos como referência mínima de estabilidade. Jogadores com menos minutos recebem um fator proporcional à raiz da razão entre minutos observados e 900 minutos:

```text
penalidade = sqrt(minutos / 900), quando minutos < 900
penalidade = 1, quando minutos >= 900
```

Essa função preserva jogadores promissores com baixa amostra, mas reduz a chance de que poucos minutos extremamente eficientes dominem o ranking.

## Etapa 5 — Incerteza individual

A incerteza do modelo é calculada como função decrescente dos jogos completos de 90 minutos e do volume total de jogo. Jogadores com mais minutos tendem a possuir menor variabilidade simulada, enquanto jogadores com menor exposição recebem maior desvio-padrão. O objetivo é representar incerteza estatística, não instabilidade psicológica ou tática.

| Situação | Efeito esperado |
|---|---|
| Muitos minutos jogados | Menor incerteza e escore simulado mais estável. |
| Poucos minutos jogados | Maior incerteza e maior variação nas simulações. |
| Índice alto com baixa amostra | Pode oscilar bastante e perder posições em cenários conservadores. |
| Índice alto com grande amostra | Tende a manter alta probabilidade de seleção. |

## Etapa 6 — Simulação de Monte Carlo

Em cada rodada Monte Carlo, o modelo sorteia um escore de desempenho para cada jogador com distribuição normal centrada no índice ajustado e desvio-padrão igual à incerteza individual multiplicada pelo fator de incerteza escolhido pelo usuário. Depois disso, os melhores jogadores de cada posição são selecionados até preencher as vagas definidas no painel.

```text
escore_simulado_i ~ Normal(indice_ajustado_i, incerteza_i × fator_incerteza)
```

Ao final de `N` simulações, a probabilidade de seleção de cada jogador é calculada como:

```text
probabilidade_i = número_de_seleções_i / N
```

## Interpretação estatística

A probabilidade estimada deve ser interpretada como uma probabilidade condicional ao cenário configurado. Ela depende da nacionalidade selecionada, do número de vagas por posição, dos minutos mínimos, dos pesos do índice, da semente e do fator de incerteza. Assim, o dashboard deve ser lido como ferramenta de análise de sensibilidade.

| Probabilidade | Classificação | Interpretação |
|---|---|---|
| 80% a 100% | Favorito estatístico | Jogador selecionado na grande maioria dos cenários simulados. |
| 55% a 79,99% | Forte candidato | Jogador competitivo, mas ainda sensível a incerteza e pesos. |
| 30% a 54,99% | Competitivo | Jogador relevante em parte dos cenários. |
| 10% a 29,99% | Aposta situacional | Jogador dependente de configuração específica. |
| 0% a 9,99% | Baixa probabilidade | Jogador raramente selecionado no cenário atual. |

## Limitações e uso responsável

O modelo não inclui lesões, preferências táticas, histórico em seleção nacional, qualidade contextual dos adversários, dados avançados proprietários ou avaliação subjetiva de comissão técnica. Portanto, ele deve ser utilizado como uma ferramenta acadêmica e exploratória de estatística aplicada ao futebol.

O valor do projeto está na transparência e na reprodutibilidade: todas as regras, pesos, dados e limitações são documentados, permitindo ajustes, críticas e melhorias metodológicas.

## Referências

[^1]: Hubert Sidorowicz. **Football Players Stats (2025-2026)**. Kaggle. Disponível em: <https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2025-2026>.
[^2]: FBref. **Football Statistics and History**. Disponível em: <https://fbref.com/>.
[^3]: Posit. **Shiny for R**. Disponível em: <https://shiny.posit.co/r/>.
