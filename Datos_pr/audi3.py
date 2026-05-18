import pandas as pd
import numpy as np
import warnings
import os

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

archivo = 'DataFramev1.xlsx'
print("🔍 Iniciando Auditoría de Mediocentros (Radiografía de Bonos y Techos)...\n")

# Configuración básica de MC para la auditoría
PESOS_JSON = {
    "MC_DEF": {
        "categoria_pesos": { "Defensa": 0.55, "Passing": 0.25, "Possession": 0.12, "Aerial": 0.05, "GAS": 0.02, "Shooting": 0.01 },
        "estadisticas": {
            "Defensa": { "Int": 0.25, "Recov": 0.25, "TklW": 0.15, "BallRec": 0.10, "BallRecProg": 0.10, "TklMid3rd": 0.10, "Tkl": 0.05 },
            "Passing": { "Cmp%Total": 0.35, "ShortCmp": 0.15, "Cmp%Short": 0.15, "MediumCmp": 0.10, "Prog": 0.10, "PrgDist": 0.10, "LongCmp": 0.05 },
            "Possession": { "Dispossesed": 0.40, "TouchesMid3rd": 0.30, "TouchesDef3rd": 0.20, "BallRec": 0.10 },
            "Aerial": { "AerialWon%": 1.00 },
            "GAS": { "SCA": 0.50, "SCAPassLive": 0.50 },
            "Shooting": { "Gls": 1.0 }
        }
    },
    "MC_ORG": {
        "categoria_pesos": { "Passing": 0.45, "Possession": 0.25, "Defensa": 0.16, "GAS": 0.12, "Aerial": 0.01, "Shooting": 0.01 },
        "estadisticas": {
            "Passing": { "Prog": 0.20, "PrgDist": 0.20, "IntoLast3rd": 0.15, "Cmp%Total": 0.15, "KP": 0.10, "LongCmp": 0.10, "xA": 0.05, "xAG": 0.05 },
            "Possession": { "PrgDist": 0.30, "TouchesMid3rd": 0.20, "TouchesLive": 0.15, "Dispossesed": 0.12, "DribSucc": 0.13, "TouchesDef3rd": 0.10 },
            "Defensa": { "Recov": 0.35, "Int": 0.30, "BallRec": 0.20, "TklMid3rd": 0.15 },
            "GAS": { "SCA": 0.60, "SCAPassLive": 0.40 },
            "Aerial": { "AerialWon%": 1.0 },
            "Shooting": { "Gls": 0.50, "npxG/Sh": 0.50 }
        }
    }
}

def obtener_pesos_planos(rol):
    config = PESOS_JSON[rol]
    pesos_planos = {}
    for cat, peso_cat in config['categoria_pesos'].items():
        if cat in config['estadisticas']:
            for stat, peso_stat in config['estadisticas'][cat].items():
                pesos_planos[stat] = pesos_planos.get(stat, 0) + (peso_cat * peso_stat)
    return pesos_planos

metricas_defensivas = ['TklW', 'Int', 'Recov', 'Clr', 'Tkl', 'TklDef3rd', 'TklMid3rd', 'TklAtt3rd', 'BallRec', 'BallRecProg']
stats_inversas = ['Dispossesed', 'AerialLost']

# Vamos a rastrear a la élite de tu lista
jugadores_test = ['Joshua Kimmich', 'Thiago Alcántara', 'Marcelo Brozović', 'Sergio Busquets', 'Jorginho', 'Wendell', 'Toni Kroos']

if os.path.exists(archivo):
    xls = pd.ExcelFile(archivo, engine='openpyxl')
    
    print(f"{'JUGADOR (TEMP)':<25} | {'ROL':<7} | {'DEF%':<6} | {'PAS%':<6} | {'GAS%':<6} | {'BONO?':<6} | {'NOTA BASE':<10} | {'FINAL'}")
    print("-" * 95)

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df_clean = df[df['Min'] >= 800].copy()
        df_pos = df_clean[df_clean['Pos'].str.contains('MF', na=False)].copy()
        
        if df_pos.empty: continue
        
        for rol in ['MC_DEF', 'MC_ORG']:
            pesos = obtener_pesos_planos(rol)
            df_calc = df_pos.copy()
            df_calc['Rating_Base'] = 0.0
            df_calc['Puntaje_Def'] = 0.0
            df_calc['Puntaje_Pas'] = 0.0
            df_calc['Puntaje_Gas'] = 0.0
            
            for col, peso in pesos.items():
                if col in df_calc.columns:
                    col_vals = pd.to_numeric(df_calc[col], errors='coerce').fillna(0)
                    _min = col_vals.min()
                    _max_real = col_vals.quantile(0.85) if col in metricas_defensivas else col_vals.quantile(0.95)
                    if _max_real <= _min: _max_real = col_vals.max()
                    
                    if _max_real - _min == 0: norm = 0
                    else:
                        if col in stats_inversas:
                            norm = (_max_real - np.clip(col_vals, _min, _max_real)) / (_max_real - _min)
                        else:
                            norm = (np.clip(col_vals, _min, _max_real) - _min) / (_max_real - _min)
                            
                    puntos = norm * peso
                    df_calc['Rating_Base'] += puntos
                    
                    if col in PESOS_JSON[rol]['estadisticas'].get('Defensa', {}):
                        df_calc['Puntaje_Def'] += puntos / PESOS_JSON[rol]['categoria_pesos']['Defensa']
                    if col in PESOS_JSON[rol]['estadisticas'].get('Passing', {}):
                        df_calc['Puntaje_Pas'] += puntos / PESOS_JSON[rol]['categoria_pesos']['Passing']
                    if col in PESOS_JSON[rol]['estadisticas'].get('GAS', {}):
                        df_calc['Puntaje_Gas'] += puntos / PESOS_JSON[rol]['categoria_pesos'].get('GAS', 1)

            df_calc['Rating_Base'] *= 100
            condicion_todoterreno = (df_calc['Puntaje_Def'] >= 0.60) & ((df_calc['Puntaje_Pas'] >= 0.60) | (df_calc['Puntaje_Gas'] >= 0.60))
            df_calc['Rating_Final'] = np.where(condicion_todoterreno, df_calc['Rating_Base'] * 1.075, df_calc['Rating_Base'])
            df_calc['Rating_Final'] = np.clip(df_calc['Rating_Final'], 0, 100)
            
            filtro = df_calc['Player'].apply(lambda x: any(j in str(x) for j in jugadores_test))
            resultados = df_calc[filtro]
            
            for idx, row in resultados.iterrows():
                # Filtramos para mostrar solo los casos donde rinden muy alto
                if row['Rating_Final'] >= 94.0:
                    jug_temp = f"{row['Player']} ({sheet_name})"
                    bono = "SÍ" if condicion_todoterreno.loc[idx] else "NO"
                    print(f"{jug_temp:<25} | {rol:<7} | {row['Puntaje_Def']:.2f} | {row['Puntaje_Pas']:.2f} | {row['Puntaje_Gas']:.2f} | {bono:<6} | {row['Rating_Base']:<10.2f} | {row['Rating_Final']:.2f}")