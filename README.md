## Hello all.

This middle complexity house control smart assistant based on the raspberry.
It supports interface over web, telegram messenger, voice
It alerting over telegram messenger, mail, voice.
Because I got 2 raspberry one at the house and one at the flat - there are 2 configs.

dependencies:
sudo python3 -m pip install flask pyserial numpy pygame picamera feedparser wiringpi ppretty
sudo python3 -m pip install gunicorn PySocks urllib3 requests
sudo python3 -m pip install pyaudio matplotlib pyTelegramBotAPI Adafruit_Python_DHT requests[socks] wakeonlan validators
sudo python3 -m pip install gTTS gtts SpeechRecognition pyttsx pyttsx3 dateparser yandex_speech babel pyowm soundfile russian-numerals transliterate noisereduce numba-0.56.4
sudo python3 -m pip install nextion
sudo python3 -m pip install vosk sounddevice soundfile
sudo python3 -m pip install openai
sudo python3 -m pip install torch==1.13.1 torchaudio==0.13.1 omegaconf
sudo python3 -m pip install pyalsaaudio
sudo python3 -m pip install cython

# Currently I have hardware:

    sensors :
        - DHT22 - for temperature and humidity (actually I can read temperature from CO2 sensor)
        - MH-Z19 - CO2 sensor
        - PMS7003 - particles sensor
        - light - standard raspberry light sensor
        - moisture - standard raspberry moisture sensor
        - waterlevel - standard respberry waterdrop sensor

    devices:
        - raspberry camera/ USB camera
        - outlet 220V - general purpoise
        - IR transceiver for control conditioner
        - Fan on the heater to increase temperature in the room if needed (12V)
        - plant watering engine (5V)
        - WOL wake up pc over telegram

    for voice control:
        - USB connected jabra speaker - it got good noise reduction for task

    for display:
        - nextion display on uart for display current values
            nextion project in nextion_project folder

    Pinout of sensor board (DHT22, MH-Z19, PMS7003)

    RJ45 connector bottom view:
                UART TX UART            3.3V
                UART RX                 GND
    Board->     UART CS0 (GPIO 18)      5V                      -> Cable
                UART CS1 (GPIO 23)      DHT22 data GPIO4

    UART3 (PL011) TX3 - GPIO 4, RX3 - GPIO 5 (dtoverlay=uart3)
    UART        CS0   CS1
                0     0 - CO2 sensor A0, B0
                0     1 - nextion display A1, B1
                1     0 - particles A2, B2


Photos of interface:
    ![alt text](https://github.com/AMV007/raspberry_house_control/blob/master/readme/image1.png)
    ![alt text](https://github.com/AMV007/raspberry_house_control/blob/master/readme/image2.png)
    ![alt text](https://github.com/AMV007/raspberry_house_control/blob/master/readme/image3.png)

