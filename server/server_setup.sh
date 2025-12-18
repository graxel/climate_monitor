# update system
sudo apt update && sudo apt upgrade -y

# install, enable, start mosquitto
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# create systemd service files
USER_NAME=$(whoami)
sed "s/__USERNAME__/${USER_NAME}/g" service_files/mqtt_postgres_bridge.service | sudo tee /etc/systemd/system/climate_monitor_mqtt_postgres_bridge.service > /dev/null
sed "s/__USERNAME__/${USER_NAME}/g" service_files/bulk_data_provider.service | sudo tee /etc/systemd/system/climate_monitor_bulk_data_provider.service > /dev/null
sed "s/__USERNAME__/${USER_NAME}/g" service_files/websocket_server.service | sudo tee /etc/systemd/system/climate_monitor_websocket_server.service > /dev/null
sed "s/__USERNAME__/${USER_NAME}/g" service_files/summarizer.service | sudo tee /etc/systemd/system/climate_monitor_summarizer.service > /dev/null
sudo cp service_files/summarizer.timer /etc/systemd/system/climate_monitor_summarizer.timer

# enable and start services
sudo systemctl daemon-reload
sudo systemctl enable climate_monitor_mqtt_postgres_bridge.service
sudo systemctl start climate_monitor_mqtt_postgres_bridge.service
sudo systemctl enable climate_monitor_bulk_data_provider.service
sudo systemctl start climate_monitor_bulk_data_provider.service
sudo systemctl enable climate_monitor_websocket_server.service
sudo systemctl start climate_monitor_websocket_server.service
sudo systemctl enable climate_monitor_summarizer.timer
sudo systemctl start climate_monitor_summarizer.timer
