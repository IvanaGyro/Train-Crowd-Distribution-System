import requests
import os
import time

def time_string():
	t = time.time()
	tInt = int(t)
	tNs =  t - tInt
	tStr = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(tInt)) + '.' + ('%.6f' %(tNs))[2:]
	return tStr
destIP = '192.168.1.59'
destPort = 8080
#srcFn = os.path.join('..', '0-IMAG3158.jpg')
#srcBin = open(srcFn, 'rb').read()
srcBin = requests.get('http://localhost:8080/?action=snapshot').content
destFn = time_string() + '.jpg'
files = {'pic': (destFn, srcBin, 'image/jpeg')}
r = requests.post('http://%s:%s/?action=calcu' %(destIP, destPort), files=files)
print r.status_code, r.text