import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# Cargar el archivo con los datos procesados (el V5 que acabamos de hacer)
# Asegúrate de que el nombre del archivo sea el correcto
ARCHIVO_DATOS = 'Premier_Valuation_Model_V5_Final.csv'

# Si no encuentras el archivo generado, intenta cargarlo o avisa
if not os.path.exists(ARCHIVO_DATOS):
    print(f" No encuentro {ARCHIVO_DATOS}. Asegúrate de haber corrido el script de valoración antes.")
    # Para pruebas, puedes comentar esto y cargar tu excel manual si prefieres
else:
    df = pd.read_csv(ARCHIVO_DATOS)

# =============================================================================
# 1. GRÁFICO DE RADAR (ESTILO FOOTBALL MANAGER)
# =============================================================================
def crear_radar_fm(nombre_jugador):
    """
    Genera un gráfico de radar comparando las métricas CLAVE del rol del jugador
    contra el promedio de los jugadores en su misma posición.
    """
    # 1. Buscar al jugador
    jugador = df[df['Player'] == nombre_jugador].iloc[0]
    if jugador.empty:
        print("Jugador no encontrado.")
        return

    posicion = jugador['PosAdj']
    rol_ideal = jugador['Rol_Ideal']
    
    # 2. Definir métricas visuales según el Rol (Para que el gráfico tenga sentido)
    # Estas son las "esquinas" del hexágono. Puedes personalizar más.
   # 2. Definir métricas visuales (CORREGIDO: Usando nombres reales del Excel)
    metricas_map = {
        'FW_ST': [
            'Gls_Score',           # Goles
            'xG_Score',            # Goles Esperados
            'Sh_Score',            # Tiros Totales (Reemplaza a Shooting)
            'TouchesAttPen_Score', # Toques en área
            'AerialWon_Score',     # Aéreo
            'SCA_Score'            # Creación de tiro
        ],
        'FW_WG': [
            'DribSucc_Score',      # Regates
            'PrgDist_Score',       # Conducción progresiva
            'Gls_Score',           # Goles
            'Ast_Score',           # Asistencias
            'SCA_Score',           # Creación
            'CrsPA_Score'          # Centros al área
        ],
        'AM': [
            'SCA_Score', 
            'Ast_Score', 
            'xA_Score', 
            'KP_Score',            # Pases Clave
            'PrgDist_Score', 
            'DribSucc_Score'
        ],
        'LB_OFF': [
            'CrsPA_Score',         # Centros
            'SCA_Score', 
            'TklW_Score',          # Tackles Ganados
            'Int_Score',           # Intercepciones
            'PrgDist_Score', 
            'Ast_Score'
        ],
        'DC': [
            'AerialWon_Score', 
            'Clr_Score',           # Despejes
            'TklW_Score', 
            'Int_Score', 
            'PrgDist_Score',       # Salida de balón
            'Recov_Score'          # Recuperaciones
        ],
        'MC_DEF': [
            'TklW_Score', 
            'Int_Score', 
            'Recov_Score', 
            'Cmp%Total_Score',     # Precisión de pase
            'PrgDist_Score', 
            'AerialWon_Score'
        ],
        'FW_SS': [ # Agrego este porque Foden o Jota podrían salir aquí
            'Gls_Score',
            'xA_Score',
            'SCA_Score',
            'DribSucc_Score',
            'TouchesAtt3rd_Score',
            'SoT%_Score'
        ]
    }
    
    # Si el rol no está mapeado, usamos métricas genéricas
    cols_radar = metricas_map.get(rol_ideal, ['Gls_Score', 'Ast_Score', 'TklW_Score', 'Int_Score', 'PrgDist_Score', 'SCA_Score'])
    
    # Limpiamos los nombres para que se vean bonitos en el gráfico (quitamos "_Score")
    nombres_ejes = [c.replace('_Score', '') for c in cols_radar]

    # 3. Obtener valores del Jugador
    valores_jugador = [jugador.get(col, 50) for col in cols_radar] # 50 por defecto si falta dato
    
    # 4. Obtener el Promedio de la Posición (La "Sombra" en el radar)
    df_pos = df[df['PosAdj'] == posicion]
    valores_promedio = [df_pos[col].mean() for col in cols_radar]

    # Cerrar el círculo del radar (repetir el primer punto al final)
    valores_jugador.append(valores_jugador[0])
    valores_promedio.append(valores_promedio[0])
    nombres_ejes.append(nombres_ejes[0])

    # 5. Crear el Gráfico
    fig = go.Figure()

    # Capa 1: Promedio de la Liga (Gris de fondo)
    fig.add_trace(go.Scatterpolar(
        r=valores_promedio,
        theta=nombres_ejes,
        fill='toself',
        name=f'Promedio {posicion}',
        line_color="#510101",
        opacity=0.4
    ))

    # Capa 2: El Jugador (Verde FM)
    fig.add_trace(go.Scatterpolar(
        r=valores_jugador,
        theta=nombres_ejes,
        fill='toself',
        name=nombre_jugador,
        line_color='#00ff00' 
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100] # Los percentiles van de 0 a 100
            )
        ),
        title=f"Análisis FM: {nombre_jugador} ({rol_ideal})",
        template="plotly_dark" # Modo oscuro estilo gamer
    )
    
    fig.show()

# =============================================================================
# 2. GRÁFICO DE DISPERSIÓN (SCATTER) INTERACTIVO
# =============================================================================
def crear_dispersion_fm(posicion_filtro, eje_x, eje_y, color_por='Precio_Mercado'):
    """
    Crea un mapa de dispersión para encontrar "Gangas" o "Outliers".
    Ejemplo: Eje X = Goles, Eje Y = Valor de Mercado.
    """
    # Filtrar datos
    data = df[df['PosAdj'] == posicion_filtro].copy()
    
    # Crear gráfico interactivo
    fig = px.scatter(
        data, 
        x=eje_x, 
        y=eje_y,
        color=color_por, # El color indica el precio o rating
        size='Rating_Final', # El tamaño del punto indica qué tan bueno es
        hover_data=['Player', 'Squad', 'Age', 'Rol_Ideal', 'Valor_Intrinseco'], # Lo que sale al pasar el mouse
        text='Player', # Etiquetas de texto
        title=f"Comparativa {posicion_filtro}: {eje_x} vs {eje_y}",
        template="plotly_dark",
        color_continuous_scale='Viridis'
    )
    
    # Ajustes visuales para que se vea limpio
    fig.update_traces(textposition='top center', marker=dict(opacity=0.8, line=dict(width=1, color='White')))
    fig.update_layout(height=800) # Altura para ver bien
    
    fig.show()

# =============================================================================
# ZONA DE PRUEBAS (EJECUTA ESTO PARA VER LA MAGIA)
# =============================================================================
if __name__ == "__main__":
    # 1. Ver el Radar de una Estrella
    print("Generando Radar de Kane...")
    crear_radar_fm('Harry Kane')
    
    # 2. Ver el Radar de una "Ganga" (Thiago o Cairney)
    print("Generando Radar de Thiago...")
    crear_radar_fm('Thiago Alcántara') # Asegúrate que el nombre coincida exactamente con el Excel (tildes)

    # 3. Analizar Delanteros: ¿Quién mete goles y quién solo vive de nombre?
    # Eje X: Rating Rendimiento | Eje Y: Precio de Mercado
    # Los jugadores abajo a la derecha son GANGAS (Rinden mucho, cuestan poco)
    print("Generando Mapa de Delanteros...")
    crear_dispersion_fm('FW', 'Rating_Final', 'Precio_Mercado')
    
    # 4. Analizar Defensas: Tackles vs Intercepciones (Estilo táctico)
    # Para esto necesitamos que las columnas TklW_Score e Int_Score existan en tu CSV final.
    # Si guardaste 'df' completo en el paso anterior, funcionará. Si solo guardaste las columnas de precio, fallará.
    # (El script V5 guardaba pocas columnas, tendrías que guardar todo el DF para hacer esto).