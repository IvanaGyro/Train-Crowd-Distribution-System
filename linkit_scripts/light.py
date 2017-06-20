#!/usr/bin/python
import requests
import serial
import time
import json

srvIP = '192.168.1.59'
srvPort = 8080

s = None
def setup():
		global s
		#Serial 57600
		s = serial.Serial("/dev/ttyS0", 57600)

def loop():
	response = requests.get('http://%s:%s/?action=light' %(srvIP, srvPort)).content
	crowdLv = int(json.loads(response)['crowd_level'])
	if crowdLv < 20:
		s.write('\0')
	elif crowdLv < 40:
		s.write('\1')
	elif crowdLv < 60:
		s.write('\2')
	else:
		s.write('\3')
	time.sleep(1)

setup()
while True:
		loop()
