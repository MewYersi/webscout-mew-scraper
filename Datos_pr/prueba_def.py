import pandas as pd
import numpy as np
import os
import sys
import warnings

# --- CONFIGURACIÓN ---
sys.stdout.reconfigure(encoding='utf-8')
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# ==========================================
# 1. PESOS Y PARAMETROS
# ==========================================
PESOS_JSON = {
    "DC": {
        "categoria_pesos": {
            "Defensa": 0.40,
            "Aerial": 0.20,
            "Passing": 0.30,
            "Possession": 0.10
        },
        "estadisticas": {
            "Defensa": {
                "Int": 0.20,
                "Clr": 0.20,
                "Recov": 0.20,
                "TklW": 0.15,
                "BallRec": 0.15,
                "TklDef3rd": 0.10
            },
            "Aerial": {
                "AerialWon%": 0.60,
                "AerialWon": 0.40
            },
            "Passing": {
                "Cmp%Total": 0.25,
                "PrgDist": 0.20,
                "Prog": 0.20,
                "LongCmp": 0.20,
                "Cmp%Long": 0.15
            },
            "Possession": {
                "TouchesDef3rd": 0.45,
                "TouchesMid3rd": 0.25,
                "Dispossesed": 0.30
            }
        }
    },
    "LB_DEF": {
        "categoria_pesos": {
            "Defensa": 0.50,
            "Passing": 0.25,
            "Possession": 0.15,
            "Aerial": 0.10
        },
        "estadisticas": {
            "Defensa": {
                "TklW": 0.25,
                "Int": 0.25,
                "Recov": 0.20,
                "Clr": 0.15,
                "TklDef3rd": 0.15
            },
            "Passing": {
                "Cmp%Total": 0.35,
                "PrgDist": 0.25,
                "Prog": 0.25,
                "IntoLast3rd": 0.15
            },
            "Possession": {
                "TouchesDef3rd": 0.40,
                "TouchesMid3rd": 0.30,
                "Dispossesed": 0.30
            },
            "Aerial": {
                "AerialWon%": 0.70,
                "AerialWon": 0.30
            }
        }
    },
    "LB_OFF": {
        "categoria_pesos": {
            "Passing": 0.35,
            "Possession": 0.25,
            "GAS": 0.20,
            "Defensa": 0.20
        },
        "estadisticas": {
            "Passing": {
                "xA": 0.30,
                "CrsPA": 0.25,
                "KP": 0.20,
                "Prog": 0.15,
                "IntoLast3rd": 0.10
            },
            "Possession": {
                "TouchesAtt3rd": 0.40,
                "PrgDist": 0.30,
                "DribSucc": 0.20,
                "Dispossesed": 0.10
            },
            "GAS": {
                "SCA": 0.60,
                "SCAPassLive": 0.40
            },
            "Defensa": {
                "Recov": 0.30,
                "TklW": 0.30,
                "Int": 0.25,
                "BallRec": 0.15
            }
        }
    },
    "MC_DEF": {
        "categoria_pesos": {
            "Defensa": 0.55,
            "Passing": 0.25,
            "Possession": 0.12,
            "Aerial": 0.05,
            "GAS": 0.02,
            "Shooting": 0.01
        },
        "estadisticas": {
            "Defensa": {
                "Int": 0.25,
                "Recov": 0.25,
                "TklW": 0.15,
                "BallRec": 0.10,
                "BallRecProg": 0.10,
                "TklMid3rd": 0.10,
                "Tkl": 0.05
            },
            "Passing": {
                "Cmp%Total": 0.35,
                "ShortCmp": 0.15,
                "Cmp%Short": 0.15,
                "MediumCmp": 0.10,
                "Prog": 0.10,
                "PrgDist": 0.10,
                "LongCmp": 0.05
            },
            "Possession": {
                "Dispossesed": 0.40,
                "TouchesMid3rd": 0.30,
                "TouchesDef3rd": 0.20,
                "BallRec": 0.10
            },
            "Aerial": {
                "AerialWon%": 1.00
            },
            "GAS": {
                "SCA": 0.50,
                "SCAPassLive": 0.50
            },
            "Shooting": {
                "Gls": 1.00
            }
        }
    },
    "MC_ORG": {
        "categoria_pesos": {
            "Passing": 0.45,
            "Possession": 0.25,
            "Defensa": 0.16,
            "GAS": 0.12,
            "Aerial": 0.01,
            "Shooting": 0.01
        },
        "estadisticas": {
            "Passing": {
                "Prog": 0.20,
                "PrgDist": 0.20,
                "IntoLast3rd": 0.15,
                "Cmp%Total": 0.15,
                "KP": 0.10,
                "LongCmp": 0.10,
                "xA": 0.05,
                "xAG": 0.05
            },
            "Possession": {
                "PrgDist": 0.30,
                "TouchesMid3rd": 0.20,
                "TouchesLive": 0.15,
                "Dispossesed": 0.12,
                "DribSucc": 0.13,
                "TouchesDef3rd": 0.10
            },
            "Defensa": {
                "Recov": 0.35,
                "Int": 0.30,
                "BallRec": 0.20,
                "TklMid3rd": 0.15
            },
            "GAS": {
                "SCA": 0.60,
                "SCAPassLive": 0.40
            },
            "Aerial": {
                "AerialWon%": 1.00
            },
            "Shooting": {
                "Gls": 0.50,
                "npxG/Sh": 0.50
            }
        }
    },
    "MC_EST": {
        "categoria_pesos": {
            "Passing": 0.28,
            "Possession": 0.22,
            "Defensa": 0.22,
            "GAS": 0.15,
            "Shooting": 0.08,
            "Aerial": 0.05
        },
        "estadisticas": {
            "Passing": {
                "Prog": 0.15,
                "IntoLast3rd": 0.15,
                "PrgDist": 0.15,
                "xA": 0.15,
                "Cmp%Total": 0.10,
                "KP": 0.10,
                "PPA": 0.10,
                "Ast": 0.10
            },
            "Defensa": {
                "Recov": 0.25,
                "TklMid3rd": 0.20,
                "TklW": 0.20,
                "Int": 0.15,
                "BallRec": 0.10,
                "BallRecProg": 0.10
            },
            "Possession": {
                "TouchesMid3rd": 0.20,
                "TouchesAtt3rd": 0.15,
                "TouchesDef3rd": 0.15,
                "PrgDist": 0.15,
                "TouchesAttPen": 0.10,
                "DribSucc": 0.10,
                "Dispossesed": 0.10,
                "BallRecProg": 0.05
            },
            "GAS": {
                "SCA": 0.35,
                "SCAPassLive": 0.30,
                "GCA": 0.20,
                "SCADef": 0.10,
                "SCADrib": 0.05
            },
            "Aerial": {
                "AerialWon%": 0.60,
                "AerialWon": 0.40
            },
            "Shooting": {
                "Gls": 0.30,
                "npxG": 0.25,
                "G-xG": 0.20,
                "xG": 0.15,
                "SoT%": 0.10
            }
        }
    },
    "AM": {
        "categoria_pesos": {
            "Passing": 0.45,
            "GAS": 0.40,
            "Shooting": 0.10,
            "Possession": 0.05
        },
        "estadisticas": {
            "Passing": {
                "xAG": 0.20,
                "xA": 0.20,
                "KP": 0.20,
                "PPA": 0.15,
                "Prog": 0.15,
                "IntoLast3rd": 0.10
            },
            "GAS": {
                "SCA": 0.30,
                "SCAPassLive": 0.30,
                "GCA": 0.20,
                "SCAPassDead": 0.10,
                "SCADrib": 0.10
            },
            "Shooting": {
                "Gls": 0.30,
                "npxG": 0.30,
                "np:G-xG": 0.20,
                "npxG/Sh": 0.20
            },
            "Possession": {
                "TouchesAtt3rd": 0.50,
                "TouchesAttPen": 0.50
            }
        }
    },
    "FW_WG": {
        "categoria_pesos": {
            "Possession": 0.35,
            "GAS": 0.25,
            "Passing": 0.20,
            "Shooting": 0.20
        },
        "estadisticas": {
            "Possession": {
                "DribSucc": 0.40,
                "PrgDist": 0.40,
                "TouchesAtt3rd": 0.20
            },
            "GAS": {
                "SCADrib": 0.60,
                "GCA": 0.30,
                "SCAFld": 0.10
            },
            "Passing": {
                "CrsPA": 0.50,
                "xAG": 0.30,
                "IntoLast3rd": 0.20
            },
            "Shooting": {
                "Gls": 0.50,
                "npxG": 0.50
            }
        }
    },
    "FW_ST": {
        "categoria_pesos": {
            "Shooting": 0.60,
            "GAS": 0.25,
            "Aerial": 0.10,
            "Passing": 0.05
        },
        "estadisticas": {
            "Shooting": {
                "Gls": 0.40,
                "npxG": 0.30,
                "np:G-xG": 0.20,
                "npxG/Sh": 0.10
            },
            "GAS": {
                "GCA": 0.50,
                "SCA": 0.50
            },
            "Aerial": {
                "AerialWon": 0.50,
                "AerialWon%": 0.50
            },
            "Passing": {
                "xA": 0.50,
                "Ast": 0.50
            }
        }
    },
    "FW_SS": {
        "categoria_pesos": {
            "Shooting": 0.30,
            "GAS": 0.30,
            "Passing": 0.30,
            "Possession": 0.10
        },
        "estadisticas": {
            "Shooting": {
                "Gls": 0.40,
                "npxG": 0.40,
                "npxG/Sh": 0.20
            },
            "GAS": {
                "SCA": 0.50,
                "SCAPassLive": 0.50
            },
            "Passing": {
                "PPA": 0.40,
                "KP": 0.30,
                "xA": 0.30
            },
            "Possession": {
                "TouchesAttPen": 0.70,
                "DribSucc": 0.30
            }
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

def calcular_valor_deportivo(row, col_rtg, nombre_rol):
    rtg = row[col_rtg]
    edad = row['Age']
    minutos = row['Min']
    liga = row['League']

    # Curva Exponencial Base
    precio_base = ((rtg / 10) ** 6) * 200  

    # 1. EDAD: Aplanada.
    factor_edad = 1.0
    if edad >= 34: 
        factor_edad = 0.90
    # 2. MINUTOS
    pct_minutos = minutos / 3420
    factor_minutos = 0.6 + (pct_minutos * 0.4)
    if minutos < 1000: 
        factor_minutos = 0.5
    # 3. LIGA
    factor_liga = 1.0
    if liga == 'Premier League':
        factor_liga = 1.15
    elif liga in ['La Liga', 'Bundesliga', 'Serie A']:
        factor_liga = 1.0
    else:
        factor_liga = 0.85

    # 4. POSICIÓN
    prefijo = nombre_rol.split('_')[0]
    if prefijo in ['FW', 'AM']:
        factor_pos = 1.10 
    elif prefijo == 'MC':
        factor_pos = 1.0
    else: 
        factor_pos = 0.98 

    valor_final = precio_base * factor_edad * factor_minutos * factor_liga * factor_pos
    
    return round(valor_final, -4)

# ==========================================
# 3. PROCESAMIENTO MULTI-LIGA Y MULTI-TEMPORADA (V15: CON CURA DE SESGO)
# ==========================================
archivo = 'DataFramev1.xlsx'
UMBRAL_MINUTOS = 800

# --- NUEVOS UMBRALES DE ADUANA TÁCTICA ---


UMBRAL_CENTROS = 15.0 # Si tira más de 15 centros al año, sospechamos que es lateral
UMBRAL_TOQUES_ATT = 12.0 # Si promedia/acumula más de 12 toques en el tercio rival, es lateral

metricas_defensivas = ['TklW', 'Int', 'Recov', 'Clr', 'Tkl', 'TklDef3rd', 'TklMid3rd', 'TklAtt3rd', 'BallRec', 'BallRecProg']

    if os.path.exists(archivo):
        print("🚀 Iniciando Motor V15 (Modo Escala Europea + Cura de Sesgo)...")
        xls = pd.ExcelFile(archivo, engine='openpyxl')
        all_assessments = []
        stats_inversas = ['Dispossesed', 'AerialLost']

        for sheet_name in xls.sheet_names:
            print(f"\n📅 Procesando Temporada Global: {sheet_name}")
            df_season = pd.read_excel(xls, sheet_name=sheet_name)
            df_clean = df_season[df_season['Min'] >= UMBRAL_MINUTOS].copy()
            
            if df_clean.empty: continue
            
            print(f" 🌍 Calculando radares y métricas a nivel continental ({len(df_clean)} jugadores)...")
            stats_radar = ['Gls', 'Ast', 'TotalCmp', 'Sh', 'DribSucc', 'Tkl']
            
            for stat in stats_radar:
                if stat in df_clean.columns:
                    _min, _max = df_clean[stat].min(), df_clean[stat].max()
                    if _max - _min > 0:
                        df_clean[f'{stat}_Score'] = ((df_clean[stat] - _min) / (_max - _min) * 100).fillna(0)
                    else:
                        df_clean[f'{stat}_Score'] = 0

            for rol in PESOS_JSON.keys():
                prefijo_rol = rol.split('_')[0]
                df_pos = pd.DataFrame()
                
                if prefijo_rol in ["DC", "LB"]:
                    df_temp = df_clean[df_clean['Pos'].str.contains('DF', na=False)].copy()
                    # LA NUEVA ADUANA TÁCTICA
                    if prefijo_rol == "DC":
                        # Eres central SOLO SI tienes pocos centros Y pocos toques en ataque
                        df_pos = df_temp[(df_temp['Crs'] < UMBRAL_CENTROS) & (df_temp['TouchesAtt3rd'] < UMBRAL_TOQUES_ATT)].copy()
                    else:
                        # Eres lateral SI superas los centros O superas los toques en ataque
                        df_pos = df_temp[(df_temp['Crs'] >= UMBRAL_CENTROS) | (df_temp['TouchesAtt3rd'] >= UMBRAL_TOQUES_ATT)].copy()

                elif prefijo_rol in ["MC", "AM"]:
                    df_pos = df_clean[df_clean['Pos'].str.contains('MF', na=False)].copy()
                else:
                    df_pos = df_clean[df_clean['Pos'].str.contains('FW', na=False)].copy()
                    
                if len(df_pos) < 2: continue
                
                pesos = obtener_pesos_planos(rol)
                df_calc = df_pos.copy()
                col_rating = 'Rating_Final'
                df_calc[col_rating] = 0
                
                # --- NUEVO: VARIABLES PARA EL BONO TODOTERRENO ---
                df_calc['Puntaje_Def'] = 0.0
                df_calc['Puntaje_Pas'] = 0.0
                df_calc['Puntaje_Gas'] = 0.0
                
                for col, peso in pesos.items():
                    if col in df_calc.columns:
                        col_vals = pd.to_numeric(df_calc[col], errors='coerce').fillna(0)
                        _min = col_vals.min()
                        
                        # --- NUEVO: TECHO INTELIGENTE (P85 para defensa, P95 para el resto) ---

                        
                        if col in metricas_defensivas:
                            _max_real = col_vals.quantile(0.85)
                        else:
                            _max_real = col_vals.quantile(0.95)
                            
                        if _max_real <= _min: _max_real = col_vals.max()
                        
                        if _max_real - _min == 0:
                            norm = 0
                        else:
                            if col in stats_inversas:
                                norm = (_max_real - np.clip(col_vals, _min, _max_real)) / (_max_real - _min)
                            else:
                                norm = (np.clip(col_vals, _min, _max_real) - _min) / (_max_real - _min)
                                
                        puntos_aportados = norm * peso
                        df_calc[col_rating] += puntos_aportados
                        
                        # --- NUEVO: RASTREO POR CATEGORÍA PARA EL BONO ---
                        if col in PESOS_JSON[rol]['estadisticas'].get('Defensa', {}):
                            df_calc['Puntaje_Def'] += puntos_aportados / PESOS_JSON[rol]['categoria_pesos']['Defensa']
                        if col in PESOS_JSON[rol]['estadisticas'].get('Passing', {}):
                            df_calc['Puntaje_Pas'] += puntos_aportados / PESOS_JSON[rol]['categoria_pesos']['Passing']
                        if col in PESOS_JSON[rol]['estadisticas'].get('GAS', {}):
                            df_calc['Puntaje_Gas'] += puntos_aportados / PESOS_JSON[rol]['categoria_pesos'].get('GAS', 1) # Evitar div/0
                            
                df_calc[col_rating] *= 100
                
                # --- NUEVO: APLICAR BONO TODOTERRENO SOLO A MEDIOCENTROS ---
                if prefijo_rol == "MC":
                    # EXIGENCIA ALTA: Tienen que ser élite en Defensa (>= 0.80) Y en Pase o Creación (>= 0.80)
                    condicion_todoterreno = (df_calc['Puntaje_Def'] >= 0.80) & ((df_calc['Puntaje_Pas'] >= 0.80) | (df_calc['Puntaje_Gas'] >= 0.80))
                    # BONO REDUCIDO: Solo un 3% extra (1.03) a su nota base
                    df_calc[col_rating] = np.where(condicion_todoterreno, df_calc[col_rating] * 1.03, df_calc[col_rating])
                    # Limitamos a 100 máximo
                    df_calc[col_rating] = np.clip(df_calc[col_rating], 0, 100)
                    
                # --- AJUSTE POR MINUTOS (Aplica a todos los roles) ---
                df_calc[col_rating] = np.where(
                    df_calc['Min'] < 1800,
                    df_calc[col_rating] * (0.85 + (df_calc['Min'] / 1800) * 0.15),
                    df_calc[col_rating]
                )
                
                # --- NUEVO: BONO DE CENTRAL MODERNO (Líbero) ---
                if prefijo_rol == "DC":
                    # Verificamos que las columnas existan para evitar errores
                    if 'AerialWon%' in df_calc.columns and 'Cmp%Total' in df_calc.columns:
                        # Si el jugador es Top 20% en Eficacia Aérea Y Top 20% en Salida de Balón
                        condicion_libero = (df_calc['AerialWon%'] >= df_calc['AerialWon%'].quantile(0.80)) & (df_calc['Cmp%Total'] >= df_calc['Cmp%Total'].quantile(0.80))
                        # Bono del 5% a la nota final
                        df_calc[col_rating] = np.where(condicion_libero, df_calc[col_rating] * 1.05, df_calc[col_rating])
                        df_calc[col_rating] = np.clip(df_calc[col_rating], 0, 100)
                        
                # --- FINALIZACIÓN DE CÁLCULOS ---
                # Solo guardamos el Valor Deportivo, adiós Precio de Mercado
                df_calc['Valor_Deportivo'] = df_calc.apply(
                    lambda r: calcular_valor_deportivo(r, col_rating, rol), axis=1
                )
                df_calc['Mejor_Rol'] = rol
                
                # Guardamos el resultado de este rol
                all_assessments.append(df_calc)

    print("\n🔄 Unificando base de datos masiva...")
    df_master = pd.concat(all_assessments)
    
    df_sorted = df_master.sort_values(by=['Player', 'Szn', 'Rating_Final'], ascending=[True, True, False])
    df_top3 = df_sorted.groupby(['Player', 'Szn']).head(3).copy()
    df_top3['Rank'] = df_top3.groupby(['Player', 'Szn']).cumcount() + 1
    
    df_roles_info = df_top3.pivot(index=['Player', 'Szn'], columns='Rank', values=['Mejor_Rol', 'Rating_Final'])
    df_roles_info.columns = [f"{'Rol' if col[0] == 'Mejor_Rol' else 'RTG'}_{col[1]}" for col in df_roles_info.columns]
    df_roles_info = df_roles_info.reset_index()
    
    df_master = df_master.sort_values('Valor_Deportivo', ascending=False)
    df_master_unique = df_master.drop_duplicates(subset=['Player', 'Szn'], keep='first')
    df_master_unique = df_master_unique.rename(columns={'Mejor_Rol': 'Rol_Principal', 'Rating_Final': 'RTG_Principal'})
    
    df_final = df_master_unique.merge(df_roles_info, on=['Player', 'Szn'], how='left')
    output_path = 'Scouting_Database_Final.csv'
    df_final.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n✅ ¡PROCESO TERMINADO CON ÉXITO!")
    print(f"📄 Archivo Maestro generado: {output_path}")
else:
    print(f"❌ Archivo {archivo} no encontrado.")