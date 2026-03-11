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

            threading.Thread(target=self.read, daemon=True).start()
            threading.Thread(target=self.write, daemon=True).start()

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

                if line == "":
                    continue

                try:
                    data = json.loads(line)
                except:
                    self.log(f"Invalid JSON: {line}")
                    continue
                if line =="":
                    pass
                else:
                    if "machine" in data:

                        machine = data["machine"]
                        self.last_nrf_data = time()
                        self.log(f"GOT MACHINE: {machine}")

                        if machine == "REG-001":
                            last_R1 = time()
                            if dict_reg["REG-001"] == False:
                                dict_reg["REG-001"] = True
                                changes = 1

                        elif machine == "REG-002":
                            last_R2 = time()
                            if dict_reg["REG-002"] == False:
                                dict_reg["REG-002"] = True
                                changes = 1

                        elif machine == "REG-003":
                            last_R3 = time()
                            if dict_reg["REG-003"] == False:
                                dict_reg["REG-003"] = True
                                changes = 1

                        elif machine == "REG-100":
                            last_R100 = time()
                            if dict_reg["REG-100"] == False:
                                dict_reg["REG-100"] = True
                                changes = 1


                    if any(k in data for k in ["cargar_agua", "cargar_sulf", "detener"]):
                        self.log(f"GOT COMMAND: {data}")
                        try:
                            regador = data.get("machine", "LOCAL")

                            timestamp = int(time())

                            button_state = {
                                "regador": regador,
                                "cargar_agua": data.get("cargar_agua", False),
                                "cargar_sulf": data.get("cargar_sulf", False),
                                "detener": data.get("detener", False),
                                "time": timestamp
                            }

                            with open("/button_state_live.json", "w") as f:
                                json.dump(button_state, f, indent=4)

                            log_line = "%s | %s | %s\n" % (
                                self.get_datetime(),
                                regador,
                                json.dumps(button_state)
                            )

                            self.write_file("/button_state.txt", log_line, "a")

                            self.log(f"Button state saved: {button_state}")

                        except Exception as e:
                            self.log(f"Error saving button state: {e}")

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
                
    def write(self) -> None:
        while True:
            try:
                if self.serial_module and self.serial_module.is_open:

                    msg = {
                        "timestamp": int(time())
                    }

                    data = json.dumps(msg)
                    self.serial_module.write((data + "\n").encode())

                    self.log(f"SENT: {data}")

                else:
                    self.log("Serial port not connected")

            except Exception as Ex:
                self.log(f"Write error: {Ex}")
            sleep(1)

    def puerto(self, port):
        if "tty" in str(port):
            return port
        else:
            out = subprocess.check_output(["usb","-a",str(port)]).decode()
            return out[:-1]
