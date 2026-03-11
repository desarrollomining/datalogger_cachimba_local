cd /srv/datalogger_cachimba
for service in config serial serial_nrf state_button turno
do
    cd $service
    sh uninstall.sh
    cd ..
done