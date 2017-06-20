import requests
import os
srcFn = os.path.join('..', '0-IMAG3158.jpg')
srcBin = open(srcFn, 'rb').read()
#srcBin = requests.get('http://local.host:8080/?action=snapshot').raw
destFn = '0-IMAG3158.jpg'
files = {'pic': (destFn, srcBin, 'image/jpeg')}
r = requests.post("http://192.168.1.59:8080/?action=calcu", files=files)
print r.status_code, r.text