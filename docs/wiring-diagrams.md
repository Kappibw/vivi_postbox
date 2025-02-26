# Wiring Diagrams and Pin Assignments

Document your wiring details and pin assignments here.

## Suggested Connections

- **LED Ring (WS2812):**
- Data Pin: GPIO18 (with a 330–470Ω resistor)
- Power: 5V (with appropriate current capacity) + a 1000µF capacitor across 5V and GND

- **Hall Effect Sensor:**
- VCC: 5V (or 3.3V if supported)
- GND: Ground
- Signal: GPIO pin (with pull-up resistor if needed)

- **Audio Amplifier (DAOKAI MAX98357):**
- I2S BCLK, LRCLK, and DIN connected as per your I2S configuration in `/boot/config.txt`
- Speaker connected to the amplifier's output

Update this document as you finalize your wiring and pin configuration.
