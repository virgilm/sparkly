#!/usr/bin/python

import math
import time
import sys
import fcntl
from AtlasI2C import (
    AtlasI2C
)

TIMEOUT = 60

def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []
    
    for i in device_address_list:
        device.set_i2c_address(i)
        try:
            response = device.query("I")
            moduletype = response.split(",")[1]
            response = device.query("name,?").split(",")[1]
            device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
        except:
            continue
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
    current = -1.0
    loop = 0
    # waiting for the reading to stabilize
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        sensor = read(device)
        time.sleep(1)
        print("Current value, sensor value: {:.2f} {:.2f}".format(current, sensor))
        if math.isclose(current, sensor, abs_tol=0.02):
            break
        current = sensor
        loop = loop + 1

    # clear previous calibration
    cmd = "cal,clear"
    print("Clearing previous calibration data... {:s}".format(cmd))
    response = device.query(cmd)
    print(response)

    # make sure calibration clear is done
    loop = 0
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        cmd = "cal,?"
        response = device.query(cmd)
        if response.startswith("Success"):
            response_array = response.split(",")
            if len(response_array) > 1:
                is_calibrated = int(response_array[1])
                if is_calibrated == 0:
                    break
        loop = loop + 1
        time.sleep(1)

    # calibrate
    if device.moduletype.lower() == "ph":
        # pH sensor require a special 3-point calibration
        # calibrate mid point
        cmd = "cal,mid,{:.2f}".format(target)
    else:
        cmd = "cal,{:.2f}".format(target)
    print("Calibrating: {:.3f} to target {:.3f}: {:s}".format(current, target, cmd))
    response = device.query(cmd)
    print(response)

    # make sure calibration clear is done
    loop = 0
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        cmd = "cal,?"
        response = device.query(cmd)
        if response.startswith("Success"):
            response_array = response.split(",")
            if len(response_array) > 1:
                is_calibrated = int(response_array[1])
                if is_calibrated == 1:
                    break
        loop = loop + 1
        time.sleep(1)

    # waiting for the read value to match the calibration target
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        sensor = read(device)
        time.sleep(1)
        if math.isclose(target, sensor, abs_tol=0.02):
            break
        print("Current value, target value: {:.3f}, {:.3f}".format(sensor, target))


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

    print("Calibrating {:s} sensor to target value {:.3f}".format(device.moduletype, target))
    
    # print_devices(device_list, device)
    
    calibrate(device, target)


if __name__ == '__main__':
    main()
