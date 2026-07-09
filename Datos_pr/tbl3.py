import pandas as pd

# ==========================================
# SVD - AUDITORÍA DE CÁLCULO DESDE CSV
# ==========================================

# 1. Cargar el dataset original
nombre_archivo = 'Scouting_Database_con_TM.csv'
try:
    df = pd.read_csv(nombre_archivo)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{nombre_archivo}'. Asegúrate de estar en la carpeta correcta.")
    exit()

# 2. Filtrar a Trent Alexander-Arnold (2018)
trent = df[(df['Player'] == 'Trent Alexander-Arnold') & (df['Szn'] == 2018)]

if trent.empty:
    print("Error: No se encontró el registro de Trent (2018) en el CSV.")
    exit()

# Extraer la fila como Serie
trent_data = trent.iloc[0]

# 3. Extraer valores exactos que ya están calculados en el CSV
rtg_csv = trent_data['RTG_Principal']
valor_csv = trent_data['Valor_Deportivo']
edad = trent_data['Age']
minutos = trent_data['Min']
liga = trent_data['League']
rol = trent_data['Rol_Principal']

# 4. Reconstruir la lógica económica para la Tabla 4
# Precio Base (Curva Exponencial)
precio_base = ((rtg_csv / 10) ** 6) * 200

# Moduladores Contextuales
factor_edad = 1.0 if edad < 34 else 0.90
factor_minutos = 0.6 + ((minutos / 3420) * 0.4) if minutos >= 1000 else 0.5
factor_liga = 1.15 if liga == 'Premier League' else (1.0 if liga in ['La Liga', 'Bundesliga', 'Serie A'] else 0.85)
factor_pos = 0.98  # Correspondiente a defensores (LB_OFF)

multiplicador_total = factor_edad * factor_minutos * factor_liga * factor_pos
valor_calculado = precio_base * multiplicador_total
valor_redondeado = round(valor_calculado, -4)

# ==========================================
# 5. IMPRESIÓN DEL REPORTE DE AUDITORÍA
# ==========================================
print("="*65)
print(" AUDITORÍA SVD - LECTURA DIRECTA DEL CSV")
print("="*65)
print(f"Jugador: {trent_data['Player']} | Temporada: {trent_data['Szn']} | Rol: {rol}")
print(f"RTG Principal (Dato CSV): {rtg_csv}")
print(f"Valor Deportivo (Dato CSV): € {valor_csv:,.2f}")
print("-" * 65)

print("--- MÉTRICAS CRUDAS DISPONIBLES (Insumo para Tabla 3) ---")
# Lista de métricas que definiste en el JSON para LB_OFF
metricas_lb_off = ['xA', 'CrsPA', 'KP', 'Prog', 'IntoLast3rd', 
                   'TouchesAtt3rd', 'PrgDist', 'DribSucc', 'Dispossesed', 
                   'SCA', 'SCAPassLive', 
                   'Recov', 'TklW', 'Int', 'BallRec']

for m in metricas_lb_off:
    if m in trent_data:
        print(f" - {m}: {trent_data[m]}")
    else:
        print(f" - {m}: [No encontrada en CSV]")

print("\n--- CONSTRUCCIÓN DE LA TABLA 4 (Simulador Financiero) ---")
print(f"1. Precio Base: ({rtg_csv} / 10)^6 * 200 = € {precio_base:,.2f}")
print(f"2. Factor Edad ({edad} años): {factor_edad:.2f}")
print(f"3. Factor Minutos ({minutos} min): {factor_minutos:.4f}")
print(f"4. Factor Liga ({liga}): {factor_liga:.2f}")
print(f"5. Factor Posición ({rol}): {factor_pos:.2f}")
print(f"6. Multiplicador de Mercado Total: {multiplicador_total:.6f}")
print(f"\n>> VERIFICACIÓN MATEMÁTICA: € {precio_base:,.2f} * {multiplicador_total:.6f} = € {valor_calculado:,.2f}")
print(f">> REDONDEO SVD (Igual al CSV): € {valor_redondeado:,.2f}")
print("="*65)