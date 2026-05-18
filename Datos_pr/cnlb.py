import pandas as pd
import numpy as np
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

archivo = 'Premier20-21.xlsx'

if os.path.exists(archivo):
    print("Cargando datos para diagnóstico de Centros...")
    df = pd.read_excel(archivo, engine='openpyxl')
    
    # 1. Filtramos solo Defensas con tiempo de juego decente
    df_def = df[df['Pos'].str.contains('DF', na=False)].copy()
    df_def = df_def[df_def['Min'] > 800].copy()
    
    # 2. Creamos la métrica "Centros por 90 minutos"
    # Es vital dividir por 90s, si no, el que juega más minutos siempre tendrá más centros
    df_def['Crs_p90'] = df_def['Crs'] / df_def['90s']
    
    # 3. Estadísticas
    promedio = df_def['Crs_p90'].mean()
    mediana = df_def['Crs_p90'].median()
    
    print(f"\n--- ESTADÍSTICAS DE CENTROS (Crs/90) PARA DEFENSAS ---")
    print(f"Promedio General: {promedio:.2f} centros por partido")
    print(f"Mediana (Punto medio): {mediana:.2f} centros por partido")
    
    # 4. Probemos 3 cortes distintos para ver cuál separa mejor
    cortes = [0.2, 0.5, 0.8]
    
    for corte in cortes:
        print(f"\n[PRUEBA] Si ponemos el corte en {corte} centros/90:")
        
        # Quiénes quedarían como CENTRALES (< corte)
        centrales = df_def[df_def['Crs_p90'] < corte].sort_values('Crs_p90', ascending=False).head(5)
        nombres_c = ", ".join([f"{row['Player']} ({row['Crs_p90']:.2f})" for i, row in centrales.iterrows()])
        
        # Quiénes quedarían como LATERALES (> corte)
        laterales = df_def[df_def['Crs_p90'] > corte].sort_values('Crs_p90', ascending=True).head(5)
        nombres_l = ", ".join([f"{row['Player']} ({row['Crs_p90']:.2f})" for i, row in laterales.iterrows()])
        
        print(f"   -> Centrales (Límite superior): {nombres_c}")
        print(f"   -> Laterales (Límite inferior): {nombres_l}")

else:
    print("No encuentro el archivo.")