from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd

PROJECT = Path('/home/ubuntu/Estatistica-escolha-dos-jogadores-copa-do-mundo-2026')
RAW_FILE = PROJECT / 'data' / 'raw' / 'players_data_light-2025_2026.csv'
PROCESSED_DIR = PROJECT / 'data' / 'processed'
DOCS_DIR = PROJECT / 'docs'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_METADATA = {
    'dataset_title': 'Football Players Stats (2025-2026)',
    'dataset_url': 'https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2025-2026',
    'creator': 'Hubert Sidorowicz',
    'platform': 'Kaggle',
    'original_source': 'FBref',
    'season': '2025-2026',
    'version': 34,
    'license': 'MIT',
    'author_of_project': 'Diogo Rego - Estudante de Estatística UFPB',
}

NUMERIC_COLUMNS = [
    'Age', 'MP', 'Starts', 'Min', '90s', 'Gls', 'Ast', 'G+A', 'G-PK', 'PK', 'PKatt',
    'CrdY', 'CrdR', 'G+A-PK', 'Sh', 'SoT', 'SoT%', 'Sh/90', 'SoT/90', 'G/Sh',
    'G/SoT', 'Crs', 'TklW', 'Int', 'Fld', 'Fls', 'OG', 'GA', 'GA90', 'SoTA',
    'Saves', 'Save%', 'W', 'D', 'L', 'CS', 'CS%', 'PKA', 'PKsv', 'PKm'
]


def normalize_nation(value: object) -> str:
    if pd.isna(value):
        return 'Não informado'
    parts = str(value).split()
    return parts[-1] if parts else str(value)


def primary_position(pos: object) -> str:
    if pd.isna(pos):
        return 'OUT'
    text = str(pos).upper()
    if 'GK' in text:
        return 'GK'
    if 'DF' in text:
        return 'DF'
    if 'MF' in text:
        return 'MF'
    if 'FW' in text:
        return 'FW'
    return 'OUT'


def per90(series: pd.Series, ninety: pd.Series) -> pd.Series:
    safe_90 = ninety.replace(0, np.nan)
    return (series / safe_90).replace([np.inf, -np.inf], np.nan).fillna(0)


def minmax_by_position(df: pd.DataFrame, column: str) -> pd.Series:
    grouped = df.groupby('posicao_principal')[column]
    min_v = grouped.transform('min')
    max_v = grouped.transform('max')
    spread = (max_v - min_v).replace(0, np.nan)
    return ((df[column] - min_v) / spread).fillna(0)


def build_dataset() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILE)

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df['jogador'] = df['Player'].astype(str).str.strip()
    df['nacao_codigo'] = df['Nation'].apply(normalize_nation)
    df['posicao_original'] = df['Pos'].fillna('Não informado').astype(str)
    df['posicao_principal'] = df['Pos'].apply(primary_position)
    df['clube'] = df['Squad'].fillna('Não informado').astype(str)
    df['liga'] = df['Comp'].fillna('Não informado').astype(str)
    df['idade'] = df['Age'].fillna(df['Age'].median()).round(1)
    df['minutos'] = df['Min'].fillna(0)
    df['jogos'] = df['MP'].fillna(0)
    df['noventas'] = df['90s'].fillna(0).clip(lower=0)

    raw_components = {
        'gols_p90': 'Gls',
        'assistencias_p90': 'Ast',
        'participacoes_gol_p90': 'G+A',
        'finalizacoes_p90': 'Sh',
        'finalizacoes_gol_p90': 'SoT',
        'cruzamentos_p90': 'Crs',
        'desarmes_vencidos_p90': 'TklW',
        'interceptacoes_p90': 'Int',
        'faltas_sofridas_p90': 'Fld',
    }

    for new_col, old_col in raw_components.items():
        df[new_col] = per90(df[old_col].fillna(0), df['noventas'])

    df['disciplina_p90'] = per90(df['CrdY'].fillna(0) + 2 * df['CrdR'].fillna(0), df['noventas'])
    df['eficiencia_chute'] = df['G/Sh'].fillna(0).clip(lower=0, upper=1)
    df['taxa_chutes_gol'] = (df['SoT%'].fillna(0) / 100).clip(lower=0, upper=1)
    df['save_pct'] = (df['Save%'].fillna(0) / 100).clip(lower=0, upper=1)
    df['clean_sheet_pct'] = (df['CS%'].fillna(0) / 100).clip(lower=0, upper=1)
    df['gols_sofridos_inv'] = -df['GA90'].fillna(df['GA90'].median()).fillna(0)

    for col in [
        'gols_p90', 'assistencias_p90', 'participacoes_gol_p90', 'finalizacoes_p90',
        'finalizacoes_gol_p90', 'cruzamentos_p90', 'desarmes_vencidos_p90',
        'interceptacoes_p90', 'faltas_sofridas_p90', 'eficiencia_chute', 'taxa_chutes_gol',
        'save_pct', 'clean_sheet_pct', 'gols_sofridos_inv'
    ]:
        df[f'{col}_norm'] = minmax_by_position(df, col)

    df['volume_jogo_norm'] = np.log1p(df['minutos']) / np.log1p(max(df['minutos'].max(), 1))
    df['experiencia_norm'] = np.log1p(df['jogos']) / np.log1p(max(df['jogos'].max(), 1))
    df['idade_prime_norm'] = np.exp(-((df['idade'] - 27) ** 2) / (2 * 4.5 ** 2))

    attack_score = (
        0.30 * df['participacoes_gol_p90_norm'] +
        0.18 * df['gols_p90_norm'] +
        0.16 * df['assistencias_p90_norm'] +
        0.12 * df['finalizacoes_gol_p90_norm'] +
        0.10 * df['eficiencia_chute_norm'] +
        0.08 * df['cruzamentos_p90_norm'] +
        0.06 * df['volume_jogo_norm']
    )
    midfield_score = (
        0.22 * df['assistencias_p90_norm'] +
        0.18 * df['cruzamentos_p90_norm'] +
        0.16 * df['faltas_sofridas_p90_norm'] +
        0.14 * df['participacoes_gol_p90_norm'] +
        0.12 * df['desarmes_vencidos_p90_norm'] +
        0.10 * df['interceptacoes_p90_norm'] +
        0.08 * df['volume_jogo_norm']
    )
    defense_score = (
        0.30 * df['desarmes_vencidos_p90_norm'] +
        0.26 * df['interceptacoes_p90_norm'] +
        0.12 * df['cruzamentos_p90_norm'] +
        0.10 * df['volume_jogo_norm'] +
        0.10 * df['experiencia_norm'] +
        0.07 * df['idade_prime_norm'] +
        0.05 * (1 - df['disciplina_p90'].clip(0, 1))
    )
    goalkeeper_score = (
        0.42 * df['save_pct_norm'] +
        0.24 * df['clean_sheet_pct_norm'] +
        0.16 * df['gols_sofridos_inv_norm'] +
        0.10 * df['volume_jogo_norm'] +
        0.08 * df['experiencia_norm']
    )

    df['score_ataque'] = attack_score
    df['score_meio'] = midfield_score
    df['score_defesa'] = defense_score
    df['score_goleiro'] = goalkeeper_score

    df['indice_desempenho_base'] = np.select(
        [df['posicao_principal'].eq('GK'), df['posicao_principal'].eq('DF'), df['posicao_principal'].eq('MF'), df['posicao_principal'].eq('FW')],
        [df['score_goleiro'], df['score_defesa'], df['score_meio'], df['score_ataque']],
        default=(attack_score + midfield_score + defense_score) / 3,
    )

    df['penalidade_baixa_amostra'] = np.where(df['minutos'] >= 900, 1, np.sqrt(df['minutos'].clip(lower=1) / 900))
    df['indice_desempenho'] = (100 * df['indice_desempenho_base'] * df['penalidade_baixa_amostra']).clip(0, 100)
    df['incerteza_modelo'] = (18 / np.sqrt(df['noventas'].clip(lower=1)) + 4 * (1 - df['volume_jogo_norm'])).clip(3, 28)

    selected_columns = [
        'jogador', 'nacao_codigo', 'posicao_original', 'posicao_principal', 'clube', 'liga',
        'idade', 'jogos', 'minutos', 'noventas', 'Gls', 'Ast', 'G+A', 'Sh', 'SoT', 'SoT%',
        'Crs', 'TklW', 'Int', 'GA90', 'Saves', 'Save%', 'CS%', 'gols_p90', 'assistencias_p90',
        'participacoes_gol_p90', 'finalizacoes_p90', 'finalizacoes_gol_p90', 'cruzamentos_p90',
        'desarmes_vencidos_p90', 'interceptacoes_p90', 'save_pct', 'clean_sheet_pct',
        'score_ataque', 'score_meio', 'score_defesa', 'score_goleiro', 'indice_desempenho',
        'incerteza_modelo', 'penalidade_baixa_amostra'
    ]

    out = df[selected_columns].copy()
    out = out.sort_values(['indice_desempenho', 'minutos'], ascending=[False, False])
    return out


def main() -> None:
    data = build_dataset()
    output_csv = PROCESSED_DIR / 'players_world_cup_monte_carlo_ready.csv'
    data.to_csv(output_csv, index=False)

    summary = {
        **SOURCE_METADATA,
        'rows': int(len(data)),
        'countries': int(data['nacao_codigo'].nunique()),
        'clubs': int(data['clube'].nunique()),
        'leagues': int(data['liga'].nunique()),
        'processed_file': str(output_csv.relative_to(PROJECT)),
    }

    with open(PROCESSED_DIR / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    top = data.head(30)[['jogador', 'nacao_codigo', 'posicao_principal', 'clube', 'liga', 'minutos', 'indice_desempenho']]
    top.to_csv(PROCESSED_DIR / 'top30_indice_desempenho.csv', index=False)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
