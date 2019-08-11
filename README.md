# RPI Stacker

## Prerequisites
* Raspberry Pi (I've used the 3B model but other models that has SPI is fine)
* 8 x 8 LED Dot Matrix with MAX7219

## Installation
1. Install the libraries defined from `requirements.txt`
```
$ sudo pip3 install -r requirements.txt
```

2. Make sure SPI is enabled on your Raspberry Pi. If not follow the instructions [here](https://luma-led-matrix.readthedocs.io/en/latest/install.html).

3. Connect the GPIO pins of you Raspberry Pi to MAX7219
| MAX7219| RPi GPIO|
|-------:|--------:|
|     VCC|        2|
|     GND|        6|
|     DIN|       19|
|      CS|       24|
|     CLK|       23|

4. Play!
```
$ ./stacker.py
```

