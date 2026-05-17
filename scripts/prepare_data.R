# -----------------------------------------------------------------------------
# Projeto: Simulação de Monte Carlo para Escolha Estatística de Jogadores
# Autor: Diogo Rego - Estudante de Estatística UFPB
# Fonte: Kaggle / FBref - Football Players Stats (2025-2026)
# Objetivo: preparar a base de jogadores para o dashboard Shiny.
# -----------------------------------------------------------------------------

pacotes <- c("dplyr", "readr", "stringr", "jsonlite")
pacotes_ausentes <- pacotes[!vapply(pacotes, requireNamespace, logical(1), quietly = TRUE)]

if (length(pacotes_ausentes) > 0) {
  stop(
    sprintf(
      "Instale os pacotes antes de executar este script: install.packages(c(%s))",
      paste(sprintf('"%s"', pacotes_ausentes), collapse = ", ")
    ),
    call. = FALSE
  )
}

library(dplyr)
library(readr)
library(stringr)
library(jsonlite)

arquivo_entrada <- "data/raw/players_data_light-2025_2026.csv"
diretorio_saida <- "data/processed"
dir.create(diretorio_saida, recursive = TRUE, showWarnings = FALSE)

normalizar_nacao <- function(x) {
  ifelse(is.na(x), "Não informado", stringr::word(as.character(x), -1))
}

posicao_principal <- function(posicao) {
  posicao <- toupper(as.character(posicao))
  dplyr::case_when(
    stringr::str_detect(posicao, "GK") ~ "GK",
    stringr::str_detect(posicao, "DF") ~ "DF",
    stringr::str_detect(posicao, "MF") ~ "MF",
    stringr::str_detect(posicao, "FW") ~ "FW",
    TRUE ~ "OUT"
  )
}

por_90 <- function(valor, noventas) {
  ifelse(is.na(noventas) | noventas <= 0, 0, dplyr::coalesce(valor, 0) / noventas)
}

normalizar_por_posicao <- function(dados, variavel) {
  dados |>
    group_by(posicao_principal) |>
    mutate(
      minimo = min(.data[[variavel]], na.rm = TRUE),
      maximo = max(.data[[variavel]], na.rm = TRUE),
      normalizado = ifelse(maximo == minimo, 0, (.data[[variavel]] - minimo) / (maximo - minimo))
    ) |>
    ungroup() |>
    pull(normalizado) |>
    tidyr::replace_na(0)
}

preparar_base <- function(arquivo) {
  dados <- readr::read_csv(arquivo, show_col_types = FALSE)

  dados <- dados |>
    mutate(
      jogador = stringr::str_squish(Player),
      nacao_codigo = normalizar_nacao(Nation),
      posicao_original = coalesce(Pos, "Não informado"),
      posicao_principal = posicao_principal(Pos),
      clube = coalesce(Squad, "Não informado"),
      liga = coalesce(Comp, "Não informado"),
      idade = as.numeric(Age),
      jogos = as.numeric(MP),
      minutos = as.numeric(Min),
      noventas = pmax(as.numeric(`90s`), 0),
      gols_p90 = por_90(as.numeric(Gls), noventas),
      assistencias_p90 = por_90(as.numeric(Ast), noventas),
      participacoes_gol_p90 = por_90(as.numeric(`G+A`), noventas),
      finalizacoes_p90 = por_90(as.numeric(Sh), noventas),
      finalizacoes_gol_p90 = por_90(as.numeric(SoT), noventas),
      cruzamentos_p90 = por_90(as.numeric(Crs), noventas),
      desarmes_vencidos_p90 = por_90(as.numeric(TklW), noventas),
      interceptacoes_p90 = por_90(as.numeric(Int), noventas),
      faltas_sofridas_p90 = por_90(as.numeric(Fld), noventas),
      disciplina_p90 = por_90(as.numeric(CrdY) + 2 * as.numeric(CrdR), noventas),
      eficiencia_chute = pmin(pmax(coalesce(as.numeric(`G/Sh`), 0), 0), 1),
      taxa_chutes_gol = pmin(pmax(coalesce(as.numeric(`SoT%`), 0) / 100, 0), 1),
      save_pct = pmin(pmax(coalesce(as.numeric(`Save%`), 0) / 100, 0), 1),
      clean_sheet_pct = pmin(pmax(coalesce(as.numeric(`CS%`), 0) / 100, 0), 1),
      gols_sofridos_inv = -coalesce(as.numeric(GA90), median(as.numeric(GA90), na.rm = TRUE), 0),
      volume_jogo_norm = log1p(coalesce(minutos, 0)) / log1p(max(coalesce(minutos, 0), na.rm = TRUE)),
      experiencia_norm = log1p(coalesce(jogos, 0)) / log1p(max(coalesce(jogos, 0), na.rm = TRUE)),
      idade_prime_norm = exp(-((coalesce(idade, median(idade, na.rm = TRUE)) - 27)^2) / (2 * 4.5^2))
    )

  variaveis_norm <- c(
    "gols_p90", "assistencias_p90", "participacoes_gol_p90", "finalizacoes_p90",
    "finalizacoes_gol_p90", "cruzamentos_p90", "desarmes_vencidos_p90", "interceptacoes_p90",
    "faltas_sofridas_p90", "eficiencia_chute", "taxa_chutes_gol", "save_pct",
    "clean_sheet_pct", "gols_sofridos_inv"
  )

  for (variavel in variaveis_norm) {
    dados[[paste0(variavel, "_norm")]] <- normalizar_por_posicao(dados, variavel)
  }

  dados |>
    mutate(
      score_ataque = 0.30 * participacoes_gol_p90_norm + 0.18 * gols_p90_norm +
        0.16 * assistencias_p90_norm + 0.12 * finalizacoes_gol_p90_norm +
        0.10 * eficiencia_chute_norm + 0.08 * cruzamentos_p90_norm + 0.06 * volume_jogo_norm,
      score_meio = 0.22 * assistencias_p90_norm + 0.18 * cruzamentos_p90_norm +
        0.16 * faltas_sofridas_p90_norm + 0.14 * participacoes_gol_p90_norm +
        0.12 * desarmes_vencidos_p90_norm + 0.10 * interceptacoes_p90_norm +
        0.08 * volume_jogo_norm,
      score_defesa = 0.30 * desarmes_vencidos_p90_norm + 0.26 * interceptacoes_p90_norm +
        0.12 * cruzamentos_p90_norm + 0.10 * volume_jogo_norm +
        0.10 * experiencia_norm + 0.07 * idade_prime_norm + 0.05 * (1 - pmin(disciplina_p90, 1)),
      score_goleiro = 0.42 * save_pct_norm + 0.24 * clean_sheet_pct_norm +
        0.16 * gols_sofridos_inv_norm + 0.10 * volume_jogo_norm + 0.08 * experiencia_norm,
      indice_desempenho_base = case_when(
        posicao_principal == "GK" ~ score_goleiro,
        posicao_principal == "DF" ~ score_defesa,
        posicao_principal == "MF" ~ score_meio,
        posicao_principal == "FW" ~ score_ataque,
        TRUE ~ (score_ataque + score_meio + score_defesa) / 3
      ),
      penalidade_baixa_amostra = ifelse(minutos >= 900, 1, sqrt(pmax(minutos, 1) / 900)),
      indice_desempenho = pmin(pmax(100 * indice_desempenho_base * penalidade_baixa_amostra, 0), 100),
      incerteza_modelo = pmin(pmax(18 / sqrt(pmax(noventas, 1)) + 4 * (1 - volume_jogo_norm), 3), 28)
    ) |>
    select(
      jogador, nacao_codigo, posicao_original, posicao_principal, clube, liga,
      idade, jogos, minutos, noventas, Gls, Ast, `G+A`, Sh, SoT, `SoT%`, Crs,
      TklW, Int, GA90, Saves, `Save%`, `CS%`, gols_p90, assistencias_p90,
      participacoes_gol_p90, finalizacoes_p90, finalizacoes_gol_p90,
      cruzamentos_p90, desarmes_vencidos_p90, interceptacoes_p90, save_pct,
      clean_sheet_pct, score_ataque, score_meio, score_defesa, score_goleiro,
      indice_desempenho, incerteza_modelo, penalidade_baixa_amostra
    ) |>
    arrange(desc(indice_desempenho), desc(minutos))
}

base_processada <- preparar_base(arquivo_entrada)
readr::write_csv(base_processada, file.path(diretorio_saida, "players_world_cup_monte_carlo_ready.csv"))
readr::write_csv(
  dplyr::slice_head(base_processada, n = 30) |>
    select(jogador, nacao_codigo, posicao_principal, clube, liga, minutos, indice_desempenho),
  file.path(diretorio_saida, "top30_indice_desempenho.csv")
)

metadados <- list(
  dataset_title = "Football Players Stats (2025-2026)",
  dataset_url = "https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2025-2026",
  creator = "Hubert Sidorowicz",
  platform = "Kaggle",
  original_source = "FBref",
  season = "2025-2026",
  version = 34,
  license = "MIT",
  author_of_project = "Diogo Rego - Estudante de Estatística UFPB",
  rows = nrow(base_processada),
  countries = dplyr::n_distinct(base_processada$nacao_codigo),
  clubs = dplyr::n_distinct(base_processada$clube),
  leagues = dplyr::n_distinct(base_processada$liga),
  processed_file = "data/processed/players_world_cup_monte_carlo_ready.csv"
)

jsonlite::write_json(metadados, file.path(diretorio_saida, "metadata.json"), pretty = TRUE, auto_unbox = TRUE)
message("Base processada com sucesso: ", file.path(diretorio_saida, "players_world_cup_monte_carlo_ready.csv"))
