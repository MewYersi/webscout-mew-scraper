import pandas as pd
import numpy as np
import os
import sys

# Forzar salida UTF-8 para evitar error con nombres como 'Matěj'
sys.stdout.reconfigure(encoding='utf-8')

def calibrar_roles_fw_v2():
    # 1. Cargar Datos
    carpeta = os.path.dirname(os.path.abspath(__file__))
    archivo = [f for f in os.listdir(carpeta) if 'Premier20-21' in f][0]
    if archivo.endswith('.xlsx'): df = pd.read_excel(os.path.join(carpeta, archivo), engine='openpyxl')
    else: df = pd.read_csv(os.path.join(carpeta, archivo))
    
    # 2. Filtrar solo Delanteros con minutos decentes
    col_min = 'Min' if 'Min' in df.columns else 'Minutos'
    df = df[(df['PosAdj'] == 'FW') & (df[col_min] >= 900)].copy() # Subí a 900 min para mayor fiabilidad
    
    # 3. Métrica de "Volumen Creativo" (CORREGIDA)
    # Asumimos que SCA y GCA ya son por 90 min. Si no lo son, se debería dividir.
    # Pero viendo tus datos (Kane SCA=3.71), SON por 90 min.
    df['GAS_Score_Real'] = df['SCA'] + df['GCA']
    
    # 4. Calcular los Cortes (Percentiles)
    print("\n--- DISTRIBUCIÓN DE CREATIVIDAD (GAS = SCA + GCA) ---")
    desc = df['GAS_Score_Real'].describe(percentiles=[0.40, 0.75]) # Ajustamos percentiles
    print(desc)
    
    corte_bajo = desc['40%']
    corte_alto = desc['75%']
    
    print(f"\nCORTE STRIKER (Finalizador puro): < {corte_bajo:.2f}")
    print(f"CORTE WINGER/SS (Creativo): > {corte_alto:.2f}")

    # 5. Clasificar para testear
    def clasificar(valor):
        if valor > corte_alto: return "WINGER (Alto Volumen)"
        if valor < corte_bajo: return "STRIKER (Bajo Volumen)"
        return "HYBRID (SS)"

    df['Rol_Test'] = df['GAS_Score_Real'].apply(clasificar)
    
    # 6. Ver a los jugadores
    cols = ['Player', 'GAS_Score_Real', 'Rol_Test', 'Gls', 'Ast']
    df_sorted = df.sort_values('GAS_Score_Real', ascending=False)
    
    print("\n--- TOP CREATIVOS (Deberían ser Mané, Grealish, etc) ---")
    print(df_sorted.head(10)[cols].to_string(index=False))
    
    print("\n--- ZONA MEDIA (Híbridos: Son, Vardy?) ---")
    mid_mask = (df['GAS_Score_Real'] >= corte_bajo) & (df['GAS_Score_Real'] <= corte_alto)
    print(df_sorted[mid_mask].head(10)[cols].to_string(index=False))
    
    print("\n--- ZONA BAJA (Tanques: Wood, Barnes?) ---")
    print(df_sorted.tail(10)[cols].to_string(index=False))

if __name__ == "__main__":
    calibrar_roles_fw_v2()