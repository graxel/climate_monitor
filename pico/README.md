# Setting up your Raspberry Pi Pico boards

## Hardware
For each Raspberry Pi Pico board, you'll need two AHT2x sensors, a 3- and a 5-pin header, and a few inches of single core copper wire.

1. 3-pin header
    - Remove the middle pin with pliers.
    - Bend the very tips of the two pins slightly outward.
    - Bend the pins inward so the tips are parallel and 0.1" apart.
    - Solder the short ends of the pins on the front of the board in holes 36 and 38 (3V3 and GND).
2. 5-pin header
    - Hold the header horizontally, with the longer pins facing you. Use pliers to bend the two rightmost pins about 80 degrees forward.
    - Solder the short ends of the pins on the front of the board in holes 1 through 5 (GP0, GP1, GND, GP2, and GP3), with the bent pins in holes 4 and 5 and bent towards the board.
3. AHT2x sensor #1
    - Cut two pieces of wire about 1" long. Solder them in the SCL and SDA holes on the front side of the sensor.
    - Place the sensor facing up on the two pins of the 3-pin header; the VIN hole should be on the pin soldered to 3V3 and the GND hole should be on the pin soldered to GND. Bend the wires over to meet the two bent pins of the 5-pin header. Trim the wires if they are too long.
    - Once you're happy with the shape of the wires, solder the VIN hole on the 3V3 pin, and GND hole on the GND pin to fix it in place.
    - Solder the bent wires to the bent pins of the 5-pin header. The wire attached to the SDA hole of the sensor should be soldered to the bent pin in the GP2 hole. Likewise, the wire attached to the SCL hole of the sensor should be soldered to the bent pin in the GP3 hole.
4. AHT2x sensor #2
    - Solder the GP0, GP1, and GND pins in the SDA, SCL, and GND holes of sensor #2. Try to solder the sensor on the ends of the pins so that the VIN hole has plenty of clearance from the bent pins and wires below it.
    - Cut a 1" piece of wire and solder it in the VIN hole of the sensor. Again, try to avoid the bent pins below.
    - Bend the wire over to meet the pin protruding through the VIN hole of sensor #1.
    - Once you're happy with the shape of the bent wire, solder it in place.
    


## Software
1. Edit `example_settings.toml` with your own information and save it as `settings.toml`. Setting the value for `SENSOR_ID` is optional, this will be handled automatically in step 5.
2. Connect the Pico to your computer. Hold the BOOTSEL button down while plugging it in.
3. Run `set_up_new_pico.sh`. This script will find the latest version of CircuitPython, download it, and copy it to your Pico.
4. The Pico will automatically reboot and appear as a new drive called CIRCUITPY.
5. Run `build_and_push_to_pico.sh` to download the required libraries, push the code to your Pico, and build the CircuitPython environment. It should be running now!
