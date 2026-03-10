systemctl stop mining-turno
systemctl disable mining-turno
rm /etc/systemd/system/mining-turno.service
systemctl daemon-reload
cp /srv/datalogger_cachimba/turno/mining-turno.service /etc/systemd/system/mining-turno.service
systemctl enable mining-turno
systemctl restart mining-turno
sudo cp /srv/datalogger_cachimba/turno/turno /bin/turno
sudo chmod 777 /bin/turno