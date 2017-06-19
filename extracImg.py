import wearing_devices as wd
import os
from PIL import Image

for file in os.listdir('.'):
	fn, extFn = os.path.splitext(file)
	if extFn != '.p' and extFn != '.py':
		img = Image.open(file).convert('RGB').resize((640, 360))
		imgCorrected = wd.equalize(img)
		imgCa = wd.posterize(imgCorrected, 4)
		imgCa.save('p;osterized/' + fn + '_posterized' + extFn)
		imgCa.show()
		

