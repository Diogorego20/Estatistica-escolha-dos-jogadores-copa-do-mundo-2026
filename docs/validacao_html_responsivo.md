# Validação visual do dashboard HTML responsivo

**Autor:** Diogo Rego - Estudante de Estatística UFPB  
**Arquivo validado:** `dashboard_monte_carlo.html`

## Desktop

A captura em resolução de computador apresentou identidade visual profissional, hierarquia clara de título, autoria, fonte de dados, controles e painéis analíticos. A estrutura em duas colunas ficou adequada para telas largas, com boa legibilidade dos cartões e dos blocos de controle.

## Mobile

A captura em dimensão de celular confirmou que os blocos passam para uma coluna, mas indicou necessidade de ajuste fino para impedir rolagem horizontal e evitar corte de textos longos no título, nos botões de metadados e nos campos do formulário. A validação também mostrou que a captura precisa aguardar mais tempo de execução para registrar os resultados calculados pelo JavaScript e os gráficos.

## Ajustes recomendados

Os ajustes finais devem incluir `overflow-x: hidden`, largura máxima rígida para a página, quebra segura de palavras em títulos e textos longos, `min-width: 0` nos containers em grade e nova captura com espera maior de renderização para confirmar gráficos, métricas e tabela.

## Validação após correção JavaScript

A correção da quebra de linha no exportador CSV eliminou o erro de sintaxe do JavaScript. A captura desktop passou a exibir métricas, seleção de nacionalidade, ranking Monte Carlo e resumo por posição corretamente renderizados. No mobile, os dados também passaram a aparecer nos controles, confirmando que o script executa no navegador.

A inspeção visual ainda indicou que alguns textos longos no cabeçalho mobile ficavam próximos demais da borda direita. Para uma entrega mais robusta em celulares, o CSS deve receber uma redução de fonte no título mobile e larguras explícitas baseadas em `calc(100vw - 28px)` para cartões principais, painéis e sidebar.

## Validação mobile definitiva

Após a redução conservadora da largura textual no cabeçalho e a limitação dos cartões ao viewport, a captura mobile final apresentou título, descrição, metadados, autoria e controles sem corte visual relevante. O HTML ficou adequado para navegação em celulares, mantendo os controles antes dos gráficos e preservando leitura confortável em telas estreitas.

A sintaxe JavaScript incorporada foi validada com `node --check`, e as capturas em Chromium headless confirmaram que a simulação é executada no navegador com os dados incorporados ao próprio arquivo HTML.
