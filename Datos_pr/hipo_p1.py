import pandas as pd
import matplotlib.pyplot as plt

def exportar_tabla_imagen(df, titulo, pie_pagina, nombre_archivo):
    # Ajustar tamaño de la imagen
    fig, ax = plt.subplots(figsize=(10, len(df) * 0.5 + 1.5))
    ax.axis('off') 
    
    # Agregar Título (Clásico, negro)
    plt.figtext(0.5, 0.85, titulo, ha='center', fontsize=12, weight='bold', color='black')
    
    # Crear la tabla
    tabla = ax.table(cellText=df.values, 
                     colLabels=df.columns, 
                     cellLoc='center', 
                     loc='center',
                     bbox=[0, 0.15, 1, 0.65])
    
    # Estilizar la tabla (Estilo APA Universitario: Blanco y negro)
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(11)
    
    for (row, col), cell in tabla.get_celld().items():
        cell.set_facecolor('#FFFFFF') # Fondo totalmente blanco
        cell.set_edgecolor('black')   # Bordes negros
        cell.set_text_props(color='black') # Texto negro
        
        if row == 0:
            # Cabecera solo en negrita, sin color de fondo
            cell.set_text_props(weight='bold')

    # Agregar Pie de página
    plt.figtext(0.5, 0.05, pie_pagina, ha='center', fontsize=10, style='italic', color='black')
    
    # Guardar
    plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Imagen guardada con éxito (Estilo Clásico): {nombre_archivo}")
# ==========================================
# DATOS DE LAS TABLAS DE TU TESIS
# ==========================================

# TABLA 6: Hipótesis General
df_tabla6 = pd.DataFrame({
    "Variable Independiente": ["Sistema de Valoración (SVD)"],
    "Variable Dependiente": ["Costo Real Transaccional"],
    "Rho de Spearman": ["0.369**"],
    "Sig. (p-valor)": ["0.000"],
    "N (Muestra)": ["340"]
})
exportar_tabla_imagen(df_tabla6, 
                      "Tabla 6: Correlación entre el SVD y las transacciones de mercado",
                      "* La correlación es significativa en el nivel 0.05 (bilateral).\nFuente: Elaboración propia a partir del procesamiento estadístico computacional.",
                      "Tabla_6_Hipotesis_General.png")

# TABLA 7: Hipótesis Específica 1 (Eficacia Algorítmica)
df_tabla7 = pd.DataFrame({
    "Módulo de Procesamiento": ["Aduanas Tácticas", "Desacoplamiento JSON", "Normalización (P85/P95)"],
    "Casos de Prueba": ["3085", "3085", "3085"],
    "Éxito de Procesamiento": ["100%", "100%", "100%"],
    "Filtrado de Sesgos": ["Sí", "Sí", "N/A"],
    "Eficacia Funcional": ["1.000", "1.000", "1.000"]
})
exportar_tabla_imagen(df_tabla7, 
                      "Tabla 7: Nivel de eficacia del procesamiento algorítmico del SVD (Caja Blanca)",
                      "Fuente: Elaboración propia a partir de las trazas de ejecución del algoritmo.",
                      "Tabla_7_Eficacia_SVD.png")

# TABLA 8: Hipótesis Específica 2 (Contexto)
df_tabla8 = pd.DataFrame({
    "Variable Independiente": ["Integración Contextual (Valor SVD)"],
    "Variable Dependiente": ["Precio Real Pagado (Mercado)"],
    "Rho de Spearman": ["0.369**"],
    "Sig. (p-valor)": ["0.000"],
    "N (Muestra)": ["340"]
})
exportar_tabla_imagen(df_tabla8, 
                      "Tabla 8: Correlación entre variables contextuales y el precio de mercado",
                      "* La correlación es significativa en el nivel 0.05 (bilateral).\nFuente: Elaboración propia a partir del procesamiento estadístico computacional.",
                      "Tabla_8_Variables_Contextuales.png")

# TABLA 9: Hipótesis Específica 3 (UI/UX)
df_tabla9 = pd.DataFrame({
    "Componente UI/UX": ["Panel Maestro", "Perfil Dinámico", "Matriz Scatter"],
    "Requerimiento Funcional": ["Filtros y búsqueda general", "Carga de radares tácticos", "Graficado de ineficiencias"],
    "Estado de Prueba": ["Aprobado", "Aprobado", "Aprobado"],
    "Nivel Cumplimiento": ["100%", "100%", "100%"]
})
exportar_tabla_imagen(df_tabla9, 
                      "Tabla 9: Matriz de cumplimiento funcional de la interfaz ScoutMew Vision",
                      "Fuente: Elaboración propia a partir de las pruebas de usuario (Frontend).",
                      "Tabla_9_Cumplimiento_UI.png")

# TABLA 10: Hipótesis Específica 4 (Mercado)
df_tabla10 = pd.DataFrame({
    "Variable Independiente": ["Tasación Algorítmica (SVD)"],
    "Variable Dependiente": ["Costo Real de Fichaje"],
    "Rho de Spearman": ["0.369**"],
    "Sig. (p-valor)": ["0.000"],
    "N (Muestra)": ["340"]
})
exportar_tabla_imagen(df_tabla10, 
                      "Tabla 10: Correlación entre la valoración SVD y el costo real de fichaje",
                      "* La correlación es significativa en el nivel 0.05 (bilateral).\nFuente: Elaboración propia a partir del procesamiento estadístico computacional.",
                      "Tabla_10_Validacion_Mercado.png")