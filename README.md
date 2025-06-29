# climate_monitor

I have an air conditioner temperature controller with a mind of its own. I also happened to have several Raspberry Pi Pico Ws laying around, so I bought some cheap AHT21 temperature sensors and got to work.

I thought this project would be a great chance to implement Kafka and the MQTT protocol in a home setup.

    +-------------+                             +--------Raspberry Pi 5------------------+
  +-------------+ |                             |   +-------------+       +----------+   |
+-------------+ | |  -----temperature data--------->| MQTT broker |       | Postgres |   |
| R Pi Pico W | | +                             |   |   script    |------>| Database |   |
| w/ 2 AHT21s | +                               |   +-------------+       +----------+   |
+-------------+                                 +----------------------------------------+



+-------------------+         WiFi/MQTT         +-----------------------------+
|                   | ------------------------> |                             |
|  R Pi Pico W      |                           |    Raspberry Pi 5           |
|  (2x AHT21s)      |                           |                             |
|  [Sensor Node]    |                           |  +-----------------------+  |
|                   |                           |  |   MQTT Broker         |  |
+-------------------+                           |  +-----------------------+  |
                                                |  |   Data Processing     |  |
                                                |  |   Script (MQTT Sub)   |  |
                                                |  +----------+------------+  |
                                                |             |               |
                                                |             v               |
                                                |  +-----------------------+  |
                                                |  |   Postgres Database   |  |
                                                |  +-----------------------+  |
                                                +-----------------------------+