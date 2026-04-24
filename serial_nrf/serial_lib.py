import threading
from serial import Serial
from time import time, sleep
from lib.utils import Utils
import json
import subprocess

class SerialLib(Utils):
    def __init__(self, port, baudrate: int = 9600, log_id = "SERIAL-NRF") -> None:
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
        last_R10 = time()
        last_R11 = time()
        last_R12 = time()
        last_R13 = time()
        last_R14 = time()
        last_R15 = time()
        last_R16 = time()
        changes = 0
        try:
            with open('/srv/datalogger_cachimba/reg.json', 'r') as file:
                dict_reg = json.load(file)
        except:
            dict_reg = {"REG-010": False, "REG-011": False, "REG-012": False, "REG-013": False, "REG-014": False, "REG-015": False, "REG-016": False}
            with open('/srv/datalogger_cachimba/reg.json', 'w') as file:
                json.dump(dict_reg, file, indent=4)
        while True:
            try:
                raw_line = self.serial_module.readline().decode("utf-8", errors="ignore")
                line = raw_line.strip()

                if not line:
                    continue

                start = line.find("{")
                end = line.rfind("}")

                if start == -1 or end == -1:
                    continue

                json_str = line[start:end+1]

                try:
                    data = json.loads(json_str)

                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]

                except Exception:
                    self.log(f"Invalid JSON extracted: {json_str}")
                    continue
                if line =="":
                    pass
                else:
                    if "machine" in data:

                        machine = data["machine"]
                        self.last_nrf_data = time()
                        self.log(f"GOT MACHINE: {machine}")

                        if machine == "REG-010":
                            last_R10 = time()
                            if dict_reg["REG-010"] == False:
                                dict_reg["REG-010"] = True
                                changes = 1

                        elif machine == "REG-011":
                            last_R11 = time()
                            if dict_reg["REG-011"] == False:
                                dict_reg["REG-011"] = True
                                changes = 1

                        elif machine == "REG-012":
                            last_R12 = time()
                            if dict_reg["REG-012"] == False:
                                dict_reg["REG-012"] = True
                                changes = 1

                        elif machine == "REG-013":
                            last_R13 = time()
                            if dict_reg["REG-013"] == False:
                                dict_reg["REG-013"] = True
                                changes = 1
                        
                        elif machine == "REG-014":
                            last_R14 = time()
                            if dict_reg["REG-014"] == False:
                                dict_reg["REG-014"] = True
                                changes = 1
                                
                        elif machine == "REG-015":
                            last_R15 = time()
                            if dict_reg["REG-015"] == False:
                                dict_reg["REG-015"] = True
                                changes = 1
                                
                        elif machine == "REG-016":
                            last_R16 = time()
                            if dict_reg["REG-016"] == False:
                                dict_reg["REG-016"] = True
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
                if (time()-last_R10)>10.0 and dict_reg["REG-010"]==True:
                    dict_reg["REG-010"]=False
                    changes = 1
                if (time()-last_R11)>10.0 and dict_reg["REG-011"]==True:
                    dict_reg["REG-011"]=False
                    changes = 1
                if (time()-last_R12)>10.0 and dict_reg["REG-012"]==True:
                    dict_reg["REG-012"]=False
                    changes = 1
                if (time()-last_R13)>10.0 and dict_reg["REG-013"]==True:
                    dict_reg["REG-013"]=False
                    changes = 1
                if (time()-last_R14)>10.0 and dict_reg["REG-014"]==True:
                    dict_reg["REG-014"]=False
                    changes = 1
                if (time()-last_R15)>10.0 and dict_reg["REG-015"]==True:
                    dict_reg["REG-015"]=False
                    changes = 1
                if (time()-last_R16)>10.0 and dict_reg["REG-016"]==True:
                    dict_reg["REG-016"]=False
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
