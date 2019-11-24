Hello all.

This is not simple house control on raspberry.
It supports interface over web, telegram messenger, voice
It alerting over telegram messenger, mail, voice.
Because I got 2 raspberry one at the house and one at the flat - there are 2 configs.

Currently I have hardware:

    sensors : 
        - DHT22 - for temperature and humidity (actually I can read temperature from CO2 sensor)
        - MH-Z19 - CO2 sensor
        - PMS7003 - particles sensor
        - light - standard raspberry light sensor
        - moisture - standard raspberry moisture sensor
        - waterlevel - standard respberry waterdrop sensor

    devices:
        - raspberry camera
        - outlet 220V - general purpoise
        - IR transceiver for control conditioner
        - Fan on the heater to increase temperature in the room if needed (12V)
        - plant watering engine (5V)

    for voice control:
        - USB connected jabra speaker - it got good noise reduction for task

Additional possibility:
    - wake up pc over telegram

    Pinout of sensor board (DHT22, MH-Z19, PMS7003):
        - 1 - GND (white-green)
        - 2 - 5V (green)
        - 3 - TXD0 (uart, white-blue)
        - 4 - RXD0 (uart, blue)
        - 5 - DHT22 data (GPIO4, white-brown)
        - 6 - UART switch between CO2 and particles (low - CO2, high - particles) (GPIO27, brown)
        - 7 - sleep particles sensor (GPIO13) (white-orange)
        - 8 - 3.3V (orange)

Photos of interface: 
    ![alt text](https://github.com/AMV007/raspberry_house_control/blob/master/readme/image1.png)
    ![alt text](https://github.com/AMV007/raspberry_house_control/blob/master/readme/image2.png)
    ![alt text](https://github.com/AMV007/raspberry_house_control/blob/master/readme/image3.png)

