systemctl stop mining-state-button
systemctl disable mining-state-button
rm /etc/systemd/system/mining-state-button.service
systemctl daemon-reload

