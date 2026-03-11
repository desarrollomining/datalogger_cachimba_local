cd /srv/datalogger_cachimba
for service in config serial serial_nrf state_button turno
do
    cd $service
    sh install.sh
    cd ..
done