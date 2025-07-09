# update system
sudo apt update && sudo apt upgrade -y

# install, enable, start mosquitto
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# create systemd service files
USER_NAME=$(whoami)
sed "s/__USERNAME__/${USER_NAME}/g" mqtt_postgres_bridge.service | sudo tee /etc/systemd/system/mqtt_postgres_bridge.service > /dev/null
sed "s/__USERNAME__/${USER_NAME}/g" summarizer.service | sudo tee /etc/systemd/system/summarizer.service > /dev/null
sudo cp summarizer.timer /etc/systemd/system/

# enable services
sudo systemctl daemon-reload
sudo systemctl enable mqtt_postgres_bridge.service
sudo systemctl start mqtt_postgres_bridge.service
sudo systemctl enable summarizer.timer
sudo systemctl start summarizer.timer