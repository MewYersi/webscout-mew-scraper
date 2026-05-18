import pandas as pd
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

archivo = 'DataFramev1.xlsx'
print("🔍 Iniciando Auditoría de Laterales (OFF vs DEF)...\n")

df = pd.read_excel(archivo, sheet_name='21-22')
# Filtramos a los laterales (aquellos que pasaron nuestra aduana táctica de centros/toques)
UMBRAL_CENTROS = 15.0
UMBRAL_TOQUES_ATT = 12.0
df_clean = df[(df['Min'] >= 800) & (df['Pos'].str.contains('DF', na=False))].copy()
df_laterales = df_clean[(df_clean['Crs'] >= UMBRAL_CENTROS) | (df_clean['TouchesAtt3rd'] >= UMBRAL_TOQUES_ATT)].copy()

jugadores_test = [
    'Trent Alexander-Arnold', 'João Cancelo',  # Los ofensivos top
    'César Azpilicueta', 'Ferland Mendy', 'Kyle Walker' # Los más defensivos/equilibrados
]

filtro = df_laterales['Player'].apply(lambda x: any(j in str(x) for j in jugadores_test))
df_test = df_laterales[filtro]

# Métricas clave donde sospecho que el LB_DEF se queda corto
stats_defensa = ['TklW', 'Int', 'Recov', 'TklDef3rd']
stats_ataque = ['xA', 'Prog', 'PrgDist', 'CrsPA']

print("\n=== 🚨 ANÁLISIS DE TECHOS (P95) PARA LATERALES 🚨 ===")
techos = {}
for stat in stats_defensa + stats_ataque:
    if stat in df_laterales.columns:
        df_laterales[stat] = pd.to_numeric(df_laterales[stat], errors='coerce').fillna(0)
        _min = df_laterales[stat].min()
        _max_real = df_laterales[stat].quantile(0.95)
        techos[stat] = {'min': _min, 'max': _max_real}
        print(f"  {stat:15} -> P95: {_max_real:.2f}")

print("\n=== 🔬 RENDIMIENTO CRUDO VS TECHOS 🔬 ===")
for index, row in df_test.iterrows():
    print(f"\n🏃‍♂️ {row['Player']} ({row['Squad']})")
    
    print("  --- DEFENSA (Deberían dominar los LB_DEF) ---")
    for stat in stats_defensa:
        if stat in row and stat in techos:
            valor = row[stat]
            _max = techos[stat]['max']
            _min = techos[stat]['min']
            norm = (np.clip(valor, _min, _max) - _min) / (_max - _min) * 100 if _max > _min else 0
            print(f"    {stat:15} | Crudo: {valor:6.2f} | Nota IA: {norm:5.1f}/100")
            
    print("  --- ATAQUE (Dominan los LB_OFF) ---")
    for stat in stats_ataque:
        if stat in row and stat in techos:
            valor = row[stat]
            _max = techos[stat]['max']
            _min = techos[stat]['min']
            norm = (np.clip(valor, _min, _max) - _min) / (_max - _min) * 100 if _max > _min else 0
            print(f"    {stat:15} | Crudo: {valor:6.2f} | Nota IA: {norm:5.1f}/100")