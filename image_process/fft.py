import cv2
from PIL import Image
import wearing_devices as wd
import numpy as np
import os, fnmatch
from matplotlib import pyplot as plt

for file in fnmatch.filter(os.listdir('.'), '*.jpg'):
	fn, extFn = os.path.splitext(file)
	if extFn != '.p' and extFn != '.py':
		img = cv2.imread(file,0) # 1 = color, 0 = grayscale
		pim = Image.fromarray(img)
		imgCorrected = wd.equalize(pim)
		inal = cv2.medianBlur(source, 3)
		pix = np.array(imgCorrected)
		f = np.fft.fft2(pix)
		fshift = np.fft.fftshift(f)
		magnitude_spectrum = 20*np.log(np.abs(fshift))

		plt.subplot(121),plt.imshow(pix, cmap = 'gray')
		plt.title('Input Image'), plt.xticks([]), plt.yticks([])
		plt.subplot(122),plt.imshow(magnitude_spectrum, cmap = 'gray')
		plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
		plt.show()

		#imgCa = wd.posterize(imgCorrected, 4)
