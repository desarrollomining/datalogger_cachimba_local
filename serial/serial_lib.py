import threading
from serial import Serial
import serial 
from time import time, sleep
from lib.utils import Utils
import json
import subprocess
from database.models import Database
import os
from datetime import datetime

class SerialLib(Utils):
    def __init__(self, usbdevnode, baudrate: int = 9600, log_id = "SERIAL") -> None:
        self.baudrate = baudrate
        self.timeout = 0.5
        self.log_id = log_id
        self.usbdevnode = self.usb_port(usbdevnode)
        self.last_serial_data=time()
        self. last_button_state = {
            "cargar_agua": False,
            "cargar_sulf": False,
        }
        self.data={}
        self.database = Database()
        self.last_serial = time()
        self.writting = 0
        self.writting_surf = 0
        self.liters_list = []
        self.seconds_microdata = 60 
        self.timer_microdata = serial.serialutil.Timeout(self.seconds_microdata)

        
        threading.Thread(target = self.connect).start()

        threading.Thread(target = self.local).start()

    #Hilo que aplaza la habilitacion de deteccion de boton de agua local 2 segundos
    def off_writting(self):
        sleep(2)
        self.writting = 0


    #Hilo que aplaza la habilitacion de deteccion de boton de surfactante local 2 segundos
    def off_writting_surf(self):
        sleep(2)
        self.writting_surf = 0

    def local(self):
        start = 0
        start_surf = 0
        surf = 0
        while True:
            try:
                ##BOTON ELECTROVALVULA
                if self.data['s24_1']>12.0 and start==0 and self.writting==0:
                    start = time()
                    self.log('Deteccion')
                elif start!=0 and (time()-start)>5:
                    out = subprocess.check_output(['tail','-n','1','/button_state.txt'])
                    out_d = out.decode()
                    data = out_d[:-1].split('|')
                    data_f=data[2][1:]
                    data_dict = json.loads(data_f)
                    #El ultimo boton inscrito fue posterior al boton local, se considera solo el digital
                    if data_dict['time']>start:
                        pass
                    #El ultimo boton fue antes del local, se considera el local
                    elif data_dict['time']<=start:
                        if self.data['s24_2']<4.0:
                            ##self.database.insert_state_button_data("LOCAL", True, False, False, int(start))
                            data_dict['time']=int(start)
                            data_dict['regador']="LOCAL"
                            data_dict['cargar_agua']=True
                            data_dict['cargar_sulf']=False
                            data_dict['detener']=False
                            with open("/button_state_live.json", "w") as f:
                                json.dump(data_dict, f, indent=len(data_dict))
                            self.write_file("/button_state.txt", "%s | %s| %s\n" % (self.get_datetime(), "LOCAL",  json.dumps(data_dict)), "a")
                    
                    start=0
            except:
                pass

            try:
                ##BOTON BOMBA
                if self.data['s24_2']>4.0 and start_surf==0 and surf==0 and self.writting_surf==0:
                    start_surf = time()
                elif start_surf!=0 and (time()-start_surf)>5 and surf==0:
                    out = subprocess.check_output(['tail','-n','1','/button_state.txt'])
                    out_d = out.decode()
                    data = out_d[:-1].split('|')
                    data_f=data[2][1:]
                    data_dict = json.loads(data_f)
                    #El ultimo boton inscrito fue posterior al boton local, se considera solo el digital
                    if data_dict['time']>start_surf:
                        pass
                    #El ultimo boton fue antes del local, se considera el local
                    elif data_dict['time']<=start_surf:
                        ##self.database.insert_state_button_data("LOCAL", False, True, False, int(start))
                        data_dict['time']=int(start_surf)
                        data_dict['regador']="LOCAL"
                        data_dict['cargar_agua']=False
                        data_dict['cargar_sulf']=True
                        data_dict['detener']=False
                        with open("/button_state_live.json", "w") as f:
                            json.dump(data_dict, f, indent=len(data_dict))
                        self.write_file("/button_state.txt", "%s | %s| %s\n" % (self.get_datetime(), "LOCAL",  json.dumps(data_dict)), "a")
                    
                    start_surf=0
                    surf = 1
                
                if start_surf==0 and surf==1:
                    if self.data['s24_2']<4.0:
                        ##self.database.insert_state_button_data("LOCAL", False, False, True, int(start))
                        data_dict['time']=time()
                        data_dict['regador']="LOCAL"
                        data_dict['cargar_agua']=False
                        data_dict['cargar_sulf']=False
                        data_dict['detener']=True
                        with open("/button_state_live.json", "w") as f:
                            json.dump(data_dict, f, indent=len(data_dict))
                        self.write_file("/button_state.txt", "%s | %s| %s\n" % (self.get_datetime(), "LOCAL",  json.dumps(data_dict)), "a")
                        surf = 0
            except:
                pass

            sleep(0.2)


    def usb_port(self, port):
        #USB PORT
        puerto = str(port)
        if 'tty' in puerto:
            return puerto
        else:
            out = subprocess.check_output(['usb','-a',str(port)]).decode()
            return out[:-1]

    def connect(self) -> None:
        """
        This function attempts to establish a serial connection with the specified USB device node.

        """

        try:
            self.log(f"Try to connect serial port: {self.usbdevnode}")
            self.serial_module = Serial(self.usbdevnode, self.baudrate, timeout=self.timeout)
            self.read()

        except Exception as Ex:
            self.log(Ex)

    def read(self) -> None:
        """
        This function continuously reads lines from the serial module and processes them.
        If the line is empty, the function skips it.

        """
        self.log("Reading line from serial")
        self.string = "*000"
        self.last_string = ""
        self.bomba_String = "0*"
        self.estado_bomba = 0
        self.cambio = 0
        while True:
            try:
                raw_line = self.serial_module.readline().decode("utf-8")
                line = raw_line.strip()
                if line =="":
                    pass
                else:
                    self.log(f"GOT: {line}")
                    self.last_serial_data=time()
                    line_s = line.split(';')
                    for i in range(1,len(line_s)):
                        self.data[line_s[i].split(':')[0]]=float(line_s[i].split(':')[1])
                    #print(self.data)
                    if self.data!={}:
                        self.data_analisis()
                        if self.timer_microdata.expired():
                            if len(self.liters_list)>0:
                                level_avg = round(sum([d['level'] for d in self.liters_list])/len(self.liters_list),3)
                                timestamp = int(time())*1000
                                self.database.insert_level_data(level_avg, timestamp)
                                now = datetime.now()
                                self.save_json_local("level_data.json", {
                                    "level": level_avg,
                                    "timestamp": timestamp,
                                    "datetime": now.strftime('%Y-%m-%d %H:%M:%S')
                                })
                            self.liters_list = []
                            self.timer_microdata.restart(self.seconds_microdata)
                    self.read_button_state()
                sleep(0.2)

            except Exception as Ex:
                self.log(Ex)

    def data_analisis(self):
        #s24_1 es el apriete del boton de abrir valvula
        if self.data['s24_1']>12.0:
            self.log('Abriendo valvula')
        #s24_1 es el apriete del boton de cerrar valvula
        if self.data['s24_2']>12.0:
            self.log('Encendiendo Bomba de Surfactante')
        #s12_2 es el sensor de nivel con 1.1V para 640L y 1.55 para 820 litros
        pendiente = (1000-640)/(1.95-1.1)
        litros = 1000-pendiente*(1.95-self.data['s12_2']) 
        microdata = {
            "level": litros/10, # dividir por 10 para porcentaje
            }
        self.liters_list.append(microdata)
        self.log('PORCENTAJE: '+str(litros/10))
        if litros<800 and self.estado_bomba==0:
            self.log('ENCENDIENDO BOMBA PEQUENA LITROS: '+str(litros))
            self.estado_bomba = 1
            self.cambio = 1
            self.bomba_String = "1*"
        if litros>900 and self.estado_bomba==1:
            self.log('APAGANDO BOMBA PEQUENA LITROS: '+str(litros))
            self.estado_bomba = 0
            self.cambio = 1
            self.bomba_String = "0*"

    def read_button_state(self):
        try:
            f = open('/button_state_live.json')
            data = json.load(f)
            if self.last_button_state != data:
                self.log(f"Se ha detectado un cambio, nuevo estado: {data}")
                self.process_state(data)
                self.last_button_state = data
            if self.cambio == 1:
                self.write(self.string + self.bomba_String)
                self.last_serial = time()
                #print(self.string + self.bomba_String)
                self.last_string = str(self.string)
                self.cambio = 0
            
            if (time()-self.last_serial)>15:
                self.write(self.string + self.bomba_String)
                self.last_serial = time()


        except Exception as Ex:
            self.log(Ex)

    def process_state(self, data):
        try:
            #CHECK AGUA
            if data["cargar_agua"] != self.last_button_state["cargar_agua"]: # solo si cambio
                if data["cargar_agua"] ==True:
                    #self.push_button("*1000*", 1)
                    self.writting = 1
                    self.write("*100"+self.bomba_String)
                    sleep(1)
                    self.log('ABRIENDO VALVULA CACHIMBA')
                    self.write("*000"+self.bomba_String) # T0DO: AGREGAR VERIFICACION
                    self.last_serial = time()
                    sleep(0.5)
                    self.string = "*000"
                    threading.Thread(target = self.off_writting).start()
                    return 
                elif data["cargar_agua"] ==False:
                    #self.push_button("*0100*", 1) # T0DO: AGREGAR VERIFICACION
                    self.write("*010"+self.bomba_String)
                    sleep(1)
                    self.log('CERRANDO VALVULA CACHIMBA')
                    self.write("*000"+self.bomba_String)
                    self.last_serial = time()
                    sleep(0.5)
                    self.string = "*000"
                    return
                else:
                    self.log("Dato no codificado correctamente")

                

            # CHECK SULF
            elif data["cargar_sulf"] != self.last_button_state["cargar_sulf"]: # solo si cambio
                if data["cargar_sulf"] ==True:
                    self.log('ENCENDIENDO BOMBA SURFACTANTE')
                    self.writting_surf = 1
                    self.write("*001"+self.bomba_String) # T0DO: AGREGAR VERIFICACION
                    self.last_serial = time()
                    self.string = "*001"
                    return
                elif data["cargar_sulf"] ==False:
                    self.log('APAGANDO BOMBA SURFACTANTE')
                    self.write("*000"+self.bomba_String) # T0DO: AGREGAR VERIFICACION
                    self.last_serial = time()
                    self.string = "*000"
                    threading.Thread(target = self.off_writting_surf).start()
                    return 
                else:
                    self.log("Dato no codificado correctamente")

            #if data["cargar_agua"] ==False and data["regresar"]==True:
            #    self.write("*0100*")
            #    sleep(1)
            #    self.log('CERRANDO VALVULA CACHIMBA')
            #    self.write("*0000*")
            #    sleep(0.5)
            #    return
            else: return

        
        except Exception as Ex:
            self.log(Ex)


    def push_button(self, data, seconds):
        try:
            # Simulate push button for 1 second
            last_time = time()
            while time() - last_time <= seconds:
                self.write(data)

        except Exception as Ex:
            self.log(Ex)

    def write(self, data):
        try:
            self.log(f"Sending: {data}")
            #a='*111*'.encode('utf-8')
            self.serial_module.write((data+'\n').encode('utf-8'))
        except Exception as Ex:
            self.log(Ex)

    def save_json_local(self, filename, data):
        """Guarda datos en un archivo JSON dentro de la carpeta del archivo actual."""
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_path, filename)

            # Escribir archivo completo
            with open(full_path, "w") as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            self.log(f"Error guardando JSON local: {e}")
