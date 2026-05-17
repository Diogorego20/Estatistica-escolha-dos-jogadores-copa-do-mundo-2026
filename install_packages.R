# -----------------------------------------------------------------------------
# Projeto: Simulação de Monte Carlo para Escolha Estatística de Jogadores
# Autor: Diogo Rego - Estudante de Estatística UFPB
# Objetivo: instalar dependências necessárias para executar o dashboard Shiny.
# -----------------------------------------------------------------------------

pacotes <- c(
  "shiny",
  "bslib",
  "bsicons",
  "dplyr",
  "readr",
  "ggplot2",
  "plotly",
  "DT",
  "scales",
  "tibble",
  "stringr",
  "tidyr",
  "jsonlite"
)

repositorio <- "https://cloud.r-project.org"
pacotes_ausentes <- pacotes[!vapply(pacotes, requireNamespace, logical(1), quietly = TRUE)]

if (length(pacotes_ausentes) == 0) {
  message("Todos os pacotes já estão instalados.")
} else {
  install.packages(pacotes_ausentes, repos = repositorio, dependencies = TRUE)
}
