# -----------------------------------------------------------------------------
# Projeto: Simulação de Monte Carlo para Escolha Estatística de Jogadores
# Autor: Diogo Rego - Estudante de Estatística UFPB
# Arquivo: Funções estatísticas reutilizáveis para o dashboard Shiny
# -----------------------------------------------------------------------------

validar_colunas <- function(dados, colunas_obrigatorias) {
  ausentes <- setdiff(colunas_obrigatorias, names(dados))
  if (length(ausentes) > 0) {
    stop(
      sprintf(
        "Base inválida. As seguintes colunas estão ausentes: %s",
        paste(ausentes, collapse = ", ")
      ),
      call. = FALSE
    )
  }
  invisible(TRUE)
}

carregar_base_jogadores <- function(caminho = "data/processed/players_world_cup_monte_carlo_ready.csv") {
  colunas_obrigatorias <- c(
    "jogador", "nacao_codigo", "posicao_principal", "clube", "liga", "idade",
    "jogos", "minutos", "noventas", "score_ataque", "score_meio",
    "score_defesa", "score_goleiro", "indice_desempenho", "incerteza_modelo"
  )

  if (!file.exists(caminho)) {
    stop(
      "Arquivo processado não encontrado. Execute scripts/prepare_data.py ou scripts/prepare_data.R antes de abrir o dashboard.",
      call. = FALSE
    )
  }

  dados <- readr::read_csv(caminho, show_col_types = FALSE)
  validar_colunas(dados, colunas_obrigatorias)

  dados |>
    dplyr::mutate(
      posicao_principal = factor(posicao_principal, levels = c("GK", "DF", "MF", "FW", "OUT")),
      indice_desempenho = pmax(pmin(as.numeric(indice_desempenho), 100), 0),
      incerteza_modelo = pmax(as.numeric(incerteza_modelo), 1),
      minutos = as.numeric(minutos),
      idade = as.numeric(idade)
    ) |>
    dplyr::filter(!is.na(jogador), !is.na(nacao_codigo), !is.na(posicao_principal))
}

calcular_indice_ajustado <- function(dados, peso_ataque, peso_meio, peso_defesa, peso_goleiro) {
  pesos <- c(
    ataque = peso_ataque,
    meio = peso_meio,
    defesa = peso_defesa,
    goleiro = peso_goleiro
  )

  if (any(is.na(pesos)) || any(pesos < 0)) {
    stop("Os pesos devem ser numéricos e não negativos.", call. = FALSE)
  }

  if (sum(pesos) == 0) {
    pesos[] <- 1
  }

  dados |>
    dplyr::mutate(
      componente_ataque = dplyr::coalesce(score_ataque, 0) * pesos[["ataque"]],
      componente_meio = dplyr::coalesce(score_meio, 0) * pesos[["meio"]],
      componente_defesa = dplyr::coalesce(score_defesa, 0) * pesos[["defesa"]],
      componente_goleiro = dplyr::coalesce(score_goleiro, 0) * pesos[["goleiro"]],
      indice_ajustado_raw = dplyr::case_when(
        posicao_principal == "GK" ~ 0.72 * componente_goleiro + 0.10 * componente_defesa + 0.10 * componente_meio + 0.08 * componente_ataque,
        posicao_principal == "DF" ~ 0.62 * componente_defesa + 0.16 * componente_meio + 0.12 * componente_ataque + 0.10 * componente_goleiro,
        posicao_principal == "MF" ~ 0.50 * componente_meio + 0.23 * componente_ataque + 0.22 * componente_defesa + 0.05 * componente_goleiro,
        posicao_principal == "FW" ~ 0.65 * componente_ataque + 0.20 * componente_meio + 0.10 * componente_defesa + 0.05 * componente_goleiro,
        TRUE ~ componente_ataque + componente_meio + componente_defesa
      ),
      indice_ajustado = 100 * indice_ajustado_raw / max(indice_ajustado_raw, na.rm = TRUE),
      indice_ajustado = pmax(pmin(indice_ajustado, 100), 0)
    )
}

classificar_probabilidade <- function(probabilidade) {
  dplyr::case_when(
    probabilidade >= 0.80 ~ "Favorito estatístico",
    probabilidade >= 0.55 ~ "Forte candidato",
    probabilidade >= 0.30 ~ "Competitivo",
    probabilidade >= 0.10 ~ "Aposta situacional",
    TRUE ~ "Baixa probabilidade"
  )
}

simular_convocacao_monte_carlo <- function(
    dados,
    n_simulacoes = 5000,
    vagas_gk = 3,
    vagas_df = 8,
    vagas_mf = 8,
    vagas_fw = 7,
    fator_incerteza = 1,
    semente = 2026) {

  if (nrow(dados) == 0) {
    return(tibble::tibble())
  }

  if (n_simulacoes < 100) {
    stop("Use pelo menos 100 simulações para obter estabilidade mínima.", call. = FALSE)
  }

  set.seed(semente)

  dados_sim <- dados |>
    dplyr::mutate(
      id_mc = dplyr::row_number(),
      selecionado = 0L,
      desvio_mc = pmax(incerteza_modelo * fator_incerteza, 0.5)
    )

  vagas <- c(GK = vagas_gk, DF = vagas_df, MF = vagas_mf, FW = vagas_fw)
  contagem <- integer(nrow(dados_sim))

  for (s in seq_len(n_simulacoes)) {
    escore_simulado <- stats::rnorm(
      n = nrow(dados_sim),
      mean = dados_sim$indice_ajustado,
      sd = dados_sim$desvio_mc
    )

    for (posicao in names(vagas)) {
      candidatos <- which(as.character(dados_sim$posicao_principal) == posicao)
      n_vagas <- min(vagas[[posicao]], length(candidatos))

      if (n_vagas > 0) {
        escolhidos <- candidatos[order(escore_simulado[candidatos], decreasing = TRUE)][seq_len(n_vagas)]
        contagem[escolhidos] <- contagem[escolhidos] + 1L
      }
    }
  }

  dados_sim |>
    dplyr::mutate(
      selecoes_mc = contagem,
      prob_convocacao = selecoes_mc / n_simulacoes,
      prob_convocacao_pct = 100 * prob_convocacao,
      categoria_prob = classificar_probabilidade(prob_convocacao)
    ) |>
    dplyr::arrange(dplyr::desc(prob_convocacao), dplyr::desc(indice_ajustado), dplyr::desc(minutos)) |>
    dplyr::select(-id_mc, -selecionado, -desvio_mc)
}

resumir_elenco <- function(resultado_mc) {
  if (nrow(resultado_mc) == 0) {
    return(tibble::tibble())
  }

  resultado_mc |>
    dplyr::group_by(posicao_principal) |>
    dplyr::summarise(
      candidatos = dplyr::n(),
      prob_media = mean(prob_convocacao_pct, na.rm = TRUE),
      indice_medio = mean(indice_ajustado, na.rm = TRUE),
      minutos_medianos = stats::median(minutos, na.rm = TRUE),
      .groups = "drop"
    )
}
