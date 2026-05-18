import pandas as pd
import numpy as np
import os

# =============================================================================
# 1. CONFIGURACIÓN ECONÓMICA (MODELO V7 - LOGICA DE MERCADO REAL)
# =============================================================================

# Multiplicador por "Impuesto de Club Rico". 
# Si compras al Man City, pagas más que si compras al Burnley.
TIER_MAP = {
    'Manchester City': 1, 'Manchester Utd': 1, 'Liverpool': 1, 'Chelsea': 1, 'Tottenham': 1,
    'Arsenal': 2, 'Leicester City': 2, 'Wolves': 2,
    'Aston Villa': 3, 'West Ham': 3, 'Leeds United': 3, 'Everton': 3, 'Southampton': 3, 'Crystal Palace': 3,
    'Newcastle Utd': 4, 'Brighton': 4, 'Burnley': 4,
    'Fulham': 5, 'West Brom': 5, 'Sheffield Utd': 5
}
MULTIPLICADORES_TIER = {1: 1.4, 2: 1.2, 3: 1.0, 4: 0.9, 5: 0.8}

def get_base_value(rating):
    """
    Calcula el valor base en Millones solo por el Rating (0-100).
    Ajustado para valorar más a la clase media alta (70-75).
    """
    if rating < 50: return 2.0
    
    # Jugadores de rotación (50-65) -> 5M a 20M
    if rating < 65:
        return 5 + (rating - 50) * 1.0
        
    # Buenos titulares (65-75) -> 20M a 45M
    if rating < 75:
        return 20 + (rating - 65) * 2.5 
        
    # Figuras (75-85) -> 45M a 85M
    if rating < 85:
        return 45 + (rating - 75) * 4.0
        
    # Superestrellas (85+) -> 85M para arriba (Exponencial)
    return 85 + (rating - 85) * 8.0

def get_age_factor(age):
    """
    Ajuste de edad. 
    CORRECCIÓN: Se extiende el 'Prime' hasta los 30 años para no infravalorar veteranos buenos.
    """
    if age <= 20: return 1.30  # Promesa joven (se paga futuro)
    if age <= 24: return 1.15  # En desarrollo
    if age <= 29: return 1.00  # Prime absoluto (Cairney entra aqui ahora)
    if age <= 31: return 0.85  # Veterano util
    if age <= 33: return 0.60  # Declive fisico
    return 0.30                # Retiro cercano

def get_pos_factor(rol_ideal):
    # Los delanteros y extremos siempre cuestan más
    if rol_ideal in ['FW_ST', 'FW_WG', 'FW_SS', 'AM']: return 1.15
    if rol_ideal in ['LB_OFF', 'DC']: return 1.05
    return 1.00

# =============================================================================
# 2. PESOS MAESTROS (SIN CAMBIOS)
# =============================================================================
PESOS_MAESTROS = {
  "FW_ST": {
    "categoria_pesos": { "Shooting": 0.53, "GAS": 0.20, "Possession": 0.10, "Passing": 0.10, "Aerial": 0.05, "Defensa": 0.02 },
    "estadisticas": {
      "Shooting": { "Gls": 0.45, "xG": 0.30, "npxG": 0.20, "SoT%": 0.05 },
      "GAS": { "GCA": 0.30, "SCA": 0.10, "SCAPassLive": 0.20, "SCASh": 0.15, "SCADrib": 0.10, "GCAPassLive": 0.15 },
      "Possession": { "TouchesAttPen": 0.50, "TouchesAtt3rd": 0.20, "DribSucc": 0.10, "Dispossesed": 0.10, "Touches": 0.10 },
      "Passing": { "Ast": 0.25, "xA": 0.20, "KP": 0.25, "PPA": 0.15, "Prog": 0.15 },
      "Aerial": { "AerialWon": 0.50, "AerialWon%": 0.30, "AerialLost": 0.20 },
      "Defensa": { "TklW": 0.50, "BallRec": 0.50 }
    }
  },
  "FW_WG": {
    "categoria_pesos": { "GAS": 0.32, "Possession": 0.24, "Shooting": 0.24, "Passing": 0.15, "Defensa": 0.03, "Aerial": 0.02 },
    "estadisticas": {
      "GAS": { "SCA": 0.10, "SCAPassLive": 0.20, "SCADrib": 0.25, "GCA": 0.15, "SCASh": 0.10, "GCAPassLive": 0.10, "SCAPassDead": 0.05, "GCADrib": 0.05 },
      "Possession": { "DribSucc": 0.20, "TouchesAtt3rd": 0.20, "TouchesAttPen": 0.15, "DribSucc%": 0.15, "TouchesMid3rd": 0.10, "Dispossesed": 0.10, "BallRecProg": 0.10 },
      "Shooting": { "Gls": 0.40, "xG": 0.30, "npxG": 0.20, "SoT%": 0.10 },
      "Passing": { "xA": 0.20, "Ast": 0.15, "CrsPA": 0.20, "KP": 0.15, "Prog": 0.15, "IntoLast3rd": 0.10, "PPA": 0.05 },
      "Defensa": { "TklW": 0.30, "BallRec": 0.30, "Int": 0.20, "TklAtt3rd": 0.20 },
      "Aerial": { "AerialWon%": 0.50, "AerialWon": 0.50 }
    }
  },
  "FW_SS": {
    "categoria_pesos": { "GAS": 0.34, "Shooting": 0.28, "Passing": 0.18, "Possession": 0.15, "Defensa": 0.03, "Aerial": 0.02 },
    "estadisticas": {
      "GAS": { "GCA": 0.20, "SCA": 0.10, "SCAPassLive": 0.25, "SCADrib": 0.20, "SCASh": 0.15, "GCAPassLive": 0.10 },
      "Shooting": { "Gls": 0.40, "xG": 0.30, "npxG": 0.20, "SoT%": 0.10 },
      "Possession": { "TouchesAtt3rd": 0.25, "TouchesAttPen": 0.20, "DribSucc": 0.15, "Dispossesed": 0.20, "TouchesMid3rd": 0.10, "BallRecProg": 0.10 },
      "Passing": { "xA": 0.20, "Ast": 0.20, "KP": 0.20, "PPA": 0.15, "IntoLast3rd": 0.10, "Prog": 0.10, "CrsPA": 0.05 },
      "Defensa": { "TklW": 0.40, "BallRec": 0.40, "Int": 0.20 },
      "Aerial": { "AerialWon%": 0.50, "AerialWon": 0.50 }
    }
  },
  "AM": {
    "categoria_pesos": { "GAS": 0.35, "Passing": 0.32, "Possession": 0.15, "Shooting": 0.14, "Defensa": 0.04 },
    "estadisticas": {
      "GAS": { "SCA": 0.05, "SCAPassLive": 0.25, "SCAPassDead": 0.10, "SCADrib": 0.15, "GCA": 0.15, "GCAPassLive": 0.10, "SCAFld": 0.10, "SCASh": 0.10 },
      "Passing": { "xA": 0.20, "Ast": 0.15, "KP": 0.15, "PPA": 0.15, "IntoLast3rd": 0.10, "Prog": 0.10, "CrsPA": 0.10, "PrgDist": 0.05 },
      "Possession": { "TouchesAtt3rd": 0.20, "DribSucc": 0.20, "DribSucc%": 0.10, "TouchesAttPen": 0.15, "Dispossesed": 0.20, "BallRecProg": 0.15 },
      "Shooting": { "xG": 0.30, "npxG": 0.20, "Gls": 0.40, "SoT%": 0.10 },
      "Defensa": { "TklW": 0.40, "Int": 0.30, "BallRec": 0.30 }
    }
  },
  "LB_OFF": {
    "categoria_pesos": { "Passing": 0.27, "Defensa": 0.25, "Possession": 0.23, "GAS": 0.17, "Aerial": 0.05, "Shooting": 0.03 },
    "estadisticas": {
      "Passing": { "CrsPA": 0.20, "xA": 0.15, "Ast": 0.10, "Prog": 0.15, "PrgDist": 0.10, "IntoLast3rd": 0.15, "KP": 0.10, "Cmp%Total": 0.05 },
      "Defensa": { "TklW": 0.25, "Int": 0.25, "Recov": 0.20, "Tkl": 0.15, "BallRec": 0.15 },
      "Possession": { "TouchesAtt3rd": 0.20, "DribSucc": 0.15, "TouchesMid3rd": 0.15, "Dispossesed": 0.15, "BallRecProg": 0.15, "Touches": 0.20 },
      "GAS": { "SCA": 0.20, "SCAPassLive": 0.40, "GCA": 0.20, "GCAPassLive": 0.20 },
      "Aerial": { "AerialWon%": 0.60, "AerialWon": 0.40 },
      "Shooting": { "xG": 0.50, "Gls": 0.50 }
    }
  },
  "LB_DEF": {
    "categoria_pesos": { "Defensa": 0.45, "Passing": 0.25, "Possession": 0.10, "Aerial": 0.10, "GAS": 0.07, "Shooting": 0.03 },
    "estadisticas": {
       "Defensa": { "TklW": 0.25, "Int": 0.25, "Recov": 0.20, "Tkl": 0.15, "BallRec": 0.15 },
       "Passing": { "Cmp%Total": 0.20, "Prog": 0.15, "PrgDist": 0.15, "LongCmp": 0.10, "IntoLast3rd": 0.10, "CrsPA": 0.10, "KP": 0.10, "Ast": 0.05, "xA": 0.05 },
       "Possession": { "Dispossesed": 0.25, "TouchesDef3rd": 0.25, "TouchesMid3rd": 0.25, "BallRecProg": 0.25 },
       "Aerial": { "AerialWon%": 0.60, "AerialWon": 0.40 },
       "GAS": { "SCA": 0.50, "SCAPassLive": 0.50 },
       "Shooting": { "xG": 0.50, "Gls": 0.50 }
    }
  },
  "DC": {
    "categoria_pesos": { "Defensa": 0.40, "Aerial": 0.20, "Passing": 0.15, "Possession": 0.10, "GAS": 0.10, "Shooting": 0.05 },
    "estadisticas": {
      "Defensa": { "TklW": 0.20, "Int": 0.20, "Recov": 0.15, "Clr": 0.15, "BallRec": 0.10, "TklDef3rd": 0.10, "Tkl": 0.10 },
      "Aerial": { "AerialWon%": 0.60, "AerialWon": 0.30, "AerialLost": 0.10 },
      "Passing": { "PrgDist": 0.20, "LongCmp": 0.15, "Cmp%Long": 0.15, "Cmp%Total": 0.20, "Prog": 0.20, "TotalCmp": 0.10 },
      "Possession": { "TouchesDef3rd": 0.40, "TouchesDefPen": 0.30, "Dispossesed": 0.30 },
      "GAS": { "SCAPassLive": 0.50, "SCA": 0.50 },
      "Shooting": { "xG": 0.50, "Gls": 0.50 }
    }
  },
  "MC_DEF": {
    "categoria_pesos": { "Defensa": 0.48, "Passing": 0.20, "Possession": 0.15, "Aerial": 0.12, "GAS": 0.04, "Shooting": 0.01 },
    "estadisticas": {
      "Defensa": { "TklW": 0.25, "Int": 0.25, "Recov": 0.20, "BallRec": 0.15, "TklMid3rd": 0.10, "TklDef3rd": 0.05 },
      "Passing": { "Cmp%Total": 0.20, "PrgDist": 0.15, "ShortCmp": 0.15, "Cmp%Short": 0.10, "MediumCmp": 0.15, "Cmp%Medium": 0.10, "Prog": 0.15 },
      "Possession": { "Dispossesed": 0.30, "TouchesMid3rd": 0.30, "BallRecProg": 0.20, "Touches": 0.20 },
      "Aerial": { "AerialWon%": 0.60, "AerialWon": 0.40 },
      "GAS": { "SCA": 0.50, "SCAPassLive": 0.50 },
      "Shooting": { "xG": 0.50, "Gls": 0.50 }
    }
  },
  "MC_EST": {
    "categoria_pesos": { "Passing": 0.32, "Defensa": 0.26, "Possession": 0.22, "GAS": 0.12, "Aerial": 0.06, "Shooting": 0.02 },
    "estadisticas": {
      "Passing": { "Prog": 0.15, "PrgDist": 0.15, "Cmp%Total": 0.10, "IntoLast3rd": 0.10, "KP": 0.10, "xA": 0.10, "Ast": 0.10, "PPA": 0.10, "Cmp%Medium": 0.10 },
      "Defensa": { "TklW": 0.20, "Int": 0.20, "Recov": 0.20, "BallRec": 0.20, "TklMid3rd": 0.20 },
      "Possession": { "TouchesMid3rd": 0.25, "Dispossesed": 0.20, "BallRecProg": 0.20, "DribSucc%": 0.15, "Touches": 0.20 },
      "GAS": { "SCA": 0.30, "SCAPassLive": 0.40, "GCA": 0.30 },
      "Aerial": { "AerialWon%": 0.60, "AerialWon": 0.40 },
      "Shooting": { "xG": 0.50, "Gls": 0.50 }
    }
  }
}

CANDIDATOS_ROLES = {
    'FW': ['FW_ST', 'FW_WG', 'FW_SS'],
    'AM': ['AM', 'FW_WG', 'FW_SS'],
    'MF': ['MC_EST', 'MC_DEF', 'AM'],
    'DM': ['MC_DEF', 'DC', 'LB_DEF', 'LB_OFF'],
    'DF': ['DC', 'LB_DEF', 'LB_OFF'],
    'FWMF': ['FW_WG', 'FW_SS', 'AM'],
    'MFDF': ['MC_DEF', 'DC', 'LB_OFF'],
    'DFFW': ['LB_OFF', 'FW_WG'], 
    'GK': [] 
}

# =============================================================================
# 3. FUNCIONES DEL MOTOR
# =============================================================================
def aplanar_pesos(jerarquia):
    pesos_abs = {}
    for rol, contenido in jerarquia.items():
        pesos_abs[rol] = {}
        cat_pesos = contenido.get('categoria_pesos', {})
        stats_bloque = contenido.get('estadisticas', {})
        for cat, peso_cat in cat_pesos.items():
            if cat in stats_bloque:
                stats = stats_bloque[cat]
                suma_int = sum(stats.values())
                for s, p in stats.items():
                    norm = p / suma_int if suma_int > 0 else 0
                    final = peso_cat * norm
                    if s == 'Dispossesed': final = -final
                    if s not in pesos_abs[rol]: pesos_abs[rol][s] = 0
                    pesos_abs[rol][s] += final
    return pesos_abs

def calcular_todos_los_ratings(df, pesos_abs):
    df_calc = df.copy()
    for rol, weights in pesos_abs.items():
        col_name = f'R_{rol}' 
        df_calc[col_name] = 0
        for stat, peso in weights.items():
            col_score = f"{stat}_Score"
            if col_score in df_calc.columns:
                val = df_calc[col_score].fillna(50) 
                df_calc[col_name] += val * peso
    return df_calc

# =============================================================================
# 4. EJECUCIÓN PRINCIPAL Y VALIDACIÓN
# =============================================================================
def procesar_premier_valuation():
    # A. Carga
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    archivo_input = None
    for f in os.listdir(carpeta_actual):
        if 'Premier20-21' in f and (f.endswith('.xlsx') or f.endswith('.csv')):
            archivo_input = os.path.join(carpeta_actual, f)
            break
            
    if not archivo_input:
        print("[ERROR] Falta el archivo Premier20-21")
        return

    print(f"Cargando datos de: {os.path.basename(archivo_input)}")
    if archivo_input.endswith('.xlsx'):
        df = pd.read_excel(archivo_input, engine='openpyxl')
    else:
        df = pd.read_csv(archivo_input)

    col_min = 'Min' if 'Min' in df.columns else 'Minutos'
    df = df[df[col_min] >= 450].copy()
    
    # B. Normalización
    print("Calculando percentiles...")
    cols_ignorar = ['Szn', 'Player', 'Nation', 'Pos', 'PosAdj', 'Squad', 'League', 'Age', 'Born']
    cols_num = [c for c in df.columns if c not in cols_ignorar and pd.api.types.is_numeric_dtype(df[c])]
    
    for c in cols_num:
        if df[c].std() > 0:
            rank_series = df.groupby('PosAdj')[c].rank(pct=True) * 100
            df[f"{c}_Score"] = rank_series.fillna(0).round(0).astype(int)
        else:
            df[f"{c}_Score"] = 50

    # C. Ratings Deportivos
    print("Calculando Rendimiento Deportivo...")
    PESOS_ABS = aplanar_pesos(PESOS_MAESTROS)
    df = calcular_todos_los_ratings(df, PESOS_ABS)

    df['Rol_Ideal'] = 'N/A'
    df['Rating_Final'] = 0.0
    
    for idx, row in df.iterrows():
        pos_fbref = row['PosAdj']
        candidatos = CANDIDATOS_ROLES.get(pos_fbref, [])
        if not candidatos: continue
            
        mejor_rol = 'N/A'
        mejor_puntaje = -1
        
        for rol in candidatos:
            col_r = f'R_{rol}'
            if col_r in df.columns:
                puntaje = row[col_r]
                if puntaje > mejor_puntaje:
                    mejor_puntaje = puntaje
                    mejor_rol = rol
        
        df.at[idx, 'Rol_Ideal'] = mejor_rol
        df.at[idx, 'Rating_Final'] = mejor_puntaje

    # =============================================================================
    # D. VALORACIÓN ECONÓMICA V7 (DEFINITIVA - RENDIMIENTO VS MERCADO)
    # =============================================================================
    print("Calculando Valor de Mercado V7...")
    
    # Inicializar columnas nuevas
    df['Valor_Rendimiento_Puro'] = 0.0  # (Valor Intrinseco - Es lo que debería valer por stats)
    df['Precio_Mercado'] = 0.0         # (Lo que te piden los clubes - Inflado)
    
    for idx, row in df.iterrows():
        rating = row['Rating_Final']
        edad = row['Age']
        rol = row['Rol_Ideal']
        equipo = row['Squad']
        
        # 1. Base ajustada (El suelo)
        valor_base = get_base_value(rating)
        
        # 2. Factores de multiplicación
        f_edad = get_age_factor(edad)
        f_pos = get_pos_factor(rol)
        
        # AJUSTE V7: Factor Estrella Exponencial (Solo para la élite)
        f_star = 1.0
        if rating >= 88: f_star = 1.50   
        elif rating >= 82: f_star = 1.25 
        elif rating >= 78: f_star = 1.10 # Ampliado un poco para jugadores muy buenos
        
        # --- VALOR DE RENDIMIENTO PURO (INTRÍNSECO) ---
        # Esto es lo que el jugador "produce" en el campo traducido a dinero
        fair_value = valor_base * f_edad * f_pos * f_star
        
        # --- PRECIO DE MERCADO (CON INFLACIÓN) ---
        # Esto es lo que te costaría sacarlo de su equipo actual
        tier_club = TIER_MAP.get(equipo, 4) 
        multiplicador_club = MULTIPLICADORES_TIER.get(tier_club, 0.9)
        market_price = fair_value * multiplicador_club
        
        # Guardamos en el DataFrame
        df.at[idx, 'Valor_Intrinseco'] = round(fair_value, 2) # Este es el "Valor por Rendimiento"
        df.at[idx, 'Precio_Mercado'] = round(market_price, 2)

    # === CÁLCULO DE ETIQUETAS V7 ===
    # Delta positivo = El jugador rinde más (Valor) de lo que cuesta (Precio)
    df['Delta_Valor'] = df['Valor_Intrinseco'] - df['Precio_Mercado']
    
    conditions = [
        # 1. FRANQUICIA: Jugadores de élite absoluta (Rating > 82). 
        # Son caros, pero son "Franquicia". No son sobrevalorados.
        (df['Rating_Final'] >= 82),
        
        # 2. EVITAR: Rendimiento insuficiente para Premier League (< 60).
        (df['Rating_Final'] < 60),

        # 3. GANGA: Jugadores buenos (>70) que cuestan MENOS de lo que rinden.
        # Bajamos el umbral del Delta a 5M para que Cairney entre.
        (df['Rating_Final'] >= 70) & (df['Delta_Valor'] >= 5),

        # 4. SOBREVALORADO: Cuestan mucho más de lo que rinden (Delta negativo grande).
        (df['Delta_Valor'] <= -10),
    ]
    
    choices = [
        'FRANQUICIA (TOP)',   # Caso 1
        'EVITAR (BAJO NIVEL)',# Caso 2
        'GANGA (FICHAR)',     # Caso 3
        'SOBREVALORADO'       # Caso 4
    ]
    
    # Si no cae en ninguno (Delta entre -10 y 5), es un precio justo/sólido
    df['Estado_Mercado'] = np.select(conditions, choices, default='OPCION SOLIDA')

    # E. Exportar
    ruta_salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Premier_Valuation_Model_V6_Final.csv')
    df.sort_values('Rating_Final', ascending=False).to_csv(ruta_salida, index=False)
    print(f"[EXITO] Archivo Final guardado en: {ruta_salida}")
    
    # VALIDACIÓN RÁPIDA EN CONSOLA (Sin caracteres raros)
    print("\n--- VALIDACION V7 ---")
    cols_ver = ['Player', 'Squad', 'Rating_Final', 'Valor_Intrinseco', 'Precio_Mercado', 'Estado_Mercado']
    print(df[cols_ver].head(15).to_string(index=False))

if __name__ == "__main__":
    procesar_premier_valuation()