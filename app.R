# -----------------------------------------------------------------------------
# Projeto: Simulação de Monte Carlo para Escolha Estatística de Jogadores
# Autor: Diogo Rego - Estudante de Estatística UFPB
# Aplicação: Dashboard Shiny profissional para análise da Copa do Mundo 2026
# Fonte dos dados: Kaggle / FBref - Football Players Stats (2025-2026)
# -----------------------------------------------------------------------------

pacotes <- c("shiny", "bslib", "bsicons", "dplyr", "readr", "ggplot2", "plotly", "DT", "scales", "tibble")
pacotes_ausentes <- pacotes[!vapply(pacotes, requireNamespace, logical(1), quietly = TRUE)]

if (length(pacotes_ausentes) > 0) {
  stop(
    sprintf(
      "Instale os pacotes necessários antes de executar o app: install.packages(c(%s))",
      paste(sprintf('"%s"', pacotes_ausentes), collapse = ", ")
    ),
    call. = FALSE
  )
}

library(shiny)
library(bslib)
library(bsicons)
library(dplyr)
library(readr)
library(ggplot2)
library(plotly)
library(DT)
library(scales)
library(tibble)

source("R/monte_carlo.R", encoding = "UTF-8")

dados_base <- carregar_base_jogadores()
paises_disponiveis <- sort(unique(dados_base$nacao_codigo))
pais_padrao <- ifelse("BRA" %in% paises_disponiveis, "BRA", paises_disponiveis[[1]])

rotulos_posicao <- c(
  GK = "Goleiros",
  DF = "Defensores",
  MF = "Meio-campistas",
  FW = "Atacantes",
  OUT = "Outros"
)

ui <- page_sidebar(
  title = div(
    class = "app-title",
    "Monte Carlo | Escolha Estatística de Jogadores — Copa do Mundo 2026",
    div(class = "app-subtitle", "Autoria: Diogo Rego - Estudante de Estatística UFPB")
  ),
  theme = bs_theme(
    version = 5,
    bootswatch = "flatly",
    primary = "#0B1F3A",
    secondary = "#D6A84F",
    base_font = font_google("Inter"),
    heading_font = font_google("Inter")
  ),
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "style.css")
  ),
  sidebar = sidebar(
    width = 360,
    h4("Parâmetros da simulação"),
    selectizeInput(
      "pais", "Seleção / nacionalidade analisada",
      choices = paises_disponiveis,
      selected = pais_padrao,
      multiple = FALSE
    ),
    sliderInput("min_minutos", "Minutos mínimos em campo", min = 0, max = 2500, value = 450, step = 50, sep = "."),
    sliderInput("n_sim", "Número de simulações Monte Carlo", min = 500, max = 20000, value = 5000, step = 500, sep = "."),
    sliderInput("fator_incerteza", "Fator de incerteza competitiva", min = 0.25, max = 2.50, value = 1.00, step = 0.05),
    numericInput("semente", "Semente reprodutível", value = 2026, min = 1, step = 1),
    hr(),
    h4("Composição do elenco"),
    fluidRow(
      column(6, numericInput("vagas_gk", "GK", value = 3, min = 1, max = 5, step = 1)),
      column(6, numericInput("vagas_df", "DF", value = 8, min = 1, max = 12, step = 1))
    ),
    fluidRow(
      column(6, numericInput("vagas_mf", "MF", value = 8, min = 1, max = 12, step = 1)),
      column(6, numericInput("vagas_fw", "FW", value = 7, min = 1, max = 12, step = 1))
    ),
    hr(),
    h4("Pesos do índice autoral"),
    sliderInput("peso_ataque", "Ênfase em ataque", min = 0, max = 100, value = 35, step = 1),
    sliderInput("peso_meio", "Ênfase em criação/meio", min = 0, max = 100, value = 25, step = 1),
    sliderInput("peso_defesa", "Ênfase em defesa", min = 0, max = 100, value = 25, step = 1),
    sliderInput("peso_goleiro", "Ênfase em goleiro", min = 0, max = 100, value = 15, step = 1),
    hr(),
    downloadButton("baixar_resultado", "Baixar resultado da simulação", class = "btn-download")
  ),
  layout_columns(
    col_widths = c(3, 3, 3, 3),
    value_box(title = "Candidatos filtrados", value = textOutput("vb_candidatos"), showcase = bsicons::bs_icon("people-fill"), theme = "primary"),
    value_box(title = "Elenco simulado", value = textOutput("vb_elenco"), showcase = bsicons::bs_icon("shield-fill-check"), theme = "secondary"),
    value_box(title = "Índice máximo", value = textOutput("vb_indice"), showcase = bsicons::bs_icon("graph-up-arrow"), theme = "success"),
    value_box(title = "Fonte", value = "Kaggle / FBref", showcase = bsicons::bs_icon("database-fill"), theme = "info")
  ),
  navset_card_tab(
    nav_panel(
      "Ranking Monte Carlo",
      layout_columns(
        col_widths = c(7, 5),
        card(
          card_header("Probabilidade estimada de convocação"),
          plotlyOutput("grafico_probabilidade", height = "560px")
        ),
        card(
          card_header("Distribuição por posição"),
          plotlyOutput("grafico_posicao", height = "560px")
        )
      )
    ),
    nav_panel(
      "Tabela analítica",
      card(
        card_header("Resultado detalhado da simulação"),
        DTOutput("tabela_resultado")
      )
    ),
    nav_panel(
      "Diagnóstico estatístico",
      layout_columns(
        col_widths = c(6, 6),
        card(card_header("Índice ajustado versus incerteza"), plotlyOutput("grafico_dispersao", height = "520px")),
        card(card_header("Resumo por posição"), DTOutput("tabela_resumo"))
      )
    ),
    nav_panel(
      "Metodologia",
      card(
        card_header("Como interpretar o modelo"),
        div(
          class = "methodology-text",
          p("Este dashboard utiliza uma abordagem estatística autoral de Monte Carlo para estimar probabilidades relativas de escolha de jogadores em uma composição hipotética de elenco para a Copa do Mundo 2026."),
          p("O índice de desempenho combina estatísticas ofensivas, criativas, defensivas e de goleiro. As variáveis são normalizadas dentro de grupos posicionais, recebem penalização para baixa amostra de minutos e são submetidas a perturbações aleatórias controladas pela incerteza individual."),
          p("A simulação não afirma a convocação real de nenhum atleta. Ela oferece uma leitura quantitativa, transparente e reprodutível das estatísticas disponíveis na temporada 2025-2026 das cinco principais ligas europeias."),
          tags$blockquote("Fonte dos dados: Football Players Stats (2025-2026), Kaggle, criado por Hubert Sidorowicz e derivado de estatísticas do FBref."),
          p(strong("Autoria do projeto estatístico, código e metodologia aplicada: Diogo Rego - Estudante de Estatística UFPB."))
        )
      )
    )
  )
)

server <- function(input, output, session) {
  dados_filtrados <- reactive({
    dados_base |>
      filter(nacao_codigo == input$pais, minutos >= input$min_minutos, posicao_principal %in% c("GK", "DF", "MF", "FW")) |>
      calcular_indice_ajustado(
        peso_ataque = input$peso_ataque,
        peso_meio = input$peso_meio,
        peso_defesa = input$peso_defesa,
        peso_goleiro = input$peso_goleiro
      )
  })

  resultado_mc <- reactive({
    req(nrow(dados_filtrados()) > 0)
    simular_convocacao_monte_carlo(
      dados = dados_filtrados(),
      n_simulacoes = input$n_sim,
      vagas_gk = input$vagas_gk,
      vagas_df = input$vagas_df,
      vagas_mf = input$vagas_mf,
      vagas_fw = input$vagas_fw,
      fator_incerteza = input$fator_incerteza,
      semente = input$semente
    )
  })

  output$vb_candidatos <- renderText({
    scales::comma(nrow(dados_filtrados()), big.mark = ".", decimal.mark = ",")
  })

  output$vb_elenco <- renderText({
    sum(input$vagas_gk, input$vagas_df, input$vagas_mf, input$vagas_fw)
  })

  output$vb_indice <- renderText({
    sprintf("%.1f", max(dados_filtrados()$indice_ajustado, na.rm = TRUE))
  })

  output$grafico_probabilidade <- renderPlotly({
    dados_plot <- resultado_mc() |>
      slice_max(prob_convocacao_pct, n = 25, with_ties = FALSE) |>
      mutate(jogador = reorder(jogador, prob_convocacao_pct))

    p <- ggplot(dados_plot, aes(x = prob_convocacao_pct, y = jogador, fill = posicao_principal, text = paste0(
      "Jogador: ", jogador,
      "<br>Posição: ", posicao_principal,
      "<br>Clube: ", clube,
      "<br>Probabilidade: ", sprintf("%.1f%%", prob_convocacao_pct),
      "<br>Índice ajustado: ", sprintf("%.1f", indice_ajustado)
    ))) +
      geom_col(width = 0.72, alpha = 0.94) +
      scale_fill_manual(values = c(GK = "#1B998B", DF = "#2D3047", MF = "#F4B942", FW = "#E84855"), labels = rotulos_posicao) +
      scale_x_continuous(labels = function(x) paste0(x, "%"), limits = c(0, 100)) +
      labs(x = "Probabilidade de seleção nas simulações", y = NULL, fill = "Posição") +
      theme_minimal(base_family = "Inter") +
      theme(panel.grid.major.y = element_blank(), legend.position = "bottom")

    ggplotly(p, tooltip = "text") |> layout(legend = list(orientation = "h", x = 0.05, y = -0.12))
  })

  output$grafico_posicao <- renderPlotly({
    dados_plot <- resultado_mc() |>
      group_by(posicao_principal, categoria_prob) |>
      summarise(jogadores = n(), prob_media = mean(prob_convocacao_pct), .groups = "drop")

    p <- ggplot(dados_plot, aes(x = posicao_principal, y = jogadores, fill = categoria_prob, text = paste0(
      "Posição: ", posicao_principal,
      "<br>Categoria: ", categoria_prob,
      "<br>Jogadores: ", jogadores,
      "<br>Prob. média: ", sprintf("%.1f%%", prob_media)
    ))) +
      geom_col(position = "stack", width = 0.68) +
      scale_fill_manual(values = c(
        "Favorito estatístico" = "#0B1F3A",
        "Forte candidato" = "#1B998B",
        "Competitivo" = "#F4B942",
        "Aposta situacional" = "#E84855",
        "Baixa probabilidade" = "#A7A9AC"
      )) +
      labs(x = "Posição", y = "Número de jogadores", fill = "Categoria") +
      theme_minimal(base_family = "Inter") +
      theme(legend.position = "bottom")

    ggplotly(p, tooltip = "text") |> layout(legend = list(orientation = "h", x = 0.0, y = -0.18))
  })

  output$grafico_dispersao <- renderPlotly({
    dados_plot <- resultado_mc()

    p <- ggplot(dados_plot, aes(
      x = indice_ajustado,
      y = incerteza_modelo,
      size = minutos,
      color = prob_convocacao_pct,
      text = paste0(
        "Jogador: ", jogador,
        "<br>Clube: ", clube,
        "<br>Posição: ", posicao_principal,
        "<br>Índice: ", sprintf("%.1f", indice_ajustado),
        "<br>Incerteza: ", sprintf("%.1f", incerteza_modelo),
        "<br>Probabilidade: ", sprintf("%.1f%%", prob_convocacao_pct)
      )
    )) +
      geom_point(alpha = 0.78) +
      scale_color_viridis_c(option = "C", labels = function(x) paste0(x, "%")) +
      scale_size_continuous(range = c(3, 14), labels = scales::comma) +
      labs(x = "Índice ajustado", y = "Incerteza individual", color = "Probabilidade", size = "Minutos") +
      theme_minimal(base_family = "Inter") +
      theme(legend.position = "right")

    ggplotly(p, tooltip = "text")
  })

  output$tabela_resultado <- renderDT({
    resultado_mc() |>
      transmute(
        Jogador = jogador,
        Posição = as.character(posicao_principal),
        Clube = clube,
        Liga = liga,
        Idade = idade,
        Minutos = round(minutos, 0),
        `Índice ajustado` = round(indice_ajustado, 2),
        `Incerteza` = round(incerteza_modelo, 2),
        `Probabilidade (%)` = round(prob_convocacao_pct, 2),
        Categoria = categoria_prob
      ) |>
      datatable(
        rownames = FALSE,
        filter = "top",
        extensions = c("Buttons", "Responsive"),
        options = list(
          pageLength = 15,
          scrollX = TRUE,
          responsive = TRUE,
          dom = "Bfrtip",
          buttons = c("copy", "csv", "excel")
        )
      ) |>
      formatStyle("Probabilidade (%)", background = styleColorBar(c(0, 100), "#D6A84F"), backgroundSize = "98% 88%", backgroundRepeat = "no-repeat", backgroundPosition = "center")
  })

  output$tabela_resumo <- renderDT({
    resumir_elenco(resultado_mc()) |>
      mutate(
        posicao_principal = as.character(posicao_principal),
        prob_media = round(prob_media, 2),
        indice_medio = round(indice_medio, 2),
        minutos_medianos = round(minutos_medianos, 0)
      ) |>
      rename(
        Posição = posicao_principal,
        Candidatos = candidatos,
        `Probabilidade média (%)` = prob_media,
        `Índice médio` = indice_medio,
        `Minutos medianos` = minutos_medianos
      ) |>
      datatable(rownames = FALSE, options = list(dom = "t", pageLength = 8))
  })

  output$baixar_resultado <- downloadHandler(
    filename = function() {
      paste0("resultado_monte_carlo_", input$pais, "_", Sys.Date(), ".csv")
    },
    content = function(file) {
      readr::write_csv(resultado_mc(), file)
    }
  )
}

shinyApp(ui, server)
