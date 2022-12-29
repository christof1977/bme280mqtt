#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
UDP Serveri for aquiring data from the Bosch sensor BME280
Sensor is connected to Rapsi Pi via I2C Bus 1, Addr. 0x76.
Server opens an UDP socket on port 5023 (changeable) and waits for incoming JSON requests.

Valid requests:
{"command" : "getTemperature"}
{"command" : "getHumidity"}
{"command" : "getPressure"}

The answers are then:
{"answer":"getTemperature","value":"19.56 C"})
{"answer":"getHumidity","value":"32.15% rH"})
{"answer":"getPressure","value":"992.38 hPa"})
'''


import smbus2
import bme280
#import socket
import time
import json
import syslog
#import threading
#from threading import Thread
import logging
from datetime import datetime
import paho.mqtt.publish as publish
from config import MQTTHOST, MQTTUSER, MQTTPASS, FLOOR, ROOM, DEVICE, INTERVAL


bme280_address = 0x76
udp_port = 6664

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


#class bme280mqtt(threading.Thread):
class bme280mqtt():
    def __init__(self):
        #threading.Thread.__init__(self)
        #self.t_stop = threading.Event()

        self.mqtthost = MQTTHOST
        self.mqttuser = MQTTUSER
        self.mqttpass = MQTTPASS
        self.topic = FLOOR + "/" + ROOM + "/" + DEVICE


        self.bus = smbus2.SMBus(1)
        self.calibration_params = bme280.load_calibration_params(self.bus, bme280_address)

        #while(not self.t_stop.is_set()):
        while True:
            now = datetime.now().replace(microsecond=0).isoformat()
            msg = {"Time":now, "BME280":{"Id":DEVICE,
                                         "Temperature":self.get_temperature(),
                                         "Humidity":self.get_humidity(),
                                         "Pressure":self.get_pressure()},
                                         "TempUnit":"C"}
            msg = json.dumps(msg)
            publish.single(self.topic+"/SENSOR", msg, hostname=self.mqtthost, client_id=DEVICE,auth = {"username":self.mqttuser, "password":self.mqttpass})
            #publish.single("EG/Wohnzimmer/Pressure", self.get_pressure(), hostname=self.mqtthost, client_id=self.hostname,auth = {"username":self.mqttuser, "password":self.mqttpass})
            ##publish.single("EG/Wohnzimmer/Humidity", self.get_humidity(), hostname=self.mqtthost, client_id=self.hostname,auth = {"username":self.mqttuser, "password":self.mqttpass})
            #self.t_stop.wait(INTERVAL)
            time.sleep(INTERVAL)

    def get_sensor_data(self):
        data = bme280.sample(self.bus, bme280_address, self.calibration_params)
        logging.debug(data)
        return(data)

    def get_temperature(self):
        data = self.get_sensor_data()
        return(round(data.temperature,1))

    def get_humidity(self):
        data = self.get_sensor_data()
        return(round(data.humidity,1))

    def get_pressure(self):
        data = self.get_sensor_data()
        return(round(data.pressure,1))

    def get_temperature_str(self):
        data = self.get_sensor_data()
        ret = json.dumps({"answer":"getTemperature","value":str(round(data.temperature,1))+" C"})
        return(ret)

    def get_humidity_str(self):
        data = self.get_sensor_data()
        return(json.dumps({"answer":"getHumidity","value":str(round(data.humidity,1))+"% rH"}))

    def get_pressure_str(self):
        data = self.get_sensor_data()
        return(json.dumps({"answer":"getPressure","value":str(round(data.pressure,1))+" hPa"}))

    def run(self):
        while True:
            try:
                time.sleep(1)
                pass
            except KeyboardInterrupt: # CTRL+C exiti
                self.stop()
                break



if __name__ == "__main__":
    Bme280 = bme280mqtt()
    Bme280.start()
    #steuerung.run()
