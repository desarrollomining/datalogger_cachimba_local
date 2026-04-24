import sys
from time import sleep
import json

sys.path.append('/srv/datalogger_cachimba/')
from lib.utils import Utils
from database.models import Database

class StateButton(Utils):
    def __init__(self, log_id) -> None:
        self.log_id = log_id
        self.database = Database()
        self.last_button_state = {}
        self.read_state()
    
    def read_state(self):
        while True:
            try:
                f = open('/button_state_live.json')
                data = json.load(f)
                if data != self.last_button_state:
                    self.database.insert_state_button_data(data["regador"], data["cargar_agua"], data["cargar_sulf"], data["detener"], data["time"])
                    self.last_button_state = data
                sleep(0.5)
        
            except Exception as ex:
                print(ex)


if __name__ == "__main__":
    STATE_BUTTON = StateButton(log_id="STATE-BUTTON")
    STATE_BUTTON.log("mining state-button, initialized")

