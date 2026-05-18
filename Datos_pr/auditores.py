import pandas as pd
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

archivo = 'DataFramev1.xlsx'
print("Cargando datos de Centrales con el nuevo arsenal...")
df = pd.read_excel(archivo, sheet_name='21-22') 
df_clean = df[(df['Min'] >= 800) & (df['Pos'].str.contains('CB|DF', na=False))].copy()

jugadores_test = [
    'Virgil van Dijk', 'Rúben Dias', 'Marquinhos', 
    'Grant Hanley', 'James Tarkowski', 'Mohammed Salisu'
]

# Definimos nuestras tres dimensiones basadas en TU lista
stats_volumen = ['Clr', 'Int', 'Tkl']
stats_eficacia = ['AerialWon%', 'Recov', 'BallRecProg'] 
stats_salida = ['Cmp%Total', 'Prog', 'PrgDist']
stats_inversas = ['Dispossesed'] # Menos es mejor

stats_auditoria = stats_volumen + stats_eficacia + stats_salida + stats_inversas

print("\n=== 🚨 ANÁLISIS DEL TECHO EN CENTRALES (P95/P85) 🚨 ===")
techos = {}
for stat in stats_auditoria:
    if stat in df_clean.columns:
        df_clean[stat] = pd.to_numeric(df_clean[stat], errors='coerce').fillna(0)
        _min = df_clean[stat].min()
        # Usamos P85 para volumen defensivo (para no matar a la élite) y P95 para calidad
        percentil = 0.85 if stat in stats_volumen else 0.95
        _max_real = df_clean[stat].quantile(percentil)
        techos[stat] = {'min': _min, 'max': _max_real}
        print(f"  {stat:15} -> Techo: {_max_real:.2f}")

print("\n=== 🔬 NOTAS NORMALIZADAS: ÉLITE VS VOLUMEN 🔬 ===")
filtro = df_clean['Player'].apply(lambda x: any(j in str(x) for j in jugadores_test))
df_test = df_clean[filtro]

for index, row in df_test.iterrows():
    print(f"\n🧱 {row['Player']} ({row['Squad']})")
    
    # 1. VOLUMEN
    print("  --- VOLUMEN (Dominan equipos de bloque bajo) ---")
    for stat in stats_volumen:
        if stat in row and stat in techos:
            valor = row[stat]
            _max = techos[stat]['max']
            _min = techos[stat]['min']
            norm = (np.clip(valor, _min, _max) - _min) / (_max - _min) * 100 if _max > _min else 0
            print(f"    {stat:15} | Crudo: {valor:6.2f} | Nota: {norm:5.1f}/100")
            
    # 2. EFICACIA
    print("  --- EFICACIA AÉREA Y RECUPERACIÓN (Dominio Élite) ---")
    for stat in stats_eficacia:
        if stat in row and stat in techos:
            valor = row[stat]
            _max = techos[stat]['max']
            _min = techos[stat]['min']
            norm = (np.clip(valor, _min, _max) - _min) / (_max - _min) * 100 if _max > _min else 0
            print(f"    {stat:15} | Crudo: {valor:6.2f} | Nota: {norm:5.1f}/100")

    # 3. SALIDA DE BALÓN
    print("  --- SALIDA DE BALÓN (Dominio Élite) ---")
    for stat in stats_salida:
        if stat in row and stat in techos:
            valor = row[stat]
            _max = techos[stat]['max']
            _min = techos[stat]['min']
            norm = (np.clip(valor, _min, _max) - _min) / (_max - _min) * 100 if _max > _min else 0
            print(f"    {stat:15} | Crudo: {valor:6.2f} | Nota: {norm:5.1f}/100")
            
    # 4. ERRORES (Métrica inversa)
    print("  --- SEGURIDAD (Menos pérdidas es mejor) ---")
    for stat in stats_inversas:
        if stat in row and stat in techos:
            valor = row[stat]
            _max = techos[stat]['max']
            _min = techos[stat]['min']
            # INVERSO: 0 pérdidas = 100 puntos
            norm = (_max - np.clip(valor, _min, _max)) / (_max - _min) * 100 if _max > _min else 0
            print(f"    {stat:15} | Crudo: {valor:6.2f} | Nota: {norm:5.1f}/100")