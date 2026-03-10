import sys
sys.path.append('/srv/datalogger_cachimba/')
from lib.utils import Utils

SOURCE_CONFIG = "/srv/datalogger_cachimba/config_cachimba.json"

class Config(Utils):
	def __init__(self, log_id = "CONFIG"):
		self.log_id = log_id
		self.machine_id = self.get_product_id()
		self.machine_name = self.get_product_name()
		self.location = self.get_location_assigned()
		self.faena = self.get_faena_assigned()
		self.avalaible_faenas = self.get_avalaible_faenas(datalogger_type= "cachimba")
	

if __name__ == "__main__":
	config = Config()
	print("Actualizando configuraciones")
	