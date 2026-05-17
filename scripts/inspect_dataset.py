from pathlib import Path
import pandas as pd

project = Path('/home/ubuntu/Estatistica-escolha-dos-jogadores-copa-do-mundo-2026')
raw = project / 'data' / 'raw'
out = project / 'docs'
out.mkdir(exist_ok=True)

for fname in ['players_data_light-2025_2026.csv', 'players_data-2025_2026.csv']:
    path = raw / fname
    df = pd.read_csv(path)
    print('\n===', fname, '===')
    print('shape:', df.shape)
    print('columns:', list(df.columns)[:80])
    print(df.head(3).to_string())
