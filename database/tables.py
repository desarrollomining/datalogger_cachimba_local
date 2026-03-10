# Definición de las tablas de la base de datos
TABLES = {
    'flow_data': {
        'id'             : 'INTEGER PRIMARY KEY   AUTOINCREMENT',
        'flow_avg'       : 'FLOAT',
        'volume_min'     : 'FLOAT',
        'volume_max'     : 'FLOAT',
        'packet_data'    : 'TEXT',
        'timestamp'      : 'INTEGER',
        'datetime'       : 'DATETIME',
        'uploaded_mining': 'INTEGER NOT NULL DEFAULT 0'
        },
    'energy_data': {
        'id'             : 'INTEGER PRIMARY KEY   AUTOINCREMENT',
        'bat_v'          : 'FLOAT',
        'pv_v'           : 'FLOAT',
        'pv_i'           : 'FLOAT',
        'timestamp'      : 'INTEGER',
        'datetime'       : 'DATETIME',
        'uploaded_mining': 'INTEGER NOT NULL DEFAULT 0'
        },
    'state_button_data': {
        'id'                : 'INTEGER PRIMARY KEY   AUTOINCREMENT',
        "regador"           : 'TEXT',
        "cargar_agua"       : 'BOOLEAN',
        "cargar_surfactante": 'BOOLEAN',
        "detener"           : 'BOOLEAN',
        'timestamp'         : 'INTEGER',
        'datetime'          : 'DATETIME',
        'uploaded_mining'   : 'INTEGER NOT NULL DEFAULT 0'
    },
     'level_data': {
         'id'             : 'INTEGER PRIMARY KEY   AUTOINCREMENT',
         'level_avg'     : 'FLOAT',
         'timestamp'      : 'INTEGER',
         'datetime'       : 'DATETIME',
         'uploaded_mining': 'INTEGER NOT NULL DEFAULT 0'
    },
    'turno': {
        'id'            : 'INTEGER PRIMARY KEY   AUTOINCREMENT',
        'volumen_m3'    : 'FLOAT',
        'cargas_agua'   : 'INTEGER',
        'cargas_surfactante': 'INTEGER',
        'reg_1_agua'   : 'INTEGER',
        'reg_1_surf'   : 'INTEGER',
        'reg_2_agua'   : 'INTEGER',
        'reg_2_surf'   : 'INTEGER',
        'reg_3_agua'   : 'INTEGER',
        'reg_3_surf'   : 'INTEGER',
        'timestamp'      : 'INTEGER',
        'datetime'       : 'DATETIME',
        'uploaded_mining': 'INTEGER NOT NULL DEFAULT 0'
    }
}
