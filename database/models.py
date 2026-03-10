import os
import sys
import sqlite3
import argparse
import traceback
from tabulate import tabulate
from datetime import datetime, timedelta

sys.path.append('/srv/datalogger_cachimba/')
from lib.utils import Utils
from database import tables

class Database(Utils):
    def __init__(self, log_id= "DATABASE" ):
        self.log_id = log_id
        self.database_path = "/srv/datalogger_cachimba/database/database.db"
        self.backup_database_path = "/srv/datalogger_cachimba/database/backup"

    # Función para verificar la conexión a la base de datos
    def check_database(self):
        #TODO: Add check if file is empty
        """
        Verifica si se puede abrir la base de datos SQLite.

        Args:
            database_path (str): Ruta de la base de datos.

        Returns:
            None
        """
        try:
            if not os.path.isfile(self.database_path):
                with sqlite3.connect(database=self.database_path) as conn:
                    print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)
            
    # Función para crear tablas en la base de datos
    def create_tables(self, dict_tables: dict):
        """
        Crea las tablas especificadas en la base de datos si no existen.

        Args:
            dict_tables (dict): Diccionario con las definiciones de las tablas y sus columnas.

        Returns:
            None
        """
        conn = sqlite3.connect(self.database_path, timeout=10.0)
        c = conn.cursor()

        for table in dict_tables.keys():
            fieldset = []
            for col, definition in dict_tables[table].items():
                fieldset.append("'{0}' {1}".format(col, definition))
            print(fieldset)
            if len(fieldset) > 0:
                query = "CREATE TABLE IF NOT EXISTS {0} ({1})".format(table, ", ".join(fieldset))
                c.execute(query)

        c.close()
        conn.close()

    # Función para reiniciar la base de datos (placeholder)
    def reset_database(self):
        """
        Placeholder para la lógica de reinicio de la base de datos.
        """
        try:
            self.log("REINICIANDO DATABASE")
            # 1. BACKUP DB
            now = datetime.now()
            backup_db_cmd = f"cp {self.database_path} {self.backup_database_path}/database_{now.strftime('%Y-%m-%d#%H:%M:%S')}.db"
            self.command(backup_db_cmd)

            # 2. DELETE DB FILE
            delete_db_cmd = f"sudo rm {self.database_path}"
            self.command(delete_db_cmd)

            # 3. CREATE TABLES
            create_tables_cmd = "python3 /srv/datalogger_cachimba/database/models.py --create_database true"
            self.command(create_tables_cmd)
        except:
            self.traceback()

    # === FLOW ===#
    def get_flow_data(self, columns="", condition_column = "", limit=10):
        """
        Obtiene datos de la base de datos, con la opción de especificar columnas y un límite.

        Args:
            database_path (str): Ruta de la base de datos.
            columns (str): Columnas personalizadas a seleccionar (por defecto, selecciona todas las relevantes).
            limit (int): Límite de filas a devolver.

        Returns:
            list: Lista de filas obtenidas de la base de datos.
        """
        rows, col_name = None, ""
        try:
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cur = conn.cursor()

            if condition_column:
                query = f"""SELECT id, packet_data, datetime, timestamp FROM flow_data WHERE {condition_column}=0 order by id desc limit 10"""
            else:
                if columns:
                    query = f"SELECT id, {columns} FROM flow_data order by id desc limit {limit}"
                else:
                    query = f"SELECT id, flow_avg, volume_min, volume_max, datetime, timestamp, uploaded_mining FROM flow_data order by id desc limit {limit}"
                    #query = f"SELECT datetime, MIN(volume_min) FROM flow_data"
            print(query)
            cur.execute(query)
            rows = cur.fetchall()
            col_name = [i[0] for i in cur.description]
            conn.close()
        except:
            self.traceback()
        return rows, col_name
    
        # === FLOW ===#
    def get_flow_data_date(self, start_date, end_date):
        """
        Obtiene datos de la base de datos, con la opción de rango de fechas en timestamp

        Args:
            database_path (str): Ruta de la base de datos.

        Returns:
            list: Lista de filas obtenidas de la base de datos.
        """
        try:
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cur = conn.cursor()
            query = f"""SELECT MIN(volume_min), MAX(volume_max) FROM flow_data WHERE timestamp BETWEEN ? AND ?"""
            print(query)
            cur.execute(query, (int(start_date), int(end_date)))
            rows = cur.fetchall()
            col_name = [i[0] for i in cur.description]
            conn.close()
        except:
            self.traceback()
        return rows, col_name

    
    def insert_flow_data(self, flow_avg, volume_min, volume_max, packet_data, now)-> None:
        """_summary_

        Args:
            packet_data (_type_): _description_
        """
        try:
            sql = "insert into flow_data (flow_avg, volume_min, volume_max, packet_data, timestamp, datetime) VALUES (?,?,?,?,?,?)"
            self.log(sql)
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cursor = conn.cursor()
            #now = datetime.now()

            cursor.execute(sql,(
                    flow_avg,
                    volume_min,
                    volume_max,
                    str(packet_data),
                    int(datetime.timestamp(now)),
                    now.strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as ex:
            self.traceback()
            
    def insert_level_data(self, level_avg, timestamp_avg)-> None:
        """_summary_

        Args:
            packet_data (_type_): _description_
        """
        try:
            sql = "insert into level_data (level_avg, timestamp, datetime) VALUES (?,?,?)"
            self.log(sql)
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cursor = conn.cursor()
            now = datetime.now()

            cursor.execute(sql,(
                    level_avg,
                    int(timestamp_avg),
                    now.strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as ex:
            self.traceback()
            
    def get_level_data(self, columns="", condition_column = "", limit=10):
        """
        Obtiene datos de la base de datos, con la opción de especificar columnas y un límite.

        Args:
            database_path (str): Ruta de la base de datos.
            columns (str): Columnas personalizadas a seleccionar (por defecto, selecciona todas las relevantes).
            limit (int): Límite de filas a devolver.
        
        Returns:
            list: Lista de filas obtenidas de la base de datos.
        """
        rows, col_name = None, ""
        try:
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cur = conn.cursor()

            if condition_column:
                query = f"""SELECT id, level_avg, datetime, timestamp FROM level_data WHERE {condition_column}=0 order by id desc limit 10"""
            else:
                if columns:
                    query = f"SELECT id, {columns} FROM level_data order by id desc limit {limit}"
                else:
                    query = f"SELECT id, level_avg, datetime, uploaded_mining FROM level_data order by id desc limit {limit}"

            print(query)
            cur.execute(query)
            rows = cur.fetchall()
            col_name = [i[0] for i in cur.description]
            conn.close()
        except:
            self.traceback()
        return rows, col_name

    # === ENERGY ===#
    def get_energy_data(self, columns="", condition_column = "", limit=10):
        """
        Obtiene datos de la base de datos, con la opción de especificar columnas y un límite.

        Args:
            database_path (str): Ruta de la base de datos.
            columns (str): Columnas personalizadas a seleccionar (por defecto, selecciona todas las relevantes).
            limit (int): Límite de filas a devolver.

        Returns:
            list: Lista de filas obtenidas de la base de datos.
        """
        rows, col_name = None, ""
        try:
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cur = conn.cursor()

            if condition_column:
                query = f"""SELECT id, bat_v, pv_v, pv_i, datetime, timestamp FROM energy_data WHERE {condition_column}=0 order by id desc limit 10"""
            else:
                if columns:
                    query = f"SELECT id, {columns} FROM energy_data order by id desc limit {limit}"
                else:
                    query = f"SELECT id, bat_v, pv_v, pv_i, datetime, uploaded_mining FROM energy_data order by id desc limit {limit}"

            print(query)
            cur.execute(query)
            rows = cur.fetchall()
            col_name = [i[0] for i in cur.description]
            conn.close()
        except:
            self.traceback()
        return rows, col_name

    
    def insert_energy_data(self, bat_v, pv_v, pv_i)-> None:
        """_summary_

        Args:
            packet_data (_type_): _description_
        """
        try:
            sql = "insert into energy_data (bat_v, pv_v, pv_i, timestamp, datetime) VALUES (?,?,?,?,?)"
            self.log(sql)
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cursor = conn.cursor()
            now = datetime.now()

            cursor.execute(sql,(
                    bat_v,
                    pv_v,
                    pv_i,
                    int(datetime.timestamp(now)),
                    now.strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as ex:
            self.traceback()

    # === STATE BUTTON ===#
    def get_state_button_data(self, columns="", condition_column = "", limit=10):
        """
        Obtiene datos de la base de datos, con la opción de especificar columnas y un límite.

        Args:
            database_path (str): Ruta de la base de datos.
            columns (str): Columnas personalizadas a seleccionar (por defecto, selecciona todas las relevantes).
            limit (int): Límite de filas a devolver.

        Returns:
            list: Lista de filas obtenidas de la base de datos.
        """
        rows, col_name = None, ""
        try:
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cur = conn.cursor()

            if condition_column:
                query = f"""SELECT id, regador, cargar_agua, cargar_surfactante, detener, datetime, timestamp FROM state_button_data WHERE {condition_column}=0 order by id desc limit 10"""
            else:
                if columns:
                    query = f"SELECT id, {columns} FROM state_button_data order by id desc limit {limit}"
                else:
                    query = f"SELECT id, regador, cargar_agua, cargar_surfactante, detener, datetime, uploaded_mining FROM state_button_data order by id desc limit {limit}"

            print(query)
            cur.execute(query)
            rows = cur.fetchall()
            col_name = [i[0] for i in cur.description]
            conn.close()
        except:
            self.traceback()
        return rows, col_name

    # === STATE BUTTON ===#
    def get_state_button_data_turno(self, start_date, end_date, reg=""):
        """
        Obtiene datos de la base de datos, con la opción de especificar fechas en timestamp y entrega la suma, if reg=="" entrega suma total sino por regador

        Args:
            database_path (str): Ruta de la base de datos.
            columns (str): Columnas personalizadas a seleccionar (por defecto, selecciona todas las relevantes).
            limit (int): Límite de filas a devolver.

        Returns:
            list: Lista de filas obtenidas de la base de datos.
        """
        try:
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cur = conn.cursor()

            if reg=="":
                query = f"""SELECT SUM(cargar_agua), SUM(cargar_surfactante) FROM state_button_data WHERE timestamp BETWEEN ? AND ?"""
                print(query)
                cur.execute(query, (int(start_date)*1000, int(end_date)*1000))
            else:
                query = f"""SELECT SUM(cargar_agua), SUM(cargar_surfactante) FROM state_button_data WHERE regador = ? AND timestamp BETWEEN ? AND ?"""
                print(query)
                cur.execute(query, (reg, int(start_date)*1000, int(end_date)*1000))
            
            rows = cur.fetchall()
            col_name = [i[0] for i in cur.description]
            rows_list = rows[0]
            if None in rows_list:
                list = []
                for dato in rows_list:
                    if dato == None:
                        list.append(0)
                    else:
                        list.append(dato)
                rows = [tuple(list)]

            conn.close()
        except:
            self.traceback()
        return rows, col_name

    def insert_state_button_data(self, regador, cargar_agua, cargar_surfactante, detener, timestamp)-> None:
        """_summary_

        Args:
            packet_data (_type_): _description_
        """
        try:
            sql = "insert into state_button_data (regador, cargar_agua, cargar_surfactante, detener, timestamp, datetime) VALUES (?,?,?,?,?,?)"
            self.log(sql)
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cursor = conn.cursor()

            cursor.execute(sql,(
                    regador,
                    cargar_agua,
                    cargar_surfactante,
                    detener,
                    int(timestamp*1000),
                    datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as ex:
            self.traceback()

    def insert_turno_data(self, volumen_m3, cargas_agua, cargas_surfactante, reg_1_agua, reg_1_surf, reg_2_agua, reg_2_surf, reg_3_agua, reg_3_surf, timestamp, datetime)-> None:
        """_summary_

        Args:
            packet_data (_type_): _description_
        """
        try:
            sql = "insert into turno (volumen_m3, cargas_agua, cargas_surfactante, reg_1_agua, reg_1_surf, reg_2_agua, reg_2_surf, reg_3_agua, reg_3_surf, timestamp, datetime) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
            self.log(sql)
            conn = sqlite3.connect(self.database_path, timeout=30.0)
            cursor = conn.cursor()

            cursor.execute(sql,(
                    volumen_m3, cargas_agua, cargas_surfactante, reg_1_agua, reg_1_surf, reg_2_agua, reg_2_surf, reg_3_agua, reg_3_surf, int(timestamp), datetime.strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as ex:
            self.traceback()

    def get_turno_data(self, columns="", condition_column = "", limit=10):
        """
        Obtiene datos de la base de datos, con la opción de especificar columnas y un límite.

        Args:
            database_path (str): Ruta de la base de datos.
            columns (str): Columnas personalizadas a seleccionar (por defecto, selecciona todas las relevantes).
            limit (int): Límite de filas a devolver.

        Returns:
            list: Lista de filas obtenidas de la base de datos.
        """
        rows, col_name = None, ""
        try:
            conn = sqlite3.connect(self.database_path, timeout=10.0)
            cur = conn.cursor()

            if condition_column:
                query = f"""SELECT id, volumen_m3, cargas_agua, cargas_surfactante, reg_1_agua, reg_1_surf, reg_2_agua, reg_2_surf, reg_3_agua, reg_3_surf, datetime, timestamp FROM turno WHERE {condition_column}=0 order by id desc limit 10"""
                print(query)
                cur.execute(query)
            else:
                if columns:
                    query = f"SELECT id, {columns} FROM state_button_data order by id desc limit {limit}"
                    print(query)
                    cur.execute(query)
                else:
                    if limit<=0:
                        ahora =datetime.now()
                        if ahora.hour < 8:
                            ahora_date = datetime(ahora.year,ahora.month,ahora.day,20,0,0)-timedelta(days=1)
                        elif ahora.hour >=20:
                            ahora_date = datetime(ahora.year,ahora.month,ahora.day,20,0,0)
                        else:
                            ahora_date = datetime(ahora.year,ahora.month,ahora.day,8,0,0)
                        query_date = ahora_date - timedelta(hours=12)*abs(limit)
                        query = f"SELECT id, datetime, volumen_m3, cargas_agua, cargas_surfactante, reg_1_agua, reg_1_surf, reg_2_agua, reg_2_surf, reg_3_agua, reg_3_surf, uploaded_mining FROM turno WHERE timestamp = ? order by id desc limit {limit}"
                        print(query)
                        cur.execute(query, (int(query_date.timestamp()),))
                    else:
                        query = f"SELECT id, datetime, volumen_m3, cargas_agua, cargas_surfactante, reg_1_agua, reg_1_surf, reg_2_agua, reg_2_surf, reg_3_agua, reg_3_surf, uploaded_mining FROM turno order by id desc limit {limit}"
                        print(query)
                        cur.execute(query)

            rows = cur.fetchall()
            col_name = [i[0] for i in cur.description]
            conn.close()
        except:
            self.traceback()
        return rows, col_name
    
    def update_value(self, table, column_name, ids):
            try:
                conn = sqlite3.connect(self.database_path, timeout=10.0)
                cur = conn.cursor()
                sql="update {table} set {column}=1 where id in ({seq})".format(table=table, column=column_name, seq=','.join(['?']*len(ids)))
                cur.execute(sql, tuple(ids))
                conn.commit()
                conn.close()
                print(f"Ids {ids} actualizadas")

            except:
                e = sys.exc_info()
                print("Dumping traceback for [%s: %s]" % (str(e[0].__name__), str(e[1])))
                traceback.print_tb(e[2])

    def delete_rows(self, column, operator, condition_value, table):
        try:
            conn = sqlite3.connect(database= self.database_path) 
            cur = conn.cursor()
            query = f"""DELETE from {table} where {column} {operator} {condition_value}"""
            #print(query)
            cur.execute(query)
            rows = cur.fetchall()
            conn.close()
            return rows
        except:
            self.traceback()
        return rows


# Lógica principal para manejar argumentos de línea de comandos
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gestión de la base de datos del sistema.")
    parser.add_argument('-ct', '--create_database', default=False, help='Crea las tablas en la base de datos.', type=bool)
    parser.add_argument('-rd', '--reset_db', default=False, help='Reinicia y recrea la base de datos.', type=bool)
    parser.add_argument('-gd', '--get_data', default=False, help='Obtiene datos de la base de datos.', type=bool)
    parser.add_argument('-gcd', '--get_custome_data', default="", help='Obtiene columnas personalizadas de la base de datos.', type=str)
    parser.add_argument('-l', '--limit', default=10, help='Límite opcional para la consulta.', type=int)
    parser.add_argument('-gdt', '--get_data_turno', default=False, help='Obtiene datos del turno.', type=bool)
    parser.add_argument('-gh', '--get_health', default=False, help='Obtiene sanidad del cubic', type=bool)
    args = parser.parse_args()
    database = Database()
    if args.create_database:
        database.check_database()
        database.create_tables(dict_tables=tables.TABLES)
    elif args.reset_db:
        database.check_database()
        database.reset_database()
    elif args.get_data:
        # 1. Flow
        rows, col_name = database.get_flow_data(limit=args.limit)
        print(tabulate(rows, headers=col_name, tablefmt='psql'))

        ## 2. Energy
        #rows, col_name = database.get_energy_data(limit=args.limit)
        #print(tabulate(rows, headers=col_name, tablefmt='psql'))

        # 2. LEVEL
        rows, col_name = database.get_level_data(limit=args.limit)
        print(tabulate(rows, headers=col_name, tablefmt='psql'))

        # 3. State Button
        rows, col_name = database.get_state_button_data(limit=args.limit)
        print(tabulate(rows, headers=col_name, tablefmt='psql'))

        # 4. Turno
        rows, col_name = database.get_turno_data(limit=args.limit)
        print(tabulate(rows, headers=col_name, tablefmt='psql'))

    elif args.get_custome_data:
        # 1. Flow
        rows, col_name = database.get_flow_data(columns=args.get_custome_data, limit=args.limit)
        print(tabulate(rows, headers=col_name, tablefmt='psql'))

        ## 2. Energy
        #rows, col_name = database.get_energy_data(columns=args.get_custome_data, limit=args.limit)
        #print(tabulate(rows, headers=col_name, tablefmt='psql'))

        # 2. LEVEL
        rows, col_name = database.get_level_data(columns=args.get_custome_data, limit=args.limit)
        print(tabulate(rows, headers=col_name, tablefmt='psql'))

        # 3. State Button
        rows, col_name = database.get_state_button_data(columns=args.get_custome_data, limit=args.limit)
        print(tabulate(rows, headers=col_name, tablefmt='psql'))

        # 4. Turno
        rows, col_name = database.get_turno_data(columns=args.get_custome_data, limit=args.limit)
        print(tabulate(rows, headers=col_name, tablefmt='psql'))

    elif args.get_health:
        pass
        # TODO: PREGUNTAR QUE VAN A QUERER PARA SANIDAD
        # rows, col_name = database.get_dust_health()
        # print(tabulate(rows, headers=col_name, tablefmt='psql'))
    elif args.get_data_turno:
        # 4. Turno
        rows, col_name = database.get_turno_data(limit=args.limit)
        print(tabulate(rows, headers=col_name, tablefmt='psql'))
    else:
        print("Argumento no válido. Usa --help para ver las opciones disponibles.")
