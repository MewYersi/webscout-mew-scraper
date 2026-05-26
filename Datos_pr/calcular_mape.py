import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os

def generar_grafico_dual():
    print("🎨 Generando Radiografía de Ineficiencia del Mercado (Escala Ajustada)...")
    
    # 1. Cargar los archivos CSV que generaste en los pasos anteriores
    csv_elite = 'Auditoria_Traspasos_Elite.csv'
    csv_caros = 'Auditoria_Fichajes_Caros.csv'
    
    if not os.path.exists(csv_elite) or not os.path.exists(csv_caros):
        print(f"❌ Error: Faltan los archivos CSV. Asegúrate de tener {csv_elite} y {csv_caros} en esta carpeta.")
        return

    df_elite = pd.read_csv(csv_elite)
    df_caros = pd.read_csv(csv_caros)

    # 2. Configuración estética profesional (Nivel Tesis)
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharex=False, sharey=False)
    
    max_elite = max(df_elite['Costo Real (€M)'].max(), df_elite['SVD (€M)'].max())
    max_caros = max(df_caros['Costo Real (€M)'].max(), df_caros['SVD (€M)'].max())
    max_global = max(max_elite, max_caros) + 10

    # ==========================================
    # FUNCIÓN AUXILIAR: ESCALA PERSONALIZADA
    # ==========================================
    def aplicar_escala_log(ax):
        # 0 a 50 lineal en X, 0 a 40 lineal en Y. El resto se comprime.
        ax.set_xscale('symlog', linthresh=55)
        ax.set_yscale('symlog', linthresh=45)
        
        # Evitamos la notación científica
        formatter = ticker.ScalarFormatter()
        formatter.set_scientific(False)
        ax.xaxis.set_major_formatter(formatter)
        ax.yaxis.set_major_formatter(formatter)
        
        # Forzamos las marcas visuales exactamente donde las pediste
        ax.set_xticks([0, 25, 50, 100, 150, 200])
        ax.set_yticks([0, 20, 40, 80, 120, 160])

    # ==========================================
    # GRÁFICO IZQUIERDO: Enfoque "Moneyball" (Élite Táctica)
    # ==========================================
    sns.scatterplot(
        data=df_elite, 
        x='Costo Real (€M)', 
        y='SVD (€M)', 
        ax=axes[0],
        color='#2ecc71', # Verde Gema
        alpha=0.7, 
        s=60, 
        edgecolor='black'
    )
    
    # Línea de Precio Justo
    axes[0].plot([0, max_global], [0, max_global], color='gray', linestyle='--', linewidth=1.5, label='Valor Justo (y=x)')
    
    # Aplicar escala personalizada
    aplicar_escala_log(axes[0])
    
    axes[0].set_title('A. Enfoque Rendimiento (Top 68 RTG)', fontsize=14, fontweight='bold', pad=15)
    axes[0].set_xlabel('Costo Real Pagado (Millones €)', fontsize=12)
    axes[0].set_ylabel('Valor Deportivo - SVD (Millones €)', fontsize=12)
    axes[0].set_xlim(-2, max_elite + 10)
    axes[0].set_ylim(-2, df_elite['SVD (€M)'].max() + 10)
    axes[0].legend(loc='lower right')
    
    # Añadir texto explicativo usando coordenadas relativas (transAxes)
    axes[0].text(0.05, 0.90, 'ZONA DE GEMAS\n(SVD > Costo)', transform=axes[0].transAxes, color='green', fontsize=12, fontweight='bold', alpha=0.5)

    # ==========================================
    # GRÁFICO DERECHO: Enfoque "Galáctico" (Los más caros)
    # ==========================================
    sns.scatterplot(
        data=df_caros, 
        x='Costo Real (€M)', 
        y='SVD (€M)', 
        ax=axes[1],
        color='#e74c3c', # Rojo Peligro
        alpha=0.7, 
        s=60, 
        edgecolor='black'
    )
    
    # Línea de Precio Justo
    axes[1].plot([0, max_global], [0, max_global], color='gray', linestyle='--', linewidth=1.5, label='Valor Justo (y=x)')
    
    # Aplicar escala personalizada
    aplicar_escala_log(axes[1])
    
    axes[1].set_title('B. Enfoque Especulativo (Top 68 Más Caros)', fontsize=14, fontweight='bold', pad=15)
    axes[1].set_xlabel('Costo Real Pagado (Millones €)', fontsize=12)
    axes[1].set_ylabel('Valor Deportivo - SVD (Millones €)', fontsize=12)
    axes[1].set_xlim(-2, max_caros + 10)
    axes[1].set_ylim(-2, df_caros['SVD (€M)'].max() + 10)
    axes[1].legend(loc='lower right')

    # Añadir texto explicativo usando coordenadas relativas (transAxes)
    axes[1].text(0.65, 0.10, 'ZONA DE BURBUJAS\n(Costo > SVD)', transform=axes[1].transAxes, color='red', fontsize=12, fontweight='bold', alpha=0.5)

    # ==========================================
    # TÍTULO PRINCIPAL Y EXPORTACIÓN
    # ==========================================
    fig.suptitle('Radiografía de la Ineficiencia Transaccional en el Mercado de Élite Europeo', fontsize=18, fontweight='bold', y=1.05)
    
    plt.tight_layout()
    
    # Guardar en alta resolución
    nombre_archivo = 'Radiografia_Mercado_Tesis.png'
    plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    
    print(f"✅ ¡Gráfico guardado exitosamente como: {nombre_archivo}!")
    
    plt.show()

if __name__ == '__main__':
    generar_grafico_dual()