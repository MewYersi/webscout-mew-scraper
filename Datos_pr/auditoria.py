import pandas as pd
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# 1. Cargar el archivo original de donde salen los datos
archivo = 'DataFramev1.xlsx'
print("Cargando datos...")

# Leemos directamente la temporada 21-22 (o cambia el nombre a la pestaña que estés usando)
df = pd.read_excel(archivo, sheet_name='21-22') 
df_clean = df[df['Min'] >= 800].copy()

# 2. Nuestros conejillos de indias
jugadores_test = [
    'Casemiro', 'Fabinho', 'N\'Golo Kanté', 
    'Joshua Kimmich', 'John McGinn', 'Marcelo Brozović', 'Fabián Ruiz', 
    'Theo Hernández', 'João Cancelo', 'Trent Alexander-Arnold'
]

# 3. Las métricas que queremos investigar
stats_auditoria = ['TklW', 'Int', 'Recov', 'Clr', 'Prog', 'PrgDist', 'SCA', 'TouchesMid3rd']

print("\n=== 🚨 EL TECHO DEL MODELO (Percentil 95 GLOBAL) 🚨 ===")
print("Si el P95 es muy alto, nuestros élites sacarán malas notas.")
techos = {}
for stat in stats_auditoria:
    if stat in df_clean.columns:
        _min = df_clean[stat].min()
        _max_real = df_clean[stat].quantile(0.95)
        techos[stat] = {'min': _min, 'max': _max_real}
        print(f"  {stat:15} -> P95: {_max_real:.2f} (Quien llegue a esto saca 100/100)")

print("\n=== 🔬 NOTAS NORMALIZADAS DE NUESTROS CRACKS 🔬 ===")
# Filtramos de forma flexible por si los nombres varían un poco en el Excel
filtro = df_clean['Player'].apply(lambda x: any(j in str(x) for j in jugadores_test))
df_test = df_clean[filtro]

for index, row in df_test.iterrows():
    print(f"\n⚽ {row['Player']} ({row['Squad']}) - Pos: {row['Pos']}")
    for stat in stats_auditoria:
        if stat in row and stat in techos:
            valor_crudo = row[stat]
            _min = techos[stat]['min']
            _max_real = techos[stat]['max']
            
            # Replicamos exactamente la normalización de tu motor V14
            if _max_real > _min:
                norm = (np.clip(valor_crudo, _min, _max_real) - _min) / (_max_real - _min) * 100
            else:
                norm = 0
                
            print(f"  - {stat:15} | Crudo: {valor_crudo:5.2f} | Nota IA: {norm:5.1f} / 100")