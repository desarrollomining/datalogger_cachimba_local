import time
import sys

sys.path.append('/srv/datalogger_cachimba/')
from serial_lib import SerialLib


USB_SERIAL = 3

if __name__ == "__main__":
    RX = SerialLib(USB_SERIAL,log_id="SERIAL")
    RX.set_panic_command("systemctl restart mining-serial")
    RX.log("mining serial, initialized")

    while True:
        # Breathe
        silence_period = time.time() - RX.last_serial_data
        if int(silence_period) > 40:
            RX.panic("Too much RX silence")
        print("last_serial_data: %s" % str(silence_period))
        time.sleep(1)
