from flask import Flask, render_template, request, jsonify
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scoutmew.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# 1. MODELOS OPTIMIZADOS
# ==========================================
class Jugador(db.Model):
    __tablename__ = 'jugadores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nacion = db.Column(db.String(10))
    edad = db.Column(db.Integer)
    club = db.Column(db.String(100))
    posicion = db.Column(db.String(10))
    minutos = db.Column(db.Integer)
    liga = db.Column(db.String(50))      
    temporada = db.Column(db.String(20)) 
    
    valoracion = db.relationship('Valoracion', backref='jugador', uselist=False)
    estadisticas = db.relationship('EstadisticasFBref', backref='jugador', uselist=False)

class Valoracion(db.Model):
    __tablename__ = 'valoraciones'
    id = db.Column(db.Integer, primary_key=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'))
    rol_principal = db.Column(db.String(20), index=True)
    rtg_principal = db.Column(db.Float, index=True)
    valor_deportivo = db.Column(db.Float)
    precio_mercado = db.Column(db.Integer) 
    
    rol_2 = db.Column(db.String(20))

class Transferencia(db.Model):
    __tablename__ = 'transferencias'
    id = db.Column(db.Integer, primary_key=True)
    jugador_nombre = db.Column(db.String(100), index=True) 
    temporada = db.Column(db.String(20))
    fecha = db.Column(db.String(20))
    club_origen = db.Column(db.String(100))
    club_destino = db.Column(db.String(100))
    coste_texto = db.Column(db.String(20))
    coste_num = db.Column(db.Integer)

class EstadisticasFBref(db.Model):
    __tablename__ = 'estadisticas_fbref'
    id = db.Column(db.Integer, primary_key=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'))
    datos_crudos = db.Column(db.JSON)

# ==========================================
# 2. RUTAS BÁSICAS
# ==========================================

@app.route('/')
def dashboard():
    temporadas_disponibles = db.session.query(Jugador.temporada).distinct().order_by(Jugador.temporada.desc()).all()
    temporadas_disponibles = [t[0] for t in temporadas_disponibles if t[0]]
    
    temporada_actual = request.args.get('temporada')
    if not temporada_actual and temporadas_disponibles:
        temporada_actual = temporadas_disponibles[0]

    total_jugadores = Jugador.query.filter_by(temporada=temporada_actual).count()
    
    valor_mercado_total = db.session.query(func.sum(Valoracion.valor_deportivo))\
        .join(Jugador).filter(Jugador.temporada == temporada_actual).scalar() or 0
    
    stats_ligas = db.session.query(
        Jugador.liga, func.avg(Valoracion.valor_deportivo).label('avg_vd')
    ).join(Valoracion).filter(Jugador.liga != None, Jugador.liga != "", Jugador.temporada == temporada_actual)\
     .group_by(Jugador.liga).order_by(func.avg(Valoracion.valor_deportivo).desc()).all()

    ids_excluidas = []
    def get_top_by_roles(lista_roles, excluidos):
        player = Jugador.query.join(Valoracion).filter(Valoracion.rol_principal.in_(lista_roles), ~Jugador.id.in_(excluidos), Jugador.temporada == temporada_actual)\
               .order_by(Valoracion.rtg_principal.desc()).first()
        if player: excluidos.append(player.id)
        return player

    top_posiciones = {
        'FW': get_top_by_roles(['FW_WG', 'FW_ST', 'FW_SS'], ids_excluidas),
        'AM': get_top_by_roles(['AM'], ids_excluidas),
        'MC': get_top_by_roles(['MC_EST', 'MC_ORG', 'MC_DEF'], ids_excluidas),
        'DF': get_top_by_roles(['DC', 'LB_OFF', 'LB_DEF'], ids_excluidas)
    }

    top_caros = Jugador.query.join(Valoracion).filter(Jugador.temporada == temporada_actual).order_by(Valoracion.valor_deportivo.desc()).limit(5).all()

    return render_template('index.html', jugadores=top_caros, total=total_jugadores, valor_total=valor_mercado_total, 
                           stats_ligas=stats_ligas, top_pos=top_posiciones, temporadas=temporadas_disponibles, temporada_actual=temporada_actual)

@app.route('/jugadores')
def players():
    # Obtener temporadas únicas de la base de datos
    temporadas_disponibles = db.session.query(Jugador.temporada).distinct().order_by(Jugador.temporada.desc()).all()
    temporadas_disponibles = [t[0] for t in temporadas_disponibles if t[0]]
    
    # Traer todos los jugadores
    todos_los_jugadores = Jugador.query.join(Valoracion)\
        .options(joinedload(Jugador.valoracion))\
        .order_by(Valoracion.rtg_principal.desc()).all()
        
    return render_template('players.html', jugadores=todos_los_jugadores, temporadas=temporadas_disponibles)

@app.route('/jugador/<int:id>')
def player_profile(id):
    jugador = Jugador.query.options(joinedload(Jugador.valoracion), joinedload(Jugador.estadisticas)).get_or_404(id)
    stats = jugador.estadisticas.datos_crudos if jugador.estadisticas else {}
    
    # ¡Cambiado! Ahora buscamos la coincidencia exacta porque la BD ya tiene el año restado
    fichaje = Transferencia.query.filter(
        Transferencia.jugador_nombre == jugador.nombre,
        Transferencia.temporada == str(jugador.temporada) 
    ).first()

    return render_template('profile.html', jugador=jugador, stats=stats, traspaso=fichaje)


# ==========================================
# 3. RUTAS DEL COMPARADOR AVANZADO
# ==========================================

def safe_float(val):
    try: return float(val)
    except (ValueError, TypeError): return 0.0

PESOS_JSON = {
   "DC": { "estadisticas": { "Defensa": {"Int": 0.20, "Clr": 0.20, "Recov": 0.20, "TklW": 0.15, "BallRec": 0.15, "TklDef3rd": 0.10}, "Aerial": {"AerialWon%": 0.60, "AerialWon": 0.40}, "Passing": {"Cmp%Total": 0.25, "PrgDist": 0.20, "Prog": 0.20, "LongCmp": 0.20, "Cmp%Long": 0.15}, "Possession": {"TouchesDef3rd": 0.45, "TouchesMid3rd": 0.25, "dispossesed": 0.30} } },
   "LB_DEF": { "estadisticas": { "Defensa": {"TklW": 0.25, "Int": 0.25, "Recov": 0.20, "Clr": 0.15, "TklDef3rd": 0.15}, "Passing": {"Cmp%Total": 0.35, "PrgDist": 0.25, "Prog": 0.25, "IntoLast3rd": 0.15}, "Possession": {"TouchesDef3rd": 0.40, "TouchesMid3rd": 0.30, "dispossesed": 0.30}, "Aerial": {"AerialWon%": 0.70, "AerialWon": 0.30} } },
   "LB_OFF": { "estadisticas": { "Passing": {"xA": 0.30, "CrsPA": 0.25, "KP": 0.20, "Prog": 0.15, "IntoLast3rd": 0.10}, "Possession": {"TouchesAtt3rd": 0.40, "PrgDist": 0.30, "DribSucc": 0.20, "dispossesed": 0.10}, "GAS": {"SCA": 0.60, "SCAPassLive": 0.40}, "Defensa": {"Recov": 0.30, "TklW": 0.30, "Int": 0.25, "BallRec": 0.15} } },
   "MC_DEF": { "estadisticas": { "Defensa": {"Int": 0.25, "Recov": 0.25, "TklW": 0.15, "BallRec": 0.10, "BallRecProg": 0.10, "TklMid3rd": 0.10, "Tkl": 0.05}, "Passing": {"Cmp%Total": 0.35, "ShortCmp": 0.15, "Cmp%Short": 0.15, "MediumCmp": 0.10, "Prog": 0.10, "PrgDist": 0.10, "LongCmp": 0.05}, "Possession": {"dispossesed": 0.40, "TouchesMid3rd": 0.30, "TouchesDef3rd": 0.20, "BallRec": 0.10}, "Aerial": {"AerialWon%": 1.00}, "GAS": {"SCA": 0.50, "SCAPassLive": 0.50}, "Shooting": {"Gls": 1.0} } },
   "MC_ORG": { "estadisticas": { "Passing": {"Prog": 0.20, "PrgDist": 0.20, "IntoLast3rd": 0.15, "Cmp%Total": 0.15, "KP": 0.10, "LongCmp": 0.10, "xA": 0.05, "xAG": 0.05}, "Possession": {"PrgDist": 0.30, "TouchesMid3rd": 0.20, "TouchesLive": 0.15, "dispossesed": 0.12, "DribSucc": 0.13, "TouchesDef3rd": 0.10}, "Defensa": {"Recov": 0.35, "Int": 0.30, "BallRec": 0.20, "TklMid3rd": 0.15}, "GAS": {"SCA": 0.60, "SCAPassLive": 0.40}, "Aerial": {"AerialWon%": 1.0}, "Shooting": {"Gls": 0.50, "npxG/Sh": 0.50} } },
   "MC_EST": { "estadisticas": { "Passing": {"Prog": 0.15, "IntoLast3rd": 0.15, "PrgDist": 0.15, "xA": 0.15, "Cmp%Total": 0.10, "KP": 0.10, "PPA": 0.10, "Ast": 0.10}, "Defensa": {"Recov": 0.25, "TklMid3rd": 0.20, "TklW": 0.20, "Int": 0.15, "BallRec": 0.10, "BallRecProg": 0.10}, "Possession": {"TouchesMid3rd": 0.20, "TouchesAtt3rd": 0.15, "TouchesDef3rd": 0.15, "PrgDist": 0.15, "TouchesAttPen": 0.10, "DribSucc": 0.10, "dispossesed": 0.10, "BallRecProg": 0.05}, "GAS": {"SCA": 0.35, "SCAPassLive": 0.30, "GCA": 0.20, "SCADef": 0.10, "SCADrib": 0.05}, "Aerial": {"AerialWon%": 0.60, "AerialWon": 0.40}, "Shooting": {"Gls": 0.30, "npxG": 0.25, "G-xG": 0.20, "xG": 0.15, "SoT%": 0.10} } },
   "AM": { "estadisticas": { "Passing": {"xAG": 0.20, "xA": 0.20, "KP": 0.20, "PPA": 0.15, "Prog": 0.15, "IntoLast3rd": 0.10}, "GAS": {"SCA": 0.30, "SCAPassLive": 0.30, "GCA": 0.20, "SCAPassDead": 0.10, "SCADrib": 0.10}, "Shooting": {"Gls": 0.30, "npxG": 0.30, "np:G-xG": 0.20, "npxG/Sh": 0.20}, "Possession": {"TouchesAtt3rd": 0.50, "TouchesAttPen": 0.50} } },
   "FW_WG": { "estadisticas": { "Possession": {"DribSucc": 0.40, "PrgDist": 0.40, "TouchesAtt3rd": 0.20}, "GAS": {"SCADrib": 0.60, "GCA": 0.30, "SCAFld": 0.10}, "Passing": {"CrsPA": 0.50, "xAG": 0.30, "IntoLast3rd": 0.20}, "Shooting": {"Gls": 0.50, "npxG": 0.50} } },
   "FW_ST": { "estadisticas": { "Shooting": {"Gls": 0.40, "npxG": 0.30, "np:G-xG": 0.20, "npxG/Sh": 0.10}, "GAS": {"GCA": 0.50, "SCA": 0.50}, "Aerial": {"AerialWon": 0.50, "AerialWon%": 0.50}, "Passing": {"xA": 0.50, "Ast": 0.50} } },
   "FW_SS": { "estadisticas": { "Shooting": {"Gls": 0.40, "npxG": 0.40, "npxG/Sh": 0.20}, "GAS": {"SCA": 0.50, "SCAPassLive": 0.50}, "Passing": {"PPA": 0.40, "KP": 0.30, "xA": 0.30}, "Possession": {"TouchesAttPen": 0.70, "DribSucc": 0.30} } }
}

NOMBRES_STATS = {
    "Int": "Intercepciones", "Clr": "Despejes", "Recov": "Recuperaciones", "TklW": "Tackles Ganados",
    "BallRec": "Balones Rec.", "TklDef3rd": "Tackles Def 3º", "AerialWon%": "% Duelos Aéreos",
    "AerialWon": "Aéreos Ganados", "Cmp%Total": "% Pases Comp.", "PrgDist": "Dist. Progresiva",
    "Prog": "Pases Progresivos", "LongCmp": "Pases Largos Comp.", "Cmp%Long": "% Pases Largos",
    "TouchesDef3rd": "Toques Def 3º", "TouchesMid3rd": "Toques Med 3º", "dispossesed": "Pérdidas (Inverso)",
    "IntoLast3rd": "Pases Últ. 3º", "xA": "Asist. Esperadas (xA)", "CrsPA": "Centros al Área",
    "KP": "Pases Clave", "TouchesAtt3rd": "Toques Ataque 3º", "DribSucc": "Regates Exitosos",
    "SCA": "Creación (SCA)", "SCAPassLive": "SCA (Pase Vivo)", "BallRecProg": "Recup. Progresivas",
    "TklMid3rd": "Tackles Med 3º", "Tkl": "Tackles Totales", "ShortCmp": "Pases Cortos",
    "Cmp%Short": "% Pases Cortos", "MediumCmp": "Pases Medios", "Gls": "Goles/90",
    "xAG": "Peligro Gen. (xAG)", "TouchesLive": "Toques Vivos", "PPA": "Pases al Área",
    "Ast": "Asistencias", "TouchesAttPen": "Toques Área Rival", "GCA": "Acciones Gol (GCA)",
    "SCADef": "SCA (Defensa)", "SCADrib": "SCA (Regate)", "npxG": "Goles Esp. (npxG)",
    "G-xG": "Rend. Goles (G-xG)", "xG": "Goles Esp. (xG)", "SoT%": "% Tiros a Puerta",
    "SCAPassDead": "SCA (Balón Parado)", "np:G-xG": "Rend. Sin Penal", "npxG/Sh": "Calidad Tiro (npxG/Sh)",
    "SCAFld": "SCA (Falta Recibida)"
}

@app.route('/comparar')
def compare():
    temporadas = [t[0] for t in db.session.query(Jugador.temporada).distinct().order_by(Jugador.temporada.desc()).all() if t[0]]
    stats_list = [{'key': k, 'name': v} for k, v in NOMBRES_STATS.items()]
    stats_list = sorted(stats_list, key=lambda x: x['name'])
    return render_template('compare.html', temporadas=temporadas, stats_list=stats_list)

@app.route('/api/scatter_data')
def api_scatter_data():
    temporada = request.args.get('temporada', '')
    stat_x = request.args.get('x', 'npxG')
    stat_y = request.args.get('y', 'Gls')
    rol_filter = request.args.get('rol', 'ALL')
    min_minutos = int(request.args.get('minutos', 500))

    query = Jugador.query.join(Valoracion).join(EstadisticasFBref).filter(
        Jugador.temporada == temporada,
        Jugador.minutos >= min_minutos
    )

    if rol_filter != 'ALL':
        if rol_filter == 'DF': query = query.filter(Valoracion.rol_principal.in_(['DC', 'LB_DEF', 'LB_OFF']))
        elif rol_filter == 'MC': query = query.filter(Valoracion.rol_principal.in_(['MC_DEF', 'MC_ORG', 'MC_EST']))
        elif rol_filter == 'AM': query = query.filter(Valoracion.rol_principal == 'AM')
        elif rol_filter == 'FW': query = query.filter(Valoracion.rol_principal.in_(['FW_WG', 'FW_ST', 'FW_SS']))

    jugadores = query.options(joinedload(Jugador.valoracion), joinedload(Jugador.estadisticas)).all()

    data = []
    for j in jugadores:
        st = j.estadisticas.datos_crudos if j.estadisticas else {}
        val_x = safe_float(st.get(stat_x, 0))
        val_y = safe_float(st.get(stat_y, 0))
        
        if val_x == 0 and val_y == 0: continue
            
        data.append({
            'id': j.id,
            'nombre': j.nombre,
            'club': j.club,
            'rol': j.valoracion.rol_principal if j.valoracion else 'N/A',
            'rtg': round(j.valoracion.rtg_principal, 1) if j.valoracion else 0,
            'x': val_x,
            'y': val_y
        })

    return jsonify(data)

@app.route('/api/buscar_jugador')
def api_buscar_jugador():
    query = request.args.get('q', '').lower()
    temporada = request.args.get('temporada', '')
    rol_exacto = request.args.get('rol_exacto', '') # Captura la restricción de rol
    
    if len(query) < 2: return jsonify([])
    
    q_filter = Jugador.query.join(Valoracion).filter(
        func.lower(Jugador.nombre).contains(query), 
        Jugador.temporada == temporada
    )
    
    # Si ya hay un jugador seleccionado, filtramos el buscador
    if rol_exacto:
        q_filter = q_filter.filter(Valoracion.rol_principal == rol_exacto)
        
    jugadores = q_filter.limit(8).all()
    resultados = [{'id': j.id, 'nombre': j.nombre, 'club': j.club, 'temporada': j.temporada, 'rol': j.valoracion.rol_principal if j.valoracion else 'N/A'} for j in jugadores]
    return jsonify(resultados)

@app.route('/api/rivales_similares/<int:id>')
def api_rivales_similares(id):
    jugador = Jugador.query.options(joinedload(Jugador.valoracion)).get_or_404(id)
    temp = jugador.temporada
    rol = jugador.valoracion.rol_principal if jugador.valoracion else 'MC'
    
    rivales = Jugador.query.join(Valoracion).filter(
        Jugador.temporada == temp, 
        Valoracion.rol_principal == rol,
        Jugador.id != id
    ).order_by(Valoracion.rtg_principal.desc()).all() # <-- Eliminado el límite
    
    return jsonify([{
        'id': r.id,
        'nombre': r.nombre,
        'club': r.club,
        'rtg': round(r.valoracion.rtg_principal, 1) if r.valoracion else 0
    } for r in rivales])

@app.route('/api/radar_contexto/<int:id>')
def api_radar_contexto(id):
    jugador = Jugador.query.options(joinedload(Jugador.estadisticas), joinedload(Jugador.valoracion)).get_or_404(id)
    temp = jugador.temporada
    rol = jugador.valoracion.rol_principal if jugador.valoracion else 'MC'
    plantilla_solicitada = request.args.get('plantilla', 'completo')
    
    rivales = Jugador.query.join(Valoracion).filter(Jugador.temporada == temp, Valoracion.rol_principal == rol).all()
    
    mejor_jugador = max(rivales, key=lambda j: j.valoracion.rtg_principal if j.valoracion else 0) if rivales else None
    stats_mejor = mejor_jugador.estadisticas.datos_crudos if mejor_jugador and mejor_jugador.estadisticas else {}
    nombre_mejor = mejor_jugador.nombre if mejor_jugador else "N/A"

    jugador_st = jugador.estadisticas.datos_crudos if jugador.estadisticas else {}
    prefijo = rol.split('_')[0] if '_' in rol else rol

    # ESTRUCTURA MAESTRA: Definimos todas las configuraciones aquí. 
    # Si el prefijo no existe, usamos 'MC' como estándar seguro.
    ALL_PLANTILLAS = {
        'FW': {
            'completo': {'keys': ['Gls', 'npxG', 'Ast', 'xA', 'SoT', 'KP'], 'labels': ['Goles', 'npxG', 'Asistencias', 'xA', 'Tiros Puerta', 'Pases Clave']},
            'opcion1': {'keys': ['Gls', 'npxG', 'SoT', 'SoT%', 'G/Sh'], 'labels': ['Goles', 'npxG', 'Tiros Puerta', '% Tiros Puerta', 'Goles/Tiro']},
            'opcion2': {'keys': ['Ast', 'xA', 'KP', 'Prog', 'SCA'], 'labels': ['Asistencias', 'xA', 'Pases Clave', 'Pases Prog', 'Creación (SCA)']}
        },
        'MC': {
            'completo': {'keys': ['Prog', 'SCA', 'KP', 'TklW', 'Int', 'Cmp%Total'], 'labels': ['Pases Prog', 'SCA', 'Pases Clave', 'Tackles', 'Intercepciones', '% Pase']},
            'opcion1': {'keys': ['SCA', 'xA', 'KP', 'PPA', 'Ast'], 'labels': ['Creación (SCA)', 'xA', 'Pases Clave', 'Pases Área', 'Asistencias']},
            'opcion2': {'keys': ['TklW', 'Int', 'Recov', 'BallRec', 'Clr'], 'labels': ['Tackles', 'Intercepciones', 'Recuperaciones', 'Balones Rec.', 'Despejes']}
        },
        'AM': {
            'completo': {'keys': ['Prog', 'SCA', 'KP', 'TklW', 'Int', 'Cmp%Total'], 'labels': ['Pases Prog', 'SCA', 'Pases Clave', 'Tackles', 'Intercepciones', '% Pase']},
            'opcion1': {'keys': ['SCA', 'xA', 'KP', 'PPA', 'Ast'], 'labels': ['Creación (SCA)', 'xA', 'Pases Clave', 'Pases Área', 'Asistencias']},
            'opcion2': {'keys': ['TklW', 'Int', 'Recov', 'BallRec', 'Clr'], 'labels': ['Tackles', 'Intercepciones', 'Recuperaciones', 'Balones Rec.', 'Despejes']}
        },
        'DF': {
            'completo': {'keys': ['TklW', 'Int', 'Clr', 'AerialWon%', 'Prog', 'Recov'], 'labels': ['Tackles', 'Intercepciones', 'Despejes', 'Aéreo %', 'Pases Prog', 'Recuperaciones']},
            'opcion1': {'keys': ['Prog', 'PrgDist', 'Cmp%Total', 'KP', 'IntoLast3rd'], 'labels': ['Pases Prog', 'Dist. Prog', '% Pase', 'Pases Clave', 'Pases Últ. 3º']},
            'opcion2': {'keys': ['TklW', 'Int', 'Clr', 'AerialWon%', 'BallRec'], 'labels': ['Tackles', 'Intercepciones', 'Despejes', 'Aéreo %', 'Balones Rec.']}
        }
    }

    # Lógica de respaldo infalible
    config_rol = ALL_PLANTILLAS.get(prefijo, ALL_PLANTILLAS['MC'])
    template = config_rol.get(plantilla_solicitada, config_rol['completo'])
    
    keys = template['keys']
    labels = template['labels']

    def calc_stats_block(keys_list, labels_list):
        bloque = []
        for k, label in zip(keys_list, labels_list):
            val_jugador = safe_float(jugador_st.get(k, 0))
            val_mejor = safe_float(stats_mejor.get(k, 0))
            lista_rivales = [safe_float((r.estadisticas.datos_crudos.get(k, 0) if r.estadisticas else 0)) for r in rivales]
                
            perc = (sum(i < val_jugador for i in lista_rivales) / len(lista_rivales) * 100) if lista_rivales else 0
            perc_mejor = (sum(i < val_mejor for i in lista_rivales) / len(lista_rivales) * 100) if lista_rivales else 0
            val_promedio = np.mean(lista_rivales) if lista_rivales else 0
                
            # ... dentro del bucle de calc_stats_block ...
            bloque.append({
                'key': k, # ESTO ES LO QUE NECESITA EL JS PARA BUSCAR
                'label': label, 
                'raw_jugador': val_jugador, 'perc_jugador': round(perc, 1),
                'raw_promedio': round(val_promedio, 2), 
                'raw_mejor': round(val_mejor, 2), 'perc_mejor': round(perc_mejor, 1),
                'nombre_mejor': nombre_mejor
            })
        return bloque

    radar_stats = calc_stats_block(keys, labels)
    
    role_dict = PESOS_JSON.get(rol, PESOS_JSON.get('MC_ORG')) 
    role_keys = []
    for cat, stats in role_dict['estadisticas'].items():
        role_keys.extend(stats.keys())
    role_labels = [NOMBRES_STATS.get(k, k) for k in role_keys]
    tabla_roles_stats = calc_stats_block(role_keys, role_labels)

    return jsonify({
        'nombre': jugador.nombre, 'club': jugador.club, 'rol': rol, 'prefijo_rol': prefijo, 
        'poblacion': len(rivales), 'stats': radar_stats, 'role_stats': tabla_roles_stats
    })

if __name__ == '__main__':
    app.run(debug=True)