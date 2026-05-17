from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT = Path('/home/ubuntu/Estatistica-escolha-dos-jogadores-copa-do-mundo-2026')
DATA = PROJECT / 'data' / 'processed' / 'players_world_cup_monte_carlo_ready.csv'
IMG = PROJECT / 'img'
IMG.mkdir(exist_ok=True)

sns.set_theme(style='whitegrid', context='talk')
plt.rcParams['font.family'] = 'DejaVu Sans'

players = pd.read_csv(DATA)
plot_data = (
    players[players['posicao_principal'].isin(['GK', 'DF', 'MF', 'FW'])]
    .sort_values('indice_desempenho', ascending=False)
    .groupby('posicao_principal', group_keys=False)
    .head(5)
    .copy()
)
plot_data = plot_data.sort_values(['posicao_principal', 'indice_desempenho'], ascending=[True, True])

palette = {'GK': '#1B998B', 'DF': '#2D3047', 'MF': '#F4B942', 'FW': '#E84855'}
fig, ax = plt.subplots(figsize=(14, 10))
colors = plot_data['posicao_principal'].map(palette)
ax.barh(plot_data['jogador'], plot_data['indice_desempenho'], color=colors, alpha=0.92)
ax.set_title('Ranking Estatístico Balanceado por Posição', fontsize=22, weight='bold', color='#0B1F3A', pad=18)
ax.set_xlabel('Índice de desempenho autoral (0–100)', fontsize=14)
ax.set_ylabel('')
ax.set_xlim(0, max(100, plot_data['indice_desempenho'].max() * 1.08))
for i, (_, row) in enumerate(plot_data.iterrows()):
    ax.text(row['indice_desempenho'] + 0.8, i, f"{row['indice_desempenho']:.1f} | {row['posicao_principal']} | {row['nacao_codigo']}", va='center', fontsize=10, color='#243447')

ax.text(0, -1.8, 'Autoria: Diogo Rego - Estudante de Estatística UFPB | Fonte: Kaggle / FBref, Football Players Stats (2025-2026)', fontsize=11, color='#475569')
sns.despine(left=True, bottom=True)
plt.tight_layout()
fig.savefig(IMG / 'dashboard_preview.png', dpi=180, bbox_inches='tight')
plt.close(fig)

summary = players.groupby('posicao_principal', observed=True)['indice_desempenho'].agg(['count', 'mean', 'median']).reset_index()
summary.to_csv(IMG / 'summary_by_position.csv', index=False)
print('Imagem gerada:', IMG / 'dashboard_preview.png')
