# -----------------------------------------------------------------------------
# Projeto: Simulação de Monte Carlo para Escolha Estatística de Jogadores
# Autor: Diogo Rego - Estudante de Estatística UFPB
# Objetivo: validação técnica mínima de estrutura, dados e sintaxe R.
# -----------------------------------------------------------------------------

arquivos_obrigatorios <- c(
  "app.R",
  "R/monte_carlo.R",
  "scripts/prepare_data.R",
  "install_packages.R",
  "data/raw/players_data_light-2025_2026.csv",
  "data/processed/players_world_cup_monte_carlo_ready.csv",
  "data/processed/metadata.json",
  "docs/dicionario_dados.md",
  "README.md"
)

validar_existencia <- function(caminhos) {
  ausentes <- caminhos[!file.exists(caminhos)]
  if (length(ausentes) > 0) {
    stop(sprintf("Arquivos obrigatórios ausentes: %s", paste(ausentes, collapse = ", ")), call. = FALSE)
  }
  TRUE
}

validar_sintaxe_r <- function(caminhos) {
  for (arquivo in caminhos) {
    parse(arquivo)
  }
  TRUE
}

validar_dados <- function(caminho) {
  dados <- read.csv(caminho, check.names = FALSE)
  colunas_obrigatorias <- c(
    "jogador", "nacao_codigo", "posicao_principal", "clube", "liga",
    "minutos", "score_ataque", "score_meio", "score_defesa", "score_goleiro",
    "indice_desempenho", "incerteza_modelo"
  )
  ausentes <- setdiff(colunas_obrigatorias, names(dados))
  if (length(ausentes) > 0) {
    stop(sprintf("Colunas obrigatórias ausentes na base processada: %s", paste(ausentes, collapse = ", ")), call. = FALSE)
  }
  if (nrow(dados) < 1000) {
    stop("A base processada possui menos linhas que o esperado.", call. = FALSE)
  }
  if (any(dados$indice_desempenho < 0 | dados$indice_desempenho > 100, na.rm = TRUE)) {
    stop("O índice de desempenho deve estar no intervalo [0, 100].", call. = FALSE)
  }
  TRUE
}

validar_existencia(arquivos_obrigatorios)
validar_sintaxe_r(c("app.R", "R/monte_carlo.R", "scripts/prepare_data.R", "install_packages.R"))
validar_dados("data/processed/players_world_cup_monte_carlo_ready.csv")

message("Validação concluída com sucesso.")
