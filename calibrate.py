#!/usr/bin/python

import time
import sys
import fcntl
from AtlasI2C import (
    AtlasI2C
)

def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []
    
    for i in device_address_list:
        device.set_i2c_address(i)
        response = device.query("I")
        moduletype = response.split(",")[1] 
        response = device.query("name,?").split(",")[1]
        device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
    return device_list 

def print_devices(device_list, device):
    for i in device_list:
        if(i == device):
            print("--> " + i.get_device_info())
        else:
            print(" - " + i.get_device_info())

def get_device(device_list, name):
    for device in device_list:
        if (device.moduletype.lower() == name.lower()):
            return device
    return None


def calibrate(device, target):
    current = 0.0
    # waiting for the reading to stabilize
    while True:
        sensor = read(device)
        print("Current value, sensor value: {:.2f} {:.2f}".format(current, sensor))
        if current == sensor:
            break
        current = sensor
        time.sleep(1)

    cmd = "cal,clear\r"
    print("Clearing previous calibration data... {:s}".format(cmd))
    response = device.query(cmd)
    print(response)

    if device.moduletype.lower() == "ph":
        # pH sensor require a special 3-point calibration
        # calibrate mid point
        cmd = "cal,mid,{:.2f}\r".format(target)
    else:
        cmd = "cal,{:.2f}\r".format(target)
    print("Calibrating: {:.2f} to target {:.2f}: {:s}".format(current, target, cmd))
    response = device.query(cmd)
    print(response)

    # waiting for the read value to match the calibration target
    while True:
        sensor = read(device)
        if target == sensor:
            break
        print("Current value, target value: {:.2f}, {:.2f}".format(sensor, target))
        time.sleep(1)


def read(device):
    response = device.query("R")
    print("Sensor response: %s" % response)
    if response.startswith("Success"):
        try:
            floatVal = float(response.split(":")[1])
            print("OK [" + str(floatVal) + "]")
            return floatVal
        except:
            return 0.0
    else:
        return 0.0

def main():
    if len(sys.argv) != 3:
	print("Usage: calibrate.py <sensor_name> <target_value>")
	exit()
    target = float(sys.argv[2])

    device_list = get_devices()

    print_devices(device_list, device_list[0])
    
    # choose device based on name
    device = get_device(device_list, sys.argv[1])
    if device == None:
	print("Sensor named {:s} not found!".format(sys.argv[1]))
	exit()

    print("Calibrating {:s} sensor to target value {:.2f}".format(device.moduletype, target))
    
    # print_devices(device_list, device)
    
    calibrate(device, target)


if __name__ == '__main__':
    main()
