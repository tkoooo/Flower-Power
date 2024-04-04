# Thalia Koutsougeras
# Raspberry Pi RS 485 Communication with Solar Tracking System
# How to code serial: https://circuitdigest.com/microcontroller-projects/rs485-serial-communication-between-arduino-and-raspberry-pi 
# https://wiki.seeedstudio.com/RS-485_Shield_for_Raspberry_Pi/ 
# https://www.circuitstate.com/tutorials/what-is-rs-485-how-to-use-max485-with-arduino-for-reliable-long-distance-serial-communication/ 
# Raspbi is the "master", and tracking system is the "slave", adn MAX485 DIP is in between
# half-duplex bc 2 wires

# run every day at a certain time: https://www.codementor.io/@gergelykovcs/how-to-run-and-schedule-python-scripts-on-raspberry-pi-n2clhe3kp 


import numpy as np 
import time
import serial
import RPi.GPIO as GPIO
from time import sleep
import datetime


def main():

    GPIO.setmode(GPIO.BOARD) #referring to the pins by the number of pin in the board
    GPIO.setup(7, GPIO.OUT, initial=GPIO.HIGH) #GPIO pin 4 (connected to DE & RE of RS-485)

    # initiate sreial class at pins GPIO14 and 15 - these are the serial connection ports
    send = serial.Serial(
        port='/dev/serial0',
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
    
    send.write(str(8)) # take off sun and return towards home position fully pointed away from the sun
    print("ERROR! cells exceeded 100C")
    sleep(5) # cool off for 30 seconds


if __name__ == "__main__":
    main()
