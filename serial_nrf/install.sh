systemctl stop mining-serial-nrf
systemctl disable mining-serial-nrf
rm /etc/systemd/system/mining-serial-nrf.service
systemctl daemon-reload
cp /srv/datalogger_cachimba/serial_nrf/mining-serial-nrf.service /etc/systemd/system/mining-serial-nrf.service
systemctl enable mining-serial-nrf
systemctl restart mining-serial-nrf
