#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projeto: Simulação de Monte Carlo para Escolha Estatística de Jogadores
Autor: Diogo Rego - Estudante de Estatística UFPB
Arquivo: Gerador de dashboard HTML responsivo e interativo.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "players_world_cup_monte_carlo_ready.csv"
OUT_PATH = ROOT / "dashboard_monte_carlo.html"

COLS = [
    "jogador", "nacao_codigo", "posicao_principal", "clube", "liga", "idade",
    "jogos", "minutos", "noventas", "score_ataque", "score_meio", "score_defesa",
    "score_goleiro", "indice_desempenho", "incerteza_modelo",
    "gols_p90", "assistencias_p90", "participacoes_gol_p90", "finalizacoes_p90",
    "desarmes_vencidos_p90", "interceptacoes_p90", "save_pct", "clean_sheet_pct"
]


def clean_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, float):
        return round(value, 5)
    return value


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Base processada não encontrada: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    keep = [c for c in COLS if c in df.columns]
    df = df[keep].copy()
    df = df[df["posicao_principal"].isin(["GK", "DF", "MF", "FW"])]
    df["jogador"] = df["jogador"].astype(str)
    df["nacao_codigo"] = df["nacao_codigo"].astype(str)
    df["posicao_principal"] = df["posicao_principal"].astype(str)
    df["clube"] = df["clube"].fillna("Não informado").astype(str)
    df["liga"] = df["liga"].fillna("Não informado").astype(str)

    numeric_cols = [c for c in df.columns if c not in {"jogador", "nacao_codigo", "posicao_principal", "clube", "liga"}]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    records = [
        {col: clean_value(row[col]) for col in df.columns}
        for _, row in df.iterrows()
    ]

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="author" content="Diogo Rego - Estudante de Estatística UFPB" />
  <meta name="description" content="Dashboard HTML responsivo com simulação de Monte Carlo para escolha estatística de jogadores da Copa do Mundo 2026." />
  <title>Monte Carlo | Escolha de Jogadores Copa 2026</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg: #07111f;
      --panel: rgba(15, 28, 48, 0.92);
      --panel-soft: rgba(255, 255, 255, 0.075);
      --text: #f7fbff;
      --muted: #b6c7dc;
      --gold: #d6a84f;
      --green: #1b998b;
      --red: #e84855;
      --blue: #3273dc;
      --ink: #0b1f3a;
      --line: rgba(255,255,255,0.14);
      --shadow: 0 24px 70px rgba(0,0,0,0.34);
      --radius: 22px;
    }}

    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; max-width: 100%; overflow-x: hidden; }}
    body {{
      margin: 0;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(50, 115, 220, 0.35), transparent 34rem),
        radial-gradient(circle at top right, rgba(214, 168, 79, 0.22), transparent 30rem),
        linear-gradient(135deg, #07111f 0%, #0b1f3a 52%, #06101d 100%);
      color: var(--text);
      min-height: 100vh;
      max-width: 100%;
      overflow-x: hidden;
    }}

    a {{ color: #9cc3ff; }}

    .page {{ width: min(1440px, 100%); max-width: 100%; margin: 0 auto; padding: 28px; overflow-x: hidden; }}

    .hero {{
      display: grid;
      grid-template-columns: 1.25fr 0.75fr;
      gap: 24px;
      align-items: stretch;
      margin-bottom: 24px;
    }}

    .hero > *, .controls-layout > *, .content-grid > *, .metrics > *, .method > * {{ min-width: 0; }}

    .hero-card, .panel, .metric, .method-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }}

    .hero-card {{ padding: 34px; position: relative; overflow: hidden; }}
    .hero-card::after {{
      content: "";
      position: absolute;
      inset: auto -80px -110px auto;
      width: 280px;
      height: 280px;
      background: radial-gradient(circle, rgba(214,168,79,0.32), transparent 70%);
      pointer-events: none;
    }}

    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      color: #ffe5a6;
      background: rgba(214,168,79,0.12);
      border: 1px solid rgba(214,168,79,0.38);
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      font-size: 0.78rem;
    }}

    h1 {{
      margin: 18px 0 12px;
      font-size: clamp(2.05rem, 5vw, 4.35rem);
      line-height: 1.02;
      letter-spacing: -0.055em;
      overflow-wrap: anywhere;
    }}

    h2 {{ margin: 0 0 14px; font-size: clamp(1.25rem, 2.5vw, 1.8rem); }}
    h3 {{ margin: 0 0 12px; color: #ffffff; }}
    p {{ color: var(--muted); line-height: 1.72; }}

    .hero-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 22px;
    }}

    .pill {{
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.08);
      color: #eef6ff;
      border-radius: 999px;
      padding: 9px 12px;
      font-size: 0.88rem;
      font-weight: 650;
      max-width: 100%;
      overflow-wrap: anywhere;
    }}

    .author-card {{ padding: 26px; display: flex; flex-direction: column; justify-content: space-between; }}
    .author-name {{ font-size: 1.32rem; font-weight: 800; margin: 6px 0; }}
    .source {{ font-size: 0.94rem; color: var(--muted); }}

    .controls-layout {{
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 24px;
      align-items: start;
    }}

    .sidebar {{ position: sticky; top: 18px; padding: 22px; }}
    .control-group {{ margin-bottom: 18px; }}
    label {{ display: block; font-size: 0.86rem; color: #dbe8f8; font-weight: 750; margin-bottom: 8px; }}
    select, input[type="number"], input[type="range"] {{
      width: 100%;
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 13px;
      background: rgba(255,255,255,0.10);
      color: var(--text);
      padding: 12px 13px;
      outline: none;
      font-size: 0.98rem;
    }}
    select option {{ color: #0b1f3a; }}
    input[type="range"] {{ padding: 5px 0; accent-color: var(--gold); }}
    .range-row {{ display: flex; align-items: center; gap: 12px; }}
    .range-row output {{ min-width: 44px; text-align: right; color: #ffe5a6; font-weight: 800; }}

    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
    .btn {{
      width: 100%;
      border: 0;
      border-radius: 15px;
      padding: 14px 16px;
      background: linear-gradient(135deg, #d6a84f, #f3d48a);
      color: #07111f;
      font-weight: 900;
      cursor: pointer;
      box-shadow: 0 12px 26px rgba(214,168,79,0.25);
    }}
    .btn.secondary {{ background: rgba(255,255,255,0.10); color: var(--text); border: 1px solid var(--line); box-shadow: none; }}

    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }}
    .metric {{ padding: 18px; }}
    .metric small {{ color: var(--muted); font-weight: 700; }}
    .metric strong {{ display: block; margin-top: 8px; font-size: clamp(1.55rem, 3vw, 2.35rem); letter-spacing: -0.04em; }}

    .content-grid {{ display: grid; grid-template-columns: 1.3fr 0.7fr; gap: 20px; }}
    .panel {{ padding: 22px; margin-bottom: 20px; overflow: hidden; }}
    .chart-wrap {{ position: relative; height: 430px; }}
    .chart-wrap.small {{ height: 330px; }}

    .table-wrap {{ overflow-x: auto; border-radius: 16px; border: 1px solid var(--line); }}
    table {{ width: 100%; border-collapse: collapse; min-width: 920px; }}
    th, td {{ padding: 12px 13px; border-bottom: 1px solid rgba(255,255,255,0.09); text-align: left; white-space: nowrap; }}
    th {{ background: rgba(255,255,255,0.08); color: #ffffff; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em; }}
    td {{ color: #e7f1ff; font-size: 0.94rem; }}
    tr:hover td {{ background: rgba(255,255,255,0.045); }}
    .tag {{ display: inline-block; border-radius: 999px; padding: 5px 9px; font-weight: 800; font-size: 0.78rem; }}
    .tag.GK {{ background: rgba(27,153,139,0.18); color: #74fff0; }}
    .tag.DF {{ background: rgba(90,102,150,0.28); color: #d9dfff; }}
    .tag.MF {{ background: rgba(214,168,79,0.20); color: #ffe19a; }}
    .tag.FW {{ background: rgba(232,72,85,0.20); color: #ffb5bc; }}

    .method {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-top: 4px; }}
    .method-card {{ padding: 20px; }}
    .method-card strong {{ color: #ffffff; }}

    .footer {{
      margin: 24px 0 10px;
      padding: 22px;
      text-align: center;
      color: var(--muted);
      border-top: 1px solid var(--line);
    }}

    .status-line {{ color: #ffe5a6; font-size: 0.92rem; min-height: 1.35rem; }}

    @media (max-width: 1100px) {{
      .hero, .controls-layout, .content-grid {{ grid-template-columns: 1fr; }}
      .sidebar {{ position: relative; top: auto; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .method {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 620px) {{
      .page {{ padding: 14px; width: 100vw; max-width: 100vw; }}
      .hero, .controls-layout, .content-grid {{ width: 100%; max-width: 100%; overflow: hidden; }}
      .hero-card, .author-card, .panel, .sidebar {{ padding: 18px; border-radius: 18px; width: 100%; max-width: calc(100vw - 28px); overflow: hidden; }}
      .metrics {{ grid-template-columns: 1fr; }}
      .grid-2 {{ grid-template-columns: 1fr; }}
      .chart-wrap {{ height: 390px; width: 100%; }}
      .chart-wrap.small {{ height: 310px; }}
      h1 {{ font-size: clamp(1.58rem, 6.9vw, 1.92rem); line-height: 1.14; letter-spacing: -0.018em; max-width: min(100%, 20ch); overflow-wrap: break-word; word-break: normal; }}
      p {{ font-size: 0.94rem; max-width: min(100%, 38ch); overflow-wrap: break-word; }}
      .hero-card p, .author-card p, .sidebar p {{ max-width: min(100%, 34ch); }}
      .hero-meta {{ gap: 8px; }}
      .pill {{ font-size: 0.78rem; }}
      table {{ min-width: 760px; }}
      .hero-meta {{ display: grid; grid-template-columns: 1fr; align-items: stretch; }}
      .pill {{ width: 100%; text-align: center; }}
      select, input[type="number"], input[type="range"] {{ max-width: 100%; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <article class="hero-card">
        <span class="eyebrow">R/Shiny · HTML Responsivo · Monte Carlo</span>
        <h1>Escolha Estatística de Jogadores para a Copa do Mundo 2026</h1>
        <p>Arquivo HTML interativo com filtros, pesos configuráveis, composição de elenco e simulação de Monte Carlo executada diretamente no navegador. A proposta preserva a metodologia do projeto em R/Shiny e funciona em computadores, tablets e celulares.</p>
        <div class="hero-meta">
          <span class="pill">Base Kaggle / FBref 2025-2026</span>
          <span class="pill">Índice autoral 0–100</span>
          <span class="pill">Probabilidade por frequência simulada</span>
          <span class="pill">Layout mobile-first</span>
        </div>
      </article>
      <aside class="author-card">
        <div>
          <span class="eyebrow">Autoria</span>
          <div class="author-name">Diogo Rego</div>
          <p>Estudante de Estatística UFPB</p>
        </div>
        <div class="source">
          <strong>Fonte dos dados:</strong><br />Football Players Stats (2025-2026), Kaggle / FBref.<br /><br />Este painel é acadêmico e exploratório; não representa convocação oficial.
        </div>
      </aside>
    </section>

    <section class="controls-layout">
      <aside class="panel sidebar" aria-label="Controles da simulação">
        <h2>Controles do modelo</h2>
        <p>Altere os parâmetros e execute a simulação. Em celulares, os controles aparecem antes dos gráficos para facilitar o uso.</p>

        <div class="control-group">
          <label for="country">Nacionalidade</label>
          <select id="country"></select>
        </div>

        <div class="grid-2">
          <div class="control-group">
            <label for="minMinutes">Minutos mínimos</label>
            <input id="minMinutes" type="number" min="0" max="6000" step="50" value="450" />
          </div>
          <div class="control-group">
            <label for="nSims">Simulações</label>
            <input id="nSims" type="number" min="100" max="10000" step="100" value="1500" />
          </div>
        </div>

        <div class="control-group">
          <label for="uncertainty">Fator de incerteza</label>
          <div class="range-row"><input id="uncertainty" type="range" min="0.5" max="2.5" step="0.1" value="1.0" /><output id="uncertaintyOut">1.0</output></div>
        </div>

        <h3>Vagas por posição</h3>
        <div class="grid-2">
          <div class="control-group"><label for="vGK">Goleiros</label><input id="vGK" type="number" min="0" max="5" value="3" /></div>
          <div class="control-group"><label for="vDF">Defensores</label><input id="vDF" type="number" min="0" max="12" value="8" /></div>
          <div class="control-group"><label for="vMF">Meias</label><input id="vMF" type="number" min="0" max="12" value="8" /></div>
          <div class="control-group"><label for="vFW">Atacantes</label><input id="vFW" type="number" min="0" max="12" value="7" /></div>
        </div>

        <h3>Pesos do índice</h3>
        <div class="grid-2">
          <div class="control-group"><label for="wAtk">Ataque</label><input id="wAtk" type="number" min="0" max="5" step="0.1" value="1" /></div>
          <div class="control-group"><label for="wMid">Meio</label><input id="wMid" type="number" min="0" max="5" step="0.1" value="1" /></div>
          <div class="control-group"><label for="wDef">Defesa</label><input id="wDef" type="number" min="0" max="5" step="0.1" value="1" /></div>
          <div class="control-group"><label for="wGk">Goleiro</label><input id="wGk" type="number" min="0" max="5" step="0.1" value="1" /></div>
        </div>

        <div class="grid-2">
          <button class="btn" id="runBtn">Executar Monte Carlo</button>
          <button class="btn secondary" id="downloadBtn">Baixar CSV</button>
        </div>
        <p class="status-line" id="status"></p>
      </aside>

      <section>
        <div class="metrics">
          <div class="metric"><small>Candidatos elegíveis</small><strong id="mCandidates">—</strong></div>
          <div class="metric"><small>Elenco configurado</small><strong id="mSquad">—</strong></div>
          <div class="metric"><small>Favorito estatístico</small><strong id="mTop">—</strong></div>
          <div class="metric"><small>Probabilidade líder</small><strong id="mProb">—</strong></div>
        </div>

        <div class="content-grid">
          <article class="panel">
            <h2>Ranking Monte Carlo</h2>
            <p>Probabilidade estimada de seleção em cada rodada simulada, após aplicar pesos, incerteza e vagas por posição.</p>
            <div class="chart-wrap"><canvas id="rankChart"></canvas></div>
          </article>

          <article class="panel">
            <h2>Resumo por posição</h2>
            <p>Distribuição média de probabilidade e número de candidatos por função.</p>
            <div class="chart-wrap small"><canvas id="positionChart"></canvas></div>
          </article>
        </div>

        <article class="panel">
          <h2>Risco estatístico: índice ajustado × incerteza</h2>
          <p>Jogadores mais à direita possuem índice maior; pontos mais altos carregam mais incerteza no sorteio Monte Carlo.</p>
          <div class="chart-wrap small"><canvas id="scatterChart"></canvas></div>
        </article>

        <article class="panel">
          <h2>Tabela analítica</h2>
          <p>A tabela mostra os principais jogadores do cenário atual. Use a rolagem horizontal em celulares para visualizar todas as colunas.</p>
          <div class="table-wrap"><table id="resultTable"></table></div>
        </article>

        <section class="method">
          <div class="method-card"><strong>1. Índice ajustado</strong><p>Combina ataque, meio, defesa e goleiro conforme a posição principal do jogador e os pesos definidos pelo usuário.</p></div>
          <div class="method-card"><strong>2. Incerteza individual</strong><p>Atletas com menor volume de minutos possuem maior variabilidade simulada, protegendo a análise contra baixa amostra.</p></div>
          <div class="method-card"><strong>3. Frequência Monte Carlo</strong><p>A probabilidade final é a fração de simulações em que o jogador aparece dentro das vagas de sua posição.</p></div>
        </section>
      </section>
    </section>

    <footer class="footer">
      <strong>Autoria:</strong> Diogo Rego - Estudante de Estatística UFPB · <strong>Fonte:</strong> Kaggle / FBref, Football Players Stats (2025-2026).<br />
      Projeto acadêmico de estatística aplicada ao futebol, com apresentação responsiva para computadores e celulares.
    </footer>
  </main>

  <script>
    const PLAYERS = {json.dumps(records, ensure_ascii=False, separators=(",", ":"))};
    const POS_COLORS = {{ GK: '#1b998b', DF: '#5f6b9a', MF: '#d6a84f', FW: '#e84855' }};
    let rankChart, positionChart, scatterChart;
    let latestResults = [];

    const $ = (id) => document.getElementById(id);
    const num = (id) => Number($(id).value || 0);
    const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));
    const fmt = (x, d=1) => Number.isFinite(x) ? x.toFixed(d) : '0.0';

    function mulberry32(seed) {{
      return function() {{
        let t = seed += 0x6D2B79F5;
        t = Math.imul(t ^ t >>> 15, t | 1);
        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
      }};
    }}

    function normalRandom(rng) {{
      let u = 0, v = 0;
      while (u === 0) u = rng();
      while (v === 0) v = rng();
      return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    }}

    function category(prob) {{
      if (prob >= 0.80) return 'Favorito estatístico';
      if (prob >= 0.55) return 'Forte candidato';
      if (prob >= 0.30) return 'Competitivo';
      if (prob >= 0.10) return 'Aposta situacional';
      return 'Baixa probabilidade';
    }}

    function setupCountries() {{
      const counts = new Map();
      PLAYERS.forEach(p => counts.set(p.nacao_codigo, (counts.get(p.nacao_codigo) || 0) + 1));
      const countries = [...counts.entries()].sort((a,b) => b[1] - a[1]);
      $('country').innerHTML = countries.map(([c,n]) => `<option value="${{c}}">${{c}} — ${{n}} jogadores</option>`).join('');
      if ([...counts.keys()].includes('BRA')) $('country').value = 'BRA';
    }}

    function computeAdjusted(players) {{
      const weights = {{ atk: num('wAtk'), mid: num('wMid'), def: num('wDef'), gk: num('wGk') }};
      const enriched = players.map(p => {{
        const atk = (p.score_ataque || 0) * weights.atk;
        const mid = (p.score_meio || 0) * weights.mid;
        const def = (p.score_defesa || 0) * weights.def;
        const gk = (p.score_goleiro || 0) * weights.gk;
        let raw = atk + mid + def;
        if (p.posicao_principal === 'GK') raw = 0.72*gk + 0.10*def + 0.10*mid + 0.08*atk;
        if (p.posicao_principal === 'DF') raw = 0.62*def + 0.16*mid + 0.12*atk + 0.10*gk;
        if (p.posicao_principal === 'MF') raw = 0.50*mid + 0.23*atk + 0.22*def + 0.05*gk;
        if (p.posicao_principal === 'FW') raw = 0.65*atk + 0.20*mid + 0.10*def + 0.05*gk;
        return {{...p, indice_raw: raw}};
      }});
      const maxRaw = Math.max(...enriched.map(p => p.indice_raw || 0), 1e-9);
      return enriched.map(p => ({{...p, indice_ajustado: clamp(100 * (p.indice_raw || 0) / maxRaw, 0, 100)}}));
    }}

    function simulate() {{
      $('status').textContent = 'Executando simulação no navegador...';
      const t0 = performance.now();
      const country = $('country').value;
      const minMinutes = num('minMinutes');
      const nSims = clamp(Math.round(num('nSims')), 100, 10000);
      const uncertainty = Number($('uncertainty').value);
      const vacancies = {{ GK: num('vGK'), DF: num('vDF'), MF: num('vMF'), FW: num('vFW') }};
      const seedBase = 2026 + country.split('').reduce((a,ch) => a + ch.charCodeAt(0), 0) + Math.round(minMinutes);
      const rng = mulberry32(seedBase);

      const eligible = computeAdjusted(PLAYERS.filter(p => p.nacao_codigo === country && (p.minutos || 0) >= minMinutes));
      const selected = new Array(eligible.length).fill(0);
      const byPos = {{ GK: [], DF: [], MF: [], FW: [] }};
      eligible.forEach((p, i) => {{ if (byPos[p.posicao_principal]) byPos[p.posicao_principal].push(i); }});

      for (let s = 0; s < nSims; s++) {{
        const scores = eligible.map(p => p.indice_ajustado + normalRandom(rng) * Math.max((p.incerteza_modelo || 1) * uncertainty, 0.5));
        for (const pos of Object.keys(vacancies)) {{
          const ids = byPos[pos] || [];
          const n = Math.min(vacancies[pos], ids.length);
          if (n <= 0) continue;
          ids.slice().sort((a,b) => scores[b] - scores[a]).slice(0,n).forEach(i => selected[i]++);
        }}
      }}

      latestResults = eligible.map((p, i) => {{
        const prob = selected[i] / nSims;
        return {{...p, selecoes_mc: selected[i], prob_convocacao: prob, prob_pct: 100*prob, categoria_prob: category(prob)}};
      }}).sort((a,b) => b.prob_convocacao - a.prob_convocacao || b.indice_ajustado - a.indice_ajustado || b.minutos - a.minutos);

      updateUI(latestResults, vacancies, performance.now() - t0);
    }}

    function updateUI(results, vacancies, elapsed) {{
      const squad = Object.values(vacancies).reduce((a,b) => a + b, 0);
      $('mCandidates').textContent = results.length.toLocaleString('pt-BR');
      $('mSquad').textContent = squad.toLocaleString('pt-BR');
      $('mTop').textContent = results[0]?.jogador || '—';
      $('mProb').textContent = results[0] ? `${{fmt(results[0].prob_pct, 1)}}%` : '—';
      $('status').textContent = `Simulação concluída em ${{fmt(elapsed/1000, 2)}}s. Resultado baseado em ${{num('nSims').toLocaleString('pt-BR')}} rodadas.`;
      renderRank(results);
      renderPosition(results);
      renderScatter(results);
      renderTable(results);
    }}

    function renderRank(results) {{
      const top = results.slice(0, 15).reverse();
      const ctx = $('rankChart');
      if (rankChart) rankChart.destroy();
      rankChart = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: top.map(p => p.jogador), datasets: [{{ label: 'Probabilidade (%)', data: top.map(p => p.prob_pct), backgroundColor: top.map(p => POS_COLORS[p.posicao_principal] || '#ccc'), borderRadius: 10 }}] }},
        options: {{ indexAxis: 'y', maintainAspectRatio: false, responsive: true, plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ afterLabel: c => `${{top[c.dataIndex].posicao_principal}} · ${{top[c.dataIndex].clube}}` }} }} }}, scales: {{ x: {{ min: 0, max: 100, ticks: {{ color: '#dbe8f8' }}, grid: {{ color: 'rgba(255,255,255,0.10)' }} }}, y: {{ ticks: {{ color: '#dbe8f8' }}, grid: {{ display: false }} }} }} }}
      }});
    }}

    function renderPosition(results) {{
      const positions = ['GK','DF','MF','FW'];
      const means = positions.map(pos => {{ const arr = results.filter(p => p.posicao_principal === pos); return arr.length ? arr.reduce((a,p)=>a+p.prob_pct,0)/arr.length : 0; }});
      const ctx = $('positionChart');
      if (positionChart) positionChart.destroy();
      positionChart = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: positions, datasets: [{{ label: 'Probabilidade média (%)', data: means, backgroundColor: positions.map(p => POS_COLORS[p]), borderRadius: 10 }}] }},
        options: {{ maintainAspectRatio: false, responsive: true, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ ticks: {{ color: '#dbe8f8' }}, grid: {{ display: false }} }}, y: {{ beginAtZero: true, ticks: {{ color: '#dbe8f8' }}, grid: {{ color: 'rgba(255,255,255,0.10)' }} }} }} }}
      }});
    }}

    function renderScatter(results) {{
      const top = results.slice(0, 80);
      const ctx = $('scatterChart');
      if (scatterChart) scatterChart.destroy();
      scatterChart = new Chart(ctx, {{
        type: 'scatter',
        data: {{ datasets: ['GK','DF','MF','FW'].map(pos => ({{ label: pos, data: top.filter(p => p.posicao_principal === pos).map(p => ({{x: p.indice_ajustado, y: p.incerteza_modelo, jogador: p.jogador, prob: p.prob_pct}})), backgroundColor: POS_COLORS[pos] }})) }},
        options: {{ maintainAspectRatio: false, responsive: true, plugins: {{ legend: {{ labels: {{ color: '#dbe8f8' }} }}, tooltip: {{ callbacks: {{ label: c => `${{c.raw.jogador}}: índice ${{fmt(c.raw.x,1)}} · incerteza ${{fmt(c.raw.y,1)}} · prob. ${{fmt(c.raw.prob,1)}}%` }} }} }}, scales: {{ x: {{ title: {{ display:true, text:'Índice ajustado', color:'#dbe8f8' }}, ticks: {{ color: '#dbe8f8' }}, grid: {{ color: 'rgba(255,255,255,0.10)' }} }}, y: {{ title: {{ display:true, text:'Incerteza', color:'#dbe8f8' }}, ticks: {{ color: '#dbe8f8' }}, grid: {{ color: 'rgba(255,255,255,0.10)' }} }} }} }}
      }});
    }}

    function renderTable(results) {{
      const rows = results.slice(0, 35);
      $('resultTable').innerHTML = `<thead><tr><th>#</th><th>Jogador</th><th>Posição</th><th>Clube</th><th>Liga</th><th>Minutos</th><th>Índice</th><th>Incerteza</th><th>Prob.</th><th>Categoria</th></tr></thead><tbody>${{rows.map((p,i) => `<tr><td>${{i+1}}</td><td><strong>${{p.jogador}}</strong></td><td><span class="tag ${{p.posicao_principal}}">${{p.posicao_principal}}</span></td><td>${{p.clube}}</td><td>${{p.liga}}</td><td>${{Math.round(p.minutos || 0).toLocaleString('pt-BR')}}</td><td>${{fmt(p.indice_ajustado,1)}}</td><td>${{fmt(p.incerteza_modelo,1)}}</td><td><strong>${{fmt(p.prob_pct,1)}}%</strong></td><td>${{p.categoria_prob}}</td></tr>`).join('')}}</tbody>`;
    }}

    function downloadCSV() {{
      if (!latestResults.length) return;
      const header = ['rank','jogador','nacao_codigo','posicao','clube','liga','minutos','indice_ajustado','incerteza_modelo','probabilidade_pct','categoria'];
      const lines = [header.join(',')];
      latestResults.forEach((p,i) => lines.push([i+1, p.jogador, p.nacao_codigo, p.posicao_principal, p.clube, p.liga, p.minutos, fmt(p.indice_ajustado,3), fmt(p.incerteza_modelo,3), fmt(p.prob_pct,3), p.categoria_prob].map(v => `"${{String(v).replaceAll('"','""')}}"`).join(',')));
      const blob = new Blob([lines.join('\\\\n')], {{type: 'text/csv;charset=utf-8;'}});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'resultado_monte_carlo_diogo_rego.csv'; a.click();
      URL.revokeObjectURL(url);
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      setupCountries();
      $('runBtn').addEventListener('click', simulate);
      $('downloadBtn').addEventListener('click', downloadCSV);
      $('uncertainty').addEventListener('input', () => $('uncertaintyOut').textContent = Number($('uncertainty').value).toFixed(1));
      simulate();
    }});
  </script>
</body>
</html>
"""
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"HTML gerado: {OUT_PATH}")
    print(f"Jogadores incorporados: {len(records)}")


if __name__ == "__main__":
    main()
