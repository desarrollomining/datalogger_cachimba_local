import time
import sys

sys.path.append('/srv/datalogger_cachimba/')
from serial_lib import SerialLib
PORT = 5

if __name__ == "__main__":
    RX = SerialLib(PORT,log_id="SERIAL-NRF")
    RX.set_panic_command("systemctl restart mining-serial-nrf")
    RX.log("mining serial, initialized")

    while True:
        # Breathe
        silence_period = time.time() - RX.last_nrf_data
        if int(silence_period) > 120:
            RX.panic("Too much RX silence")
        print("last_nrf_data: %s" % str(silence_period))
        time.sleep(1)
