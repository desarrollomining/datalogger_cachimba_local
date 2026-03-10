import threading
from serial import Serial
from time import time, sleep
from lib.utils import Utils
import json
import subprocess

class SerialLib(Utils):
    def __init__(self, port, baudrate: int = 115200, log_id = "SERIAL-NRF") -> None:
        self.baudrate = baudrate
        self.timeout = 0.5
        self.log_id = log_id
        self.last_nrf_data = time()
        self.port = self.puerto(port)
        threading.Thread(target = self.connect).start()

    def connect(self) -> None:
        """
        This function attempts to establish a serial connection with the specified USB device node.

        """

        try:
            self.log(f"Try to connect serial port: {self.port}")
            self.serial_module = Serial(self.port, self.baudrate, timeout=self.timeout)
            self.read()

        except Exception as Ex:
            self.log(Ex)

    def read(self) -> None:
        """
        This function continuously reads lines from the serial module and processes them.
        If the line is empty, the function skips it.

        """
        self.log("Reading line from serial")
        last_R1 = time()
        last_R2 = time()
        last_R3 = time()
        last_R100 = time()
        changes = 0
        try:
            with open('/srv/datalogger_cachimba/reg.json', 'r') as file:
                dict_reg = json.load(file)
        except:
            dict_reg = {"REG-001": False, "REG-002": False, "REG-003": False, "REG-100": False}
            with open('/srv/datalogger_cachimba/reg.json', 'w') as file:
                json.dump(dict_reg, file, indent=4)
        while True:
            try:
                raw_line = self.serial_module.readline().decode("utf-8")
                line = raw_line.strip()
                if line =="":
                    pass
                else:
                    self.last_nrf_data = time()
                    if "REG" in line: self.log(f"GOT: {line}")
                    #self.log(f"GOT: {line}")

                    #Si alguno aparece acualizamos el tiempo de la ultima vez y a True si esta en False
                    if "REG-001" in line:
                        last_R1 = time()
                        if dict_reg["REG-001"]==False:
                            dict_reg["REG-001"]=True
                            changes = 1
                    elif "REG-002" in line:
                        last_R2 = time()
                        if dict_reg["REG-002"]==False:
                            dict_reg["REG-002"]=True
                            changes = 1
                    elif "REG-003" in line:
                        last_R3 = time()
                        if dict_reg["REG-003"]==False:
                            dict_reg["REG-003"]=True
                            changes = 1
                    elif "REG-100" in line:
                        last_R100 = time()
                        if dict_reg["REG-100"]==False:
                            dict_reg["REG-100"]=True
                            changes = 1

                #Si alguno lleva mucho tiempo 10segndos fuera cambia a False
                if (time()-last_R1)>10.0 and dict_reg["REG-001"]==True:
                    dict_reg["REG-001"]=False
                    changes = 1
                if (time()-last_R2)>10.0 and dict_reg["REG-002"]==True:
                    dict_reg["REG-002"]=False
                    changes = 1
                if (time()-last_R3)>10.0 and dict_reg["REG-003"]==True:
                    dict_reg["REG-003"]=False
                    changes = 1
                if (time()-last_R100)>10.0 and dict_reg["REG-100"]==True:
                    dict_reg["REG-100"]=False
                    changes = 1

                #Si algo cambia reescribimos el json
                if changes==1:
                    with open('/srv/datalogger_cachimba/reg.json', 'w') as file:
                        json.dump(dict_reg, file, indent=4)
                    changes = 0
                    self.log(dict_reg)
                sleep(0.01)

            except Exception as Ex:
                self.log(Ex)

    def puerto(self, port):
        if "tty" in str(port):
            return port
        else:
            out = subprocess.check_output(["usb","-a",str(port)]).decode()
            return out[:-1]
