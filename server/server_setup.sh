# Get username and server directory (where this script is located)
USER_NAME=$(whoami)
SERVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Climate Monitor Setup ==="
echo "User name: $USER_NAME  Server directory: $SERVER_DIR"
echo ""

# update system
sudo apt update && sudo apt upgrade -y

# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# build uv environment
uv python install 3.13
cd "$SERVER_DIR"
uv sync

# install, enable, start mosquitto
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# create systemd service files
SED_SUBS="s|__USERNAME__|${USER_NAME}|g; s|__SERVER_DIR__|${SERVER_DIR}|g"
sed "$SED_SUBS" "$SERVER_DIR/service_files/mqtt_postgres_bridge.service" | sudo tee /etc/systemd/system/climate_monitor_mqtt_postgres_bridge.service > /dev/null
sed "$SED_SUBS" "$SERVER_DIR/service_files/summarizer.service" | sudo tee /etc/systemd/system/climate_monitor_summarizer.service > /dev/null
sed "$SED_SUBS" "$SERVER_DIR/service_files/bulk_data_provider.service" | sudo tee /etc/systemd/system/climate_monitor_bulk_data_provider.service > /dev/null
sed "$SED_SUBS" "$SERVER_DIR/service_files/websocket_server.service" | sudo tee /etc/systemd/system/climate_monitor_websocket_server.service > /dev/null
sudo cp service_files/summarizer.timer /etc/systemd/system/climate_monitor_summarizer.timer

# enable and start services
sudo systemctl daemon-reload
sudo systemctl enable climate_monitor_mqtt_postgres_bridge.service
sudo systemctl start climate_monitor_mqtt_postgres_bridge.service
sudo systemctl enable climate_monitor_summarizer.timer
sudo systemctl start climate_monitor_summarizer.timer
sudo systemctl enable climate_monitor_bulk_data_provider.service
sudo systemctl start climate_monitor_bulk_data_provider.service
sudo systemctl enable climate_monitor_websocket_server.service
sudo systemctl start climate_monitor_websocket_server.service
