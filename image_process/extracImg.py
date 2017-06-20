import wearing_devices as wd
import cv2
import os , fnmatch
import numpy as np
from PIL import Image

for file in fnmatch.filter(os.listdir('.'), '*.jpg'):
	fn, extFn = os.path.splitext(file)
	if extFn != '.p' and extFn != '.py':
		img = Image.open(file).convert('RGB').resize((640, 360))
		imgCorrected = wd.equalize(img)
		npim = np.array(imgCorrected) #trans to np
		cvblur = cv2.medianBlur(npim, 3)
		imgblur = Image.fromarray(cvblur) #trans back
		imgCa = wd.posterize(imgblur, 4)
		imgCa.save('posterized/' + fn + '_posterized' + extFn)
		imgCa.show()