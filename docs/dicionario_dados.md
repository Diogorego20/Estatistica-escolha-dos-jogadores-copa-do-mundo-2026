# Dicionário de Dados

**Projeto:** Simulação de Monte Carlo para Escolha Estatística de Jogadores — Copa do Mundo 2026  
**Autor:** Diogo Rego - Estudante de Estatística UFPB

## Fonte dos dados

Os dados foram obtidos do conjunto público **Football Players Stats (2025-2026)**, publicado por **Hubert Sidorowicz** na plataforma [Kaggle](https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2025-2026). Segundo a documentação do conjunto, as estatísticas são derivadas do **FBref**, contemplam a temporada **2025-2026** das cinco principais ligas europeias e são disponibilizadas sob licença **MIT**.

## Base processada

O arquivo principal utilizado pelo dashboard é `data/processed/players_world_cup_monte_carlo_ready.csv`. Ele foi construído a partir do arquivo `players_data_light-2025_2026.csv`, mantendo variáveis de identificação, minutos, gols, assistências, finalizações, indicadores defensivos, indicadores de goleiro e métricas derivadas por 90 minutos.

| Variável | Descrição | Uso estatístico |
|---|---|---|
| `jogador` | Nome do jogador. | Identificação na tabela, ranking e gráficos. |
| `nacao_codigo` | Código/abreviação da nacionalidade. | Filtro principal para simular convocações por país. |
| `posicao_original` | Posição original conforme a fonte. | Transparência da classificação esportiva. |
| `posicao_principal` | Posição simplificada: GK, DF, MF, FW ou OUT. | Restrição de vagas na simulação Monte Carlo. |
| `clube` | Clube do jogador. | Contextualização e filtros de exploração. |
| `liga` | Liga em que o jogador atua. | Comparações entre competições. |
| `idade` | Idade do jogador. | Componente suavizado de fase atlética. |
| `jogos` | Partidas disputadas. | Indicador de utilização e consistência. |
| `minutos` | Minutos jogados. | Penalização de baixa amostra e incerteza. |
| `noventas` | Minutos convertidos em jogos completos de 90 minutos. | Normalização das estatísticas por 90 minutos. |
| `gols_p90` | Gols por 90 minutos. | Componente ofensivo. |
| `assistencias_p90` | Assistências por 90 minutos. | Componente ofensivo e criativo. |
| `participacoes_gol_p90` | Gols + assistências por 90 minutos. | Indicador sintético de contribuição direta em gols. |
| `finalizacoes_p90` | Finalizações por 90 minutos. | Volume ofensivo. |
| `finalizacoes_gol_p90` | Finalizações no alvo por 90 minutos. | Qualidade/ameaça ofensiva. |
| `cruzamentos_p90` | Cruzamentos por 90 minutos. | Criação lateral e profundidade. |
| `desarmes_vencidos_p90` | Desarmes vencidos por 90 minutos. | Componente defensivo. |
| `interceptacoes_p90` | Interceptações por 90 minutos. | Leitura defensiva e recuperação. |
| `save_pct` | Percentual de defesas convertido para escala decimal. | Componente de goleiros. |
| `clean_sheet_pct` | Percentual de jogos sem sofrer gols. | Componente de goleiros. |
| `score_ataque` | Subíndice de desempenho ofensivo. | Ranqueamento de atacantes e jogadores ofensivos. |
| `score_meio` | Subíndice de desempenho de meio-campo. | Ranqueamento de meias. |
| `score_defesa` | Subíndice de desempenho defensivo. | Ranqueamento de defensores. |
| `score_goleiro` | Subíndice de desempenho de goleiro. | Ranqueamento de goleiros. |
| `indice_desempenho` | Índice final em escala 0–100. | Média/centro da distribuição na simulação Monte Carlo. |
| `incerteza_modelo` | Desvio-padrão individual usado na simulação. | Representa maior incerteza para jogadores com poucos minutos. |
| `penalidade_baixa_amostra` | Fator de ajuste para baixa exposição em campo. | Reduz risco de superestimar jogadores com amostra pequena. |

## Observação metodológica

O índice não representa uma verdade absoluta sobre convocação real. Ele é uma **ferramenta estatística autoral**, construída para comparar jogadores de maneira reprodutível a partir das estatísticas disponíveis. O dashboard permite ajustar pesos e número de simulações, incentivando análise crítica sobre sensibilidade, incerteza e composição de elenco.
