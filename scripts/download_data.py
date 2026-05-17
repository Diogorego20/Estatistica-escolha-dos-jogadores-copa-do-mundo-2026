from pathlib import Path
import shutil
import kagglehub

PROJECT = Path('/home/ubuntu/Estatistica-escolha-dos-jogadores-copa-do-mundo-2026')
RAW = PROJECT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)

path = Path(kagglehub.dataset_download('hubertsidorowicz/football-players-stats-2025-2026'))
print(f'Dataset baixado em: {path}')

for csv_file in path.glob('*.csv'):
    target = RAW / csv_file.name
    shutil.copy2(csv_file, target)
    print(f'Copiado: {target}')
