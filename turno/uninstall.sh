systemctl stop mining-turno
systemctl disable mining-turno
rm /etc/systemd/system/mining-turno.service
systemctl daemon-reload
sudo rm /bin/turno
