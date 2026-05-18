import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =============================================================================
st.set_page_config(page_title="Premier League Scout Pro 2021", layout="wide", page_icon="⚽")

# Estilos CSS Pro (Modo Oscuro Elegante)
st.markdown("""
<style>
    .metric-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #0e1117; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #262730; color: #00ff00; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #00ff00; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. CARGA DE DATOS
# =============================================================================
@st.cache_data
def cargar_datos():
    archivo = 'Premier_Valuation_Model_V5_Final.csv'
    if not os.path.exists(archivo):
        return None
    return pd.read_csv(archivo)

df = cargar_datos()

if df is None:
    st.error("❌ No encuentro el archivo de datos. Ejecuta primero el script de valoración.")
    st.stop()

# =============================================================================
# 3. MAPEO DE MÉTRICAS Y PRESETS
# =============================================================================
METRICAS_DISPLAY = {
    'Goles': 'Gls', 'Asistencias': 'Ast', 'Goles Esperados (xG)': 'xG', 'Asistencias Esperadas (xA)': 'xA',
    'Tiros Totales': 'Sh', 'Creación de Tiro (SCA)': 'SCA', 'Pases Clave': 'KP', 'Regates Exitosos': 'DribSucc',
    'Toques en Área Rival': 'TouchesAttPen', 'Pases Progresivos': 'Prog', 'Tackles Ganados': 'TklW',
    'Intercepciones': 'Int', 'Recuperaciones': 'Recov', 'Duelos Aéreos Ganados': 'AerialWon',
    'Valor de Mercado': 'Precio_Mercado', 'Rating General': 'Rating_Final', 'Centros al Área': 'CrsPA',
    'Distancia Progresiva': 'PrgDist', ' % Pase Total': 'Cmp%Total'
}
METRICAS_REALES = {v: k for k, v in METRICAS_DISPLAY.items()}

# Definición de Roles para Radar
METRICAS_RADAR = {
    'FW_ST': ['Gls_Score', 'xG_Score', 'Sh_Score', 'TouchesAttPen_Score', 'AerialWon_Score', 'SCA_Score'],
    'FW_WG': ['DribSucc_Score', 'PrgDist_Score', 'Gls_Score', 'Ast_Score', 'SCA_Score', 'CrsPA_Score'],
    'AM':    ['SCA_Score', 'Ast_Score', 'xA_Score', 'KP_Score', 'PrgDist_Score', 'DribSucc_Score'],
    'LB_OFF':['CrsPA_Score', 'SCA_Score', 'TklW_Score', 'Int_Score', 'PrgDist_Score', 'Ast_Score'],
    'DC':    ['AerialWon_Score', 'Clr_Score', 'TklW_Score', 'Int_Score', 'PrgDist_Score', 'Recov_Score'],
    'MC_DEF':['TklW_Score', 'Int_Score', 'Recov_Score', 'Cmp%Total_Score', 'PrgDist_Score', 'AerialWon_Score'],
    'FW_SS': ['Gls_Score', 'xA_Score', 'SCA_Score', 'DribSucc_Score', 'TouchesAtt3rd_Score', 'SoT%_Score']
}

# Presets Tácticos COMPLETOS
PRESETS_TACTICOS = {
    'DC': {
        '🛡️ El Muro (Solidez)': {'x': 'TklW', 'y': 'Int'},
        '⚽ Salida de Balón': {'x': 'PrgDist', 'y': 'Cmp%Total'},
        '✈️ Dominio Aéreo': {'x': 'AerialWon', 'y': 'AerialWon%'}
    },
    'LB_OFF': {
        '🚀 Amenaza Ofensiva': {'x': 'SCA', 'y': 'CrsPA'},
        '🏃‍♂️ Recorrido': {'x': 'PrgDist', 'y': 'TouchesAtt3rd'}
    },
    'MC_DEF': {
        '🛡️ El Ancla': {'x': 'TklW', 'y': 'Int'},
        '🎯 Distribución': {'x': 'Cmp%Total', 'y': 'PrgDist'},
        '🧹 Limpieza': {'x': 'Recov', 'y': 'TklW'}
    },
    'AM': {
        '🎨 El Creativo': {'x': 'KP', 'y': 'xA'},
        '⚡ Conducción': {'x': 'PrgDist', 'y': 'DribSucc'},
        '🎯 Doble Amenaza': {'x': 'Gls', 'y': 'Ast'}
    },
    'FW_WG': {
        '💨 Desborde': {'x': 'DribSucc', 'y': 'CrsPA'},
        '🔫 Extremo Goleador': {'x': 'Gls', 'y': 'xG'},
        '🧠 Playmaker': {'x': 'SCA', 'y': 'PrgDist'}
    },
    'FW_ST': {
        '🎯 El Killer (Eficacia)': {'x': 'xG', 'y': 'Gls'},
        '🦊 Depredador': {'x': 'TouchesAttPen', 'y': 'Sh'},
        '🧱 Juego Aéreo': {'x': 'AerialWon', 'y': 'SCA'}
    }
}

# =============================================================================
# 4. FUNCIONES GRÁFICAS MEJORADAS
# =============================================================================

def plot_radar(jugador_row):
    nombre = jugador_row['Player']
    rol = jugador_row['Rol_Ideal']
    pos = jugador_row['PosAdj']
    
    cols = METRICAS_RADAR.get(rol, METRICAS_RADAR['AM'])
    labels = [c.replace('_Score', '') for c in cols]
    
    values_player = [jugador_row.get(c, 50) for c in cols]
    values_player.append(values_player[0])
    
    promedio = df[df['PosAdj'] == pos][cols].mean().tolist()
    promedio.append(promedio[0])
    labels.append(labels[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=promedio, theta=labels, fill='toself', name=f'Media {pos}', line_color="#555555", opacity=0.3))
    fig.add_trace(go.Scatterpolar(r=values_player, theta=labels, fill='toself', name=nombre, line_color='#00ff00', opacity=0.7))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=350, margin=dict(t=20, b=20, l=40, r=40))
    return fig

def plot_barras_percentiles(jugador_row):
    rol = jugador_row['Rol_Ideal']
    cols = METRICAS_RADAR.get(rol, METRICAS_RADAR['AM'])
    data = {'Métrica': [c.replace('_Score', '') for c in cols], 'Percentil': [jugador_row.get(c, 0) for c in cols]}
    df_bar = pd.DataFrame(data).sort_values('Percentil', ascending=True)
    
    fig = px.bar(df_bar, x='Percentil', y='Métrica', orientation='h', text='Percentil',
                 color='Percentil', color_continuous_scale=['#ff4b4b', '#ffff4b', '#4bff4b'], range_color=[0,100])
    fig.update_layout(xaxis_range=[0, 100], height=350, showlegend=False, xaxis_title="", yaxis_title="")
    return fig

def plot_scatter_dinamico(df_filtrado, x_col, y_col, jugador_destacado):
    """
    Scatter Plot PRO: Puntos pequeños para ver la densidad, estrella grande para el jugador.
    """
    # 1. Crear la figura base con puntos pequeños
    fig = px.scatter(
        df_filtrado, 
        x=x_col, 
        y=y_col,
        color='Squad', # Colores por equipo para identificar
        hover_data=['Player', 'Age', 'Precio_Mercado'],
        title=f"{METRICAS_REALES.get(x_col, x_col)} vs {METRICAS_REALES.get(y_col, y_col)}"
    )
    
    # 2. Modificar trazas: Hacer los puntos pequeños y algo transparentes
    fig.update_traces(marker=dict(size=8, opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey')))
    
    # 3. Destacar Jugador (Estrella Roja Grande)
    df_jugador = df_filtrado[df_filtrado['Player'] == jugador_destacado]
    if not df_jugador.empty:
        fig.add_trace(go.Scatter(
            x=df_jugador[x_col], 
            y=df_jugador[y_col],
            mode='markers+text',
            marker=dict(color='red', size=18, symbol='star', line=dict(width=2, color='white')),
            name=jugador_destacado,
            text=[jugador_destacado],
            textposition="top center",
            textfont=dict(size=14, color="white")
        ))
    
    fig.update_layout(height=600, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

# =============================================================================
# 5. INTERFAZ VISUAL
# =============================================================================

# --- SIDEBAR ---
st.sidebar.title("🕵️‍♂️ Scout Pro 2021")
st.sidebar.info("Herramienta de Análisis de Mercado y Rendimiento")

posiciones = sorted(df['PosAdj'].unique())
pos_select = st.sidebar.selectbox("Posición:", ["Todos"] + posiciones, index=0)

equipos = sorted(df['Squad'].unique())
equipo_select = st.sidebar.selectbox("Equipo:", ["Todos"] + equipos)

# Aplicar Filtros
df_filtrado = df.copy()
if pos_select != "Todos": df_filtrado = df_filtrado[df_filtrado['PosAdj'] == pos_select]
if equipo_select != "Todos": df_filtrado = df_filtrado[df_filtrado['Squad'] == equipo_select]

jugadores = sorted(df_filtrado['Player'].unique())
if not jugadores:
    st.error("No hay jugadores con esos filtros.")
    st.stop()
    
jugador_select = st.sidebar.selectbox("👤 Seleccionar Jugador:", jugadores)
jugador_data = df[df['Player'] == jugador_select].iloc[0]

# --- MAIN PAGE ---

# Encabezado Compacto
c1, c2 = st.columns([1, 6])
with c2:
    st.title(f"{jugador_data['Player']}")
    st.caption(f"**{jugador_data['Squad']}** | {jugador_data['Age']} Años | {jugador_data['PosAdj']} ({jugador_data['Rol_Ideal']})")

# KPIs en Fila
k1, k2, k3, k4 = st.columns(4)
k1.metric("Rating", f"{jugador_data['Rating_Final']:.1f}")
k2.metric("Precio Mercado", f"€ {jugador_data['Precio_Mercado']:.1f} M")
k3.metric("Valor Intrínseco", f"€ {jugador_data['Valor_Intrinseco']:.1f} M", 
          delta=round(jugador_data['Valor_Intrinseco'] - jugador_data['Precio_Mercado'], 1))
diff = jugador_data['Valor_Rendimiento_Puro'] - jugador_data['Precio_Mercado']
k4.metric("Estado", jugador_data['Estado_Mercado'])

st.markdown("---")

# TABS PRINCIPALES
tabs = st.tabs(["📊 Perfil", "🔎 Análisis Táctico", "🆚 Comparador", "📋 Datos"])

# TAB 1: PERFIL
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Radar de Habilidades")
        st.plotly_chart(plot_radar(jugador_data), use_container_width=True)
    with col2:
        st.subheader("Percentiles Clave")
        st.plotly_chart(plot_barras_percentiles(jugador_data), use_container_width=True)

# TAB 2: ANÁLISIS TÁCTICO
with tabs[1]:
    col_control, col_grafico = st.columns([1, 3])
    
    with col_control:
        st.markdown("### Configuración")
        rol_jugador = jugador_data['Rol_Ideal']
        presets = PRESETS_TACTICOS.get(rol_jugador, {})
        
        modo_analisis = st.radio("Modo:", ["Presets Tácticos", "Manual"])
        
        col_x_real, col_y_real = None, None
        
        if modo_analisis == "Presets Tácticos":
            if presets:
                preset_select = st.selectbox("Escenario:", list(presets.keys()))
                eje_x = presets[preset_select]['x']
                eje_y = presets[preset_select]['y']
                col_x_real = METRICAS_DISPLAY.get(eje_x, eje_x)
                col_y_real = METRICAS_DISPLAY.get(eje_y, eje_y)
                st.info(f"Comparando: {eje_x} vs {eje_y}")
            else:
                st.warning("Sin presets para este rol.")
        else:
            eje_x = st.selectbox("Eje X:", list(METRICAS_DISPLAY.keys()), index=0)
            eje_y = st.selectbox("Eje Y:", list(METRICAS_DISPLAY.keys()), index=2)
            col_x_real = METRICAS_DISPLAY[eje_x]
            col_y_real = METRICAS_DISPLAY[eje_y]

    with col_grafico:
        if col_x_real and col_y_real:
            if col_x_real in df_filtrado.columns and col_y_real in df_filtrado.columns:
                st.plotly_chart(plot_scatter_dinamico(df_filtrado, col_x_real, col_y_real, jugador_select), use_container_width=True)
            else:
                st.error("Datos no disponibles para estas métricas.")

# TAB 3: COMPARADOR
with tabs[2]:
    c_sel1, c_sel2 = st.columns(2)
    with c_sel1:
        jug_a = st.selectbox("Jugador A (Verde):", jugadores, index=jugadores.index(jugador_select), key='j_a')
    with c_sel2:
        lista_b = [j for j in jugadores if j != jug_a]
        jug_b = st.selectbox("Jugador B (Rojo):", lista_b, index=0, key='j_b')
    
    data_a = df[df['Player'] == jug_a].iloc[0]
    data_b = df[df['Player'] == jug_b].iloc[0]
    
    c_rad_comp, c_dat_comp = st.columns([1, 1])
    
    with c_rad_comp:
        rol_ref = data_a['Rol_Ideal']
        cols = METRICAS_RADAR.get(rol_ref, METRICAS_RADAR['AM'])
        labels = [c.replace('_Score', '') for c in cols]
        
        vals_a = [data_a.get(c, 50) for c in cols]; vals_a.append(vals_a[0])
        vals_b = [data_b.get(c, 50) for c in cols]; vals_b.append(vals_b[0])
        labels.append(labels[0])
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatterpolar(r=vals_a, theta=labels, fill='toself', name=jug_a, line_color='#00ff00', opacity=0.4))
        fig_comp.add_trace(go.Scatterpolar(r=vals_b, theta=labels, fill='toself', name=jug_b, line_color='#ff0000', opacity=0.4))
        fig_comp.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, margin=dict(t=30, b=30))
        st.plotly_chart(fig_comp, use_container_width=True)
        
    with c_dat_comp:
        st.markdown("### Comparativa Directa")
        comp_df = pd.DataFrame({
            'Métrica': ['Edad', 'Rating', 'Precio', 'Valor Real', 'Estado'],
            jug_a: [data_a['Age'], f"{data_a['Rating_Final']:.1f}", f"€{data_a['Precio_Mercado']}M", f"€{data_a['Valor_Intrinseco']}M", data_a['Estado_Mercado']],
            jug_b: [data_b['Age'], f"{data_b['Rating_Final']:.1f}", f"€{data_b['Precio_Mercado']}M", f"€{data_b['Valor_Intrinseco']}M", data_b['Estado_Mercado']]
        }).set_index('Métrica')
        st.table(comp_df)

# TAB 4: DATOS RAW
with tabs[3]:
    st.dataframe(jugador_data.to_frame().T)