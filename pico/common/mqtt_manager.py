import os
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from logger import log

class MqttManager:
    def __init__(self, radio):
        self.broker = os.getenv("MQTT_BROKER_ADDRESS")
        self.port = int(os.getenv("MQTT_PORT"))
        self.topic = os.getenv("MQTT_TOPIC")
        self.sensor_id = os.getenv("SENSOR_ID")
        self.pool = socketpool.SocketPool(radio)
        self.client = MQTT.MQTT(
            broker=self.broker,
            port=self.port,
            socket_pool=self.pool,
        )
        self.client.on_connect = self._on_connect
        self._connect_forever()
        
    def _on_connect(self, client, userdata, flags, rc):
        log("Connected to MQTT broker!")

    def _connect_forever(self):
        import time
        while True:
            try:
                self.client.connect()
                return
            except Exception as e:
                log("MQTT connect failed, retrying in 5 seconds:", e)
                time.sleep(5)

    def publish(self, msg):
        try:
            self.client.publish(self.topic, msg)
        except Exception as e:
            log(f"Publish failed: {e}")
    
    def recover(self):
        import time
        try:
            self.client.reconnect()
            log("MQTT reconnected.")
        except Exception as e:
            log("Reconnect failed:", e)
            time.sleep(5)
            self._connect_forever()