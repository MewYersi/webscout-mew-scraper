import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def generar_scatter_tesis(archivo_csv):
    print("Cargando datos y procesando...")
    
    # 1. Cargar el dataset
    try:
        df = pd.read_csv("Scouting_Database_con_TM.csv")
    except FileNotFoundError:
        print("Error: No se encontró el archivo CSV.")
        return

    # Limpieza básica
    df['Valor_Deportivo'] = pd.to_numeric(df['Valor_Deportivo'], errors='coerce')
    df['TM_Value'] = pd.to_numeric(df['TM_Value'], errors='coerce')

    # 2. Recopilar la élite (Top 68 por temporada)
    temporadas = sorted(df['Szn'].unique())
    lista_top = []

    for temp in temporadas:
        df_temp = df[df['Szn'] == temp].copy()
        top_68 = df_temp.nlargest(68, 'RTG_Principal')
        
        # Filtramos los que tienen valor 0 en Transfermarkt
        top_68 = top_68[top_68['TM_Value'] > 0]
        lista_top.append(top_68)

    # Unir todos los datos en un solo DataFrame (~340 jugadores)
    df_final = pd.concat(lista_top)
    
    # 3. Estandarizar a Millones de Euros
    df_final['TM_Millones'] = df_final['TM_Value'] / 1_000_000
    df_final['VD_Millones'] = df_final['Valor_Deportivo'] / 1_000_000

    print(f"Total de jugadores graficados: {len(df_final)}")

    # ==========================================
    # 4. CONFIGURACIÓN ESTÉTICA DEL GRÁFICO (Tesis)
    # ==========================================
    # Estilo limpio y profesional
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 8))

    # Crear el gráfico de dispersión
    # Usamos el color (hue) para diferenciar las temporadas ligeramente
    scatter = sns.scatterplot(
        data=df_final, 
        x='TM_Millones', 
        y='VD_Millones', 
        hue='Szn', 
        palette='viridis', 
        alpha=0.7, 
        s=60, # Tamaño de los puntos
        edgecolor='black'
    )

    # 5. LÍNEAS DE REFERENCIA
    # Obtener los límites del gráfico para dibujar las líneas
    max_val = max(df_final['TM_Millones'].max(), df_final['VD_Millones'].max()) + 20

    # Línea 1: La diagonal perfecta (y = x). 
    # Si un punto cae aquí, tu modelo y el mercado dicen exactamente el mismo precio.
    plt.plot([0, max_val], [0, max_val], color='red', linestyle='--', linewidth=1.5, label='Igualdad Perfecta (y=x)')

    # Línea 2: Línea de Regresión de tu modelo (Tendencia real)
    # Esto demuestra la correlación a pesar de la diferencia de escala
    sns.regplot(
        data=df_final, 
        x='TM_Millones', 
        y='VD_Millones', 
        scatter=False, 
        color='blue', 
        line_kws={'linewidth': 2, 'label': 'Tendencia de Valoración (Modelo)'}
    )

    # 6. ETIQUETAS Y TÍTULOS
    plt.title('Comparativa de Valoración: Modelo de Rendimiento vs Transfermarkt\nÉlite Continental (Top 68 por Temporada)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Valor de Mercado Real - Transfermarkt (Millones €)', fontsize=12)
    plt.ylabel('Valor Deportivo Calculado - Algoritmo (Millones €)', fontsize=12)
    
    # Ajustar ejes para que empiecen en 0
    plt.xlim(0, df_final['TM_Millones'].max() + 20)
    plt.ylim(0, df_final['VD_Millones'].max() + 20)

    # Leyenda
    plt.legend(title='Leyenda', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Guardar en alta resolución (300 dpi es el estándar para imprimir tesis)
    nombre_archivo = 'scatter_valoracion_tesis.png'
    plt.tight_layout()
    plt.savefig(nombre_archivo, dpi=300)
    print(f"\n¡Éxito! Gráfico guardado en alta resolución como: {nombre_archivo}")
    
    # Mostrar la ventana interactiva
    plt.show()

# Ejecutar
generar_scatter_tesis('Scouting_Database_con_TM.csv')