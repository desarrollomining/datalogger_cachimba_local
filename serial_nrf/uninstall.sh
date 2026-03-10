systemctl stop mining-serial-nrf
systemctl disable mining-serial-nrf
rm /etc/systemd/system/mining-serial-nrf.service
systemctl daemon-reload

