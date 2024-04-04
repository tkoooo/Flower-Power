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
from pymodbus.client.sync import ModbusSerialClient


def main():

    # OLD CODE WITH PYSERIAL
    """
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
    """


    # basic starter code taken from https://stackoverflow.com/questions/70686813/how-to-access-particular-registers-using-pymodbus-rtu 
    client = ModbusSerialClient(
        port='/dev/serial0',
        startbit=1,
        databits=8,
        parity="N",
        stopbits=1,
        errorcheck="crc",
        baudrate=9600,
        method="RTU",
        timeout=3,
    )

    if client.connect():  # Trying for connect to Modbus slave
        # ONLINE CODE
        # Read holding register
        print("Connection Successful")
        res = client.read_holding_registers(address=53, count=1, unit=1)

        # Where "address" is register address
        # Where "count" is the number of registers to read
        # Where "unit" is the slave address, found in vendor documentation
        print(res)
        client.close()

        # -------------------------------------------------------------------------------
        # MY CODE
        # I will need to write to a register: function code 0x06
        # I want to write to register (integer value) not a coil (single bit on/off)
        # I think in the tracker manual, 40006.8 means register 40006 code 8
        # documentation from: https://readthedocs.org/projects/pymodbus/downloads/pdf/latest/ 
        """
        write_register(address: int, value: int, slave: int = 0, **kwargs: Any) → T
        Write register (code 0x06).
        Parameters
        • address – Address to write to
        • value – Value to write
        • slave – (optional) Modbus slave ID
        • kwargs – (optional) Experimental parameters.
        Raises
        ModbusException –
        """

        # new code - these expect integer values
        print("Connection Successful")
        address = int(0x40006) # this register from manual - may need a different one
        value = 8 # this code under this register
        slave = 6 #(number from 1-255) - i got this from the solar tracker
        res = client.write_register(address, value, slave)
        print(res)
        client.close()
        

    else:
        print("Failed to connect to Modbus device")

    sleep(3)


if __name__ == "__main__":
    main()