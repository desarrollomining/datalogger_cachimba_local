systemctl stop mining-state-button
systemctl disable mining-state-button
rm /etc/systemd/system/mining-state-button.service
systemctl daemon-reload
cp /srv/datalogger_cachimba/state_button/mining-state-button.service /etc/systemd/system/mining-state-button.service
systemctl enable mining-state-button
systemctl restart mining-state-button
