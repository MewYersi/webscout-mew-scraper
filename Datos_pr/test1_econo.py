import pandas as pd
import numpy as np
import os
import sys
import warnings

# --- CONFIGURACIÓN ---
sys.stdout.reconfigure(encoding='utf-8')
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning) 

# ==========================================
# 1. TUS PESOS (JSON COMPLETO)
# ==========================================
PESOS_JSON = {
    "DC": {
        "categoria_pesos": { "Defensa": 0.55, "Aerial": 0.25, "Passing": 0.15, "Possession": 0.05, "GAS": 0.00, "Shooting": 0.00 },
        "estadisticas": {
            "Defensa": { "Clr": 0.30, "Int": 0.25, "Recov": 0.20, "TklW": 0.15, "TklDef3rd": 0.10 },
            "Aerial": { "AerialWon%": 0.60, "AerialWon": 0.40 },
            "Passing": { "Cmp%Total": 0.40, "PrgDist": 0.30, "LongCmp": 0.30 },
            "Possession": { "Dispossessed": 1.0 }
        }
    },
    "LB_DEF": {
        "categoria_pesos": { "Defensa": 0.45, "Aerial": 0.10, "Passing": 0.25, "Possession": 0.10, "GAS": 0.07, "Shooting": 0.03 },
        "estadisticas": {
            "Defensa": { "TklW": 0.22, "Int": 0.20, "Recov": 0.15, "BallRecProg": 0.10, "Tkl": 0.10, "Clr": 0.08, "BallRec": 0.05, "TklDef3rd": 0.06, "TklMid3rd": 0.03, "TklAtt3rd": 0.01 },
            "Aerial": { "AerialWon%": 0.55, "AerialWon": 0.30, "AerialLost": 0.15 },
            "Passing": { "Cmp%Total": 0.20, "TotalCmp": 0.08, "MediumCmp": 0.10, "Cmp%Medium": 0.10, "ShortCmp": 0.08, "Cmp%Short": 0.08, "LongCmp": 0.10, "Cmp%Long": 0.10, "PrgDist": 0.10, "Prog": 0.04, "IntoLast3rd": 0.01, "KP": 0.01 },
            "Possession": { "Touches": 0.10, "TouchesDef3rd": 0.15, "TouchesDefPen": 0.10, "TouchesMid3rd": 0.10, "TouchesLive": 0.05, "DribSucc": 0.05, "DribAtt": 0.03, "DribSucc%": 0.10, "Dispossessed": 0.15, "BallRec": 0.035, "BallRecProg": 0.035 },
            "GAS": { "SCA": 0.12, "SCAPassLive": 0.18, "SCAPassDead": 0.05, "SCADef": 0.20, "GCA": 0.15, "GCAPassLive": 0.20, "GCAPassDead": 0.10 },
            "Shooting": { "xG": 0.40, "Gls": 0.40, "SoT%": 0.20 }
        }
    },
    "LB_OFF": {
        "categoria_pesos": { "Defensa": 0.25, "Aerial": 0.05, "Passing": 0.27, "Possession": 0.23, "GAS": 0.17, "Shooting": 0.03 },
        "estadisticas": {
            "Defensa": { "TklW": 0.18, "Int": 0.18, "Recov": 0.16, "BallRecProg": 0.12, "Tkl": 0.12, "Clr": 0.06, "BallRec": 0.06, "TklDef3rd": 0.05, "TklMid3rd": 0.05, "TklAtt3rd": 0.02 },
            "Aerial": { "AerialWon%": 0.50, "AerialWon": 0.30, "AerialLost": 0.20 },
            "Passing": { "Cmp%Total": 0.10, "TotalCmp": 0.05, "PrgDist": 0.15, "Prog": 0.15, "IntoLast3rd": 0.10, "PPA": 0.10, "Crs": 0.10, "CrsPA": 0.10, "KP": 0.10, "MediumCmp": 0.03, "Cmp%Medium": 0.02, "LongCmp": 0.03, "Cmp%Long": 0.02 },
            "Possession": { "Touches": 0.10, "TouchesMid3rd": 0.10, "TouchesAtt3rd": 0.10, "TouchesAttPen": 0.08, "TouchesLive": 0.07, "DribSucc": 0.10, "DribAtt": 0.07, "DribSucc%": 0.10, "Dispossessed": 0.08, "BallRec": 0.05, "BallRecProg": 0.05, "TouchesDef3rd": 0.05, "TouchesDefPen": 0.05 },
            "GAS": { "SCA": 0.17, "SCAPassLive": 0.22, "SCAPassDead": 0.06, "SCADrib": 0.09, "SCASh": 0.04, "SCAFld": 0.07, "SCADef": 0.05, "GCA": 0.10, "GCAPassLive": 0.12, "GCAPassDead": 0.05, "GCADrib": 0.02, "GCASh": 0.01, "GCAFld": 0.03, "GCADef": 0.02 },
            "Shooting": { "Gls": 0.30, "xG": 0.30, "SoT%": 0.40 }
        }
    },
    "MC_DEF": {
        "categoria_pesos": { "Defensa": 0.55, "Passing": 0.25, "Possession": 0.12, "Aerial": 0.05, "GAS": 0.02, "Shooting": 0.01 },
        "estadisticas": {
            "Defensa": { "Int": 0.20, "Recov": 0.20, "TklW": 0.15, "BallRec": 0.10, "BallRecProg": 0.10, "TklMid3rd": 0.10, "Tkl": 0.05, "TklDef3rd": 0.05, "TklAtt3rd": 0.03, "Clr": 0.02 },
            "Passing": { "Cmp%Total": 0.25, "ShortCmp": 0.15, "Cmp%Short": 0.15, "MediumCmp": 0.15, "Cmp%Medium": 0.10, "Prog": 0.10, "PrgDist": 0.05, "LongCmp": 0.05 },
            "Possession": { "Dispossessed": 0.40, "TouchesMid3rd": 0.30, "TouchesDef3rd": 0.20, "BallRec": 0.10 },
            "Aerial": { "AerialWon%": 1.00 },
            "GAS": { "SCA": 0.50, "SCAPassLive": 0.50 },
            "Shooting": { "Gls": 1.0 }
        }
    },
    "MC_EST": {
        "categoria_pesos": { "Passing": 0.38, "Possession": 0.25, "Defensa": 0.22, "GAS": 0.10, "Aerial": 0.03, "Shooting": 0.02 },
        "estadisticas": {
            "Passing": { "Prog": 0.20, "PrgDist": 0.20, "IntoLast3rd": 0.15, "Cmp%Total": 0.10, "TotalCmp": 0.10, "MediumCmp": 0.10, "LongCmp": 0.05, "PPA": 0.05, "KP": 0.05 },
            "Defensa": { "Recov": 0.25, "Int": 0.20, "TklW": 0.15, "BallRecProg": 0.15, "TklMid3rd": 0.15, "BallRec": 0.10 },
            "Possession": { "PrgDist": 0.30, "TouchesMid3rd": 0.25, "DribSucc": 0.15, "Dispossessed": 0.15, "TouchesLive": 0.15 },
            "GAS": { "SCA": 0.40, "SCAPassLive": 0.40, "GCA": 0.20 },
            "Aerial": { "AerialWon%": 1.0 },
            "Shooting": { "npxG": 0.50, "Gls": 0.50 }
        }
    },
    "AM": {
        "categoria_pesos": { "GAS": 0.36, "Passing": 0.30, "Possession": 0.16, "Shooting": 0.12, "Defensa": 0.04, "Aerial": 0.02 },
        "estadisticas": {
            "GAS": { "SCA": 0.15, "SCAPassLive": 0.22, "SCAPassDead": 0.10, "SCADrib": 0.15, "SCASh": 0.08, "SCAFld": 0.10, "SCADef": 0.05, "GCA": 0.10, "GCAPassLive": 0.03, "GCAPassDead": 0.02 },
            "Passing": { "KP": 0.18, "Prog": 0.18, "IntoLast3rd": 0.10, "PPA": 0.15, "PrgDist": 0.10, "Cmp%Medium": 0.07, "MediumCmp": 0.07, "LongCmp": 0.05, "Cmp%Long": 0.05, "TotalCmp": 0.05 },
            "Possession": { "Touches": 0.08, "TouchesMid3rd": 0.10, "TouchesAtt3rd": 0.15, "TouchesAttPen": 0.10, "DribSucc": 0.13, "DribAtt": 0.12, "DribSucc%": 0.15, "Dispossessed": 0.10, "BallRecProg": 0.07 },
            "Shooting": { "xG": 0.30, "npxG": 0.20, "Gls": 0.35, "SoT%": 0.15 },
            "Defensa": { "Tkl": 0.25, "TklW": 0.20, "Int": 0.20, "BallRec": 0.20, "SCADef": 0.15 },
            "Aerial": { "AerialWon%": 0.50, "AerialWon": 0.30, "AerialLost": 0.20 }
        }
    },
    "FW_WG": {
        "categoria_pesos": { "GAS": 0.30, "Possession": 0.25, "Shooting": 0.25, "Passing": 0.15, "Defensa": 0.03, "Aerial": 0.02 },
        "estadisticas": {
            "GAS": { "GCA": 0.30, "SCADrib": 0.30, "SCA": 0.20, "SCAPassLive": 0.20 },
            "Possession": { "DribSucc": 0.30, "TouchesAttPen": 0.30, "PrgDist": 0.25, "DribSucc%": 0.15 },
            "Shooting": { "Gls": 0.55, "npxG": 0.30, "SoT%": 0.15 },
            "Passing": { "CrsPA": 0.30, "xA": 0.25, "Ast": 0.25, "IntoLast3rd": 0.20 },
            "Defensa": { "BallRec": 0.60, "TklW": 0.40 },
            "Aerial": { "AerialWon%": 1.0 }
        }
    },
    "FW_ST": {
        "categoria_pesos": { "Shooting": 0.50, "GAS": 0.20, "Passing": 0.15, "Possession": 0.10, "Aerial": 0.05 },
        "estadisticas": {
            "Shooting": { "Gls": 0.55, "npxG": 0.20, "SoT%": 0.15, "xG": 0.10 },
            "GAS": { "GCA": 0.40, "SCA": 0.20, "SCAPassLive": 0.20, "GCAPassLive": 0.20 },
            "Passing": { "Ast": 0.35, "xA": 0.25, "KP": 0.20, "PPA": 0.20 },
            "Possession": { "TouchesAttPen": 0.70, "DribSucc": 0.20, "TouchesAtt3rd": 0.10 },
            "Aerial": { "AerialWon": 0.50, "AerialWon%": 0.50 },
            "Defensa": { "BallRec": 1.0 }
        }
    },
    "FW_SS": {
        "categoria_pesos": { "GAS": 0.32, "Shooting": 0.28, "Possession": 0.18, "Passing": 0.14, "Defensa": 0.06, "Aerial": 0.02 },
        "estadisticas": {
            "GAS": { "SCA": 0.18, "SCAPassLive": 0.22, "SCAPassDead": 0.06, "SCADrib": 0.16, "SCASh": 0.06, "SCAFld": 0.10, "SCADef": 0.04, "GCA": 0.10, "GCAPassLive": 0.05, "GCAPassDead": 0.03 },
            "Shooting": { "xG": 0.26, "npxG": 0.20, "Gls": 0.38, "SoT%": 0.16 },
            "Possession": { "Touches": 0.10, "TouchesMid3rd": 0.14, "TouchesAtt3rd": 0.22, "TouchesAttPen": 0.10, "DribSucc": 0.15, "DribAtt": 0.10, "DribSucc%": 0.13, "Dispossessed": 0.10, "BallRecProg": 0.06 },
            "Passing": { "KP": 0.24, "Prog": 0.18, "IntoLast3rd": 0.12, "PPA": 0.12, "PrgDist": 0.10, "MediumCmp": 0.10, "Cmp%Medium": 0.06, "LongCmp": 0.05, "Cmp%Long": 0.03 },
            "Defensa": { "Tkl": 0.28, "TklW": 0.24, "Int": 0.20, "BallRec": 0.18, "SCADef": 0.10 },
            "Aerial": { "AerialWon%": 0.50, "AerialWon": 0.30, "AerialLost": 0.20 }
        }
    }
}

# ==========================================
# 2. FUNCIONES DE CÁLCULO
# ==========================================
def obtener_pesos_planos(rol):
    if rol not in PESOS_JSON: return {}
    config = PESOS_JSON[rol]
    pesos_planos = {}
    for cat, peso_cat in config['categoria_pesos'].items():
        if cat in config['estadisticas']:
            for stat, peso_stat in config['estadisticas'][cat].items():
                pesos_planos[stat] = pesos_planos.get(stat, 0) + (peso_cat * peso_stat)
    return pesos_planos

def calcular_precio(row, col_rtg, nombre_rol):
    rtg = row[col_rtg]
    edad = row['Age']
    minutos = row['Min']
    equipo = row['Squad']
    # nacionalidad eliminada
    
    # 1. BASE EXPONENCIAL CÚBICA
    # Elevamos el RTG al cubo para diferenciar cracks de jugadores promedio
    precio_base = (rtg ** 3) * 400 
    
    # 2. FACTOR EDAD (Curva de Valor)
    factor_edad = 1.0
    if edad < 22: factor_edad = 1.45     # Wonderkid
    elif 22 <= edad <= 26: factor_edad = 1.25 # Crecimiento
    elif 27 <= edad <= 29: factor_edad = 1.20 # Prime
    elif 30 <= edad <= 32: factor_edad = 0.80 # Declive
    else: factor_edad = 0.65             # Veterano
    
    # 3. FACTOR MINUTOS (Disponibilidad)a
    pct_minutos = minutos / 3420
    factor_minutos = 0.6 + (pct_minutos * 0.4) 
    if minutos < 1000: factor_minutos = 0.5 
    
    # 4. FACTOR CLUB (Big 6 Tax)
    big_six = ["Manchester City", "Manchester Utd", "Liverpool", "Chelsea", "Arsenal", "Tottenham"]
    factor_club = 1.25 if equipo in big_six else 1.0
    
    # 5. FACTOR POSICIÓN (Lo que paga el mercado)
    # Se paga más por el gol y la creatividad
    prefijo = nombre_rol.split('_')[0]
    if prefijo in ['FW', 'AM']:
        factor_pos = 1.35  # +35% para atacantes (AM, WG, ST, SS)
    elif prefijo == 'MC':
        factor_pos = 1.0   # Neutro para mediocentros
    else: 
        factor_pos = 0.9   # -10% para defensas (salvo excepciones, los defensas son más baratos)

    # CÁLCULO FINAL
    precio_final = precio_base * factor_edad * factor_minutos * factor_club * factor_pos
    
    return round(precio_final, -4)

def calcular_rating_rol(df, rol_analisis):
    pesos = obtener_pesos_planos(rol_analisis)
    cols_necesarias = list(pesos.keys())
    cols_existentes = [c for c in cols_necesarias if c in df.columns]
    df_calc = df.copy()
    
    for col in cols_existentes:
        df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce').fillna(0)
        min_v, max_v = df_calc[col].min(), df_calc[col].max()
        if max_v - min_v == 0:
            df_calc[f"{col}_Norm"] = 0
        else:
            df_calc[f"{col}_Norm"] = (df_calc[col] - min_v) / (max_v - min_v)

    col_rating = f'RTG_{rol_analisis}'
    df_calc[col_rating] = 0
    for col in cols_existentes:
        peso = pesos[col]
        df_calc[col_rating] += df_calc[f"{col}_Norm"] * peso
    
    df_calc[col_rating] = df_calc[col_rating] * 100
    
    # Pasamos el nombre del rol para aplicar el factor posicional
    df_calc['Precio_Estimado'] = df_calc.apply(lambda row: calcular_precio(row, col_rating, rol_analisis), axis=1)

    cols_finales = ['Player', 'Squad', 'Age', 'Pos', 'PosAdj', 'Min', col_rating, 'Precio_Estimado'] + [c for c in df_calc.columns if "Contrib_" in c]
    return df_calc[cols_finales].sort_values('Precio_Estimado', ascending=False)

# ==========================================
# 3. EJECUCIÓN (CON FILTROS CORREGIDOS)
# ==========================================
archivo = 'Premier20-21.xlsx'
UMBRAL_MINUTOS = 800 
UMBRAL_CENTROS = 0.75

if os.path.exists(archivo):
    print(f"Cargando base de datos...")
    df_raw = pd.read_excel(archivo, engine='openpyxl')
    
    df_clean = df_raw[df_raw['Min'] >= UMBRAL_MINUTOS].copy()
    
    writer = pd.ExcelWriter('Resultados_Tesis_Final.xlsx', engine='openpyxl')
    
    for rol in PESOS_JSON.keys():
        print(f"\n--- Analizando Rol: {rol} ---")
        prefijo_rol = rol.split('_')[0]
        
        # --- FILTROS DE POSICIÓN ESTRICTOS ---
        if prefijo_rol in ["DC", "LB"]:
            # Solo DF puro (excluye MFDF)
            df_pos = df_clean[df_clean['Pos'].str.startswith('DF', na=False)].copy()
            if prefijo_rol == "DC":
                df_pos = df_pos[df_pos['Crs'] < UMBRAL_CENTROS]
                print(f"   -> Filtro DC: Pos='DF*' & Centros < {UMBRAL_CENTROS}")
            else:
                df_pos = df_pos[df_pos['Crs'] >= UMBRAL_CENTROS]
                print(f"   -> Filtro LB: Pos='DF*' & Centros >= {UMBRAL_CENTROS}")
                
        elif prefijo_rol in ["MC", "AM"]:
            # Medios (MF)
            df_pos = df_clean[df_clean['Pos'].str.contains('MF', na=False)].copy()
            
        else: # FW
            # Delanteros (FW)
            df_pos = df_clean[df_clean['Pos'].str.contains('FW', na=False)].copy()
        
        if len(df_pos) < 5: continue
            
        df_resultado = calcular_rating_rol(df_pos, rol)
        
        # Output
        top_3 = df_resultado.head(3)
        print(f"Top 3 {rol}:")
        for i, row in top_3.iterrows():
            precio_M = row['Precio_Estimado'] / 1_000_000
            print(f"   {i+1}. {row['Player']} ({row['Age']} años) -> €{precio_M:.1f}M (RTG: {row[f'RTG_{rol}']:.1f})")
            
        df_resultado.to_excel(writer, sheet_name=rol, index=False)
    
    writer.close()
    print("\n[ÉXITO] Archivo 'Resultados_Tesis_Final.xlsx' generado.")

else:
    print(f"No encuentro {archivo}")