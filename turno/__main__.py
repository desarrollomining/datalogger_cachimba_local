import sys
sys.path.append('/srv/datalogger_cachimba/')
from time import time, sleep
from lib.utils import Utils
from database.models import Database
import subprocess
from datetime import datetime, timedelta

#sys.path.append('/srv/datalogger_cachimba/')

class Turno(Utils):
    def __init__(self, log_id="TURNO")->None:
        self.database = Database()
        self.log_id = log_id

    def analisis(self):
        while True:
            try:
                ahora =datetime.now()
                if ahora.hour < 8:
                    ahora_date = datetime(ahora.year,ahora.month,ahora.day,20,0,0)-timedelta(days=1)
                elif ahora.hour >=20:
                    ahora_date = datetime(ahora.year,ahora.month,ahora.day,20,0,0)
                else:
                    ahora_date = datetime(ahora.year,ahora.month,ahora.day,8,0,0)
                rows, cols = self.database.get_turno_data(limit=-1)
                
                if rows==[]:
                    ahora_date = ahora_date - timedelta(hours=12)
                    volumen_m3, cargas_agua, cargas_surfactante, reg_1_agua, reg_1_surf, reg_2_agua, reg_2_surf, reg_3_agua, reg_3_surf = self.get_analisis(ahora_date)
                    self.database.insert_turno_data(volumen_m3, cargas_agua, cargas_surfactante, reg_1_agua, reg_1_surf, reg_2_agua, reg_2_surf, reg_3_agua, reg_3_surf, int(ahora_date.timestamp()), ahora_date)
                    self.log(f'INSERT TURNO DATA VOLUMEN_M3: {volumen_m3}, CARGAS_AGUA: {cargas_agua}, CARGAS_SURFACTANTE: {cargas_surfactante}, AGUA_REG: {[reg_1_agua,reg_2_agua,reg_3_agua,cargas_agua-(reg_1_agua+reg_2_agua+reg_3_agua)]}, SURF_REG: {[reg_1_surf,reg_2_surf,reg_3_surf,cargas_surfactante-(reg_1_surf+reg_2_surf+reg_3_surf)]}')
                else: pass

            except:
                self.traceback()
            
            sleep(60)

    def get_analisis(self,ahora_date):
        #DATA DE VOLUMEN
        rows, cols = self.database.get_flow_data_date(ahora_date.timestamp(), (ahora_date+timedelta(hours=12)).timestamp())
        data_vol = list(rows[0])
        volumen_m3 = data_vol[1]-data_vol[0]

        #CARGAS GENERALES
        rows, cols = self.database.get_state_button_data_turno(ahora_date.timestamp(), (ahora_date+timedelta(hours=12)).timestamp())
        data_cargas = list(rows[0])
        cargas_agua = data_cargas[0]
        cargas_surfactante = data_cargas[1]

        #CARGAS REG-01
        rows, cols = self.database.get_state_button_data_turno(ahora_date.timestamp(), (ahora_date+timedelta(hours=12)).timestamp(), reg='REG-01')
        data_cargas = list(rows[0])
        reg_1_agua = data_cargas[0]
        reg_1_surf = data_cargas[1]

        #CARGAS REG-02
        rows, cols = self.database.get_state_button_data_turno(ahora_date.timestamp(), (ahora_date+timedelta(hours=12)).timestamp(), reg='REG-02')
        data_cargas = list(rows[0])
        reg_2_agua = data_cargas[0]
        reg_2_surf = data_cargas[1]

        #CARGAS REG-03
        rows, cols = self.database.get_state_button_data_turno(ahora_date.timestamp(), (ahora_date+timedelta(hours=12)).timestamp(), reg='REG-03')
        data_cargas = list(rows[0])
        reg_3_agua = data_cargas[0]
        reg_3_surf = data_cargas[1]

        return volumen_m3, cargas_agua, cargas_surfactante, reg_1_agua, reg_1_surf, reg_2_agua, reg_2_surf, reg_3_agua, reg_3_surf


if __name__ == "__main__":
    TURNO = Turno()
    TURNO.log("mining flow, initialized")
    TURNO.analisis()
