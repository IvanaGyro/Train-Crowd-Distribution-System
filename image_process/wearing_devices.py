from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
import operator
import time
import os
import sys
import pickle
import numpy as np
import cv2

sys.setrecursionlimit(10000000)
print sys.getrecursionlimit()

def test_run_time(func):
	def newFunc(*args, **kwargs):
		start = time.time()
		result = func(*args, **kwargs)
		print func.__name__, 'uses', time.time() - start, 'secs'
		return result
	return newFunc

def static_vars(**kwargs):
	def decorate(func):
		for k in kwargs:
			setattr(func, k, kwargs[k])
		return func
	return decorate


def get_hist_img(img):
	# RGB Hitogram
	# This script will create a histogram image based on the RGB content of
	# an image. It uses PIL to do most of the donkey work but then we just
	# draw a pretty graph out of it.
	#
	# May 2009,  Scott McDonough, www.scottmcdonough.co.uk
	
	histHeight = 120            # Height of the histogram
	histWidth = 256             # Width of the histogram
	multiplerValue = 0.9        # The multiplier value basically increases
	                            # the histogram height so that love values
	                            # are easier to see, this in effect chops off
	                            # the top of the histogram.
	showFstopLines = True       # True/False to hide outline
	fStopLines = 5
	
	# Colours to be used
	backgroundColor = (51,51,51)    # Background color
	lineColor = (102,102,102)       # Line color of fStop Markers 
	red = (255,60,60)               # Color for the red lines
	green = (51,204,51)             # Color for the green lines
	blue = (0,102,255)              # Color for the blue lines
	
	##################################################################################
	
	img = img.convert("RGB")
	hist = img.histogram()
	histMax = max(hist)                                     #comon color
	xScale = float(histWidth)/len(hist)                     # xScaling
	yScale = float((histHeight)*multiplerValue)/histMax     # yScaling 
	
	im = Image.new("RGBA", (histWidth, histHeight), backgroundColor)   
	draw = ImageDraw.Draw(im)
	
	# Draw Outline is required
	if showFstopLines:    
	    xmarker = histWidth/fStopLines
	    x =0
	    for i in range(1,fStopLines+1):
	        draw.line((x, 0, x, histHeight), fill=lineColor)
	        x+=xmarker
	    draw.line((histWidth-1, 0, histWidth-1, 200), fill=lineColor)
	    draw.line((0, 0, 0, histHeight), fill=lineColor)
	
	# Draw the RGB histogram lines
	x=0; c=0;
	for i in hist:
	    if int(i)==0: pass
	    else:
	        color = red
	        if c>255: color = green
	        if c>511: color = blue
	        draw.line((x, histHeight, x, histHeight-(i*yScale)), fill=color)        
	    if x>255: x=0
	    else: x+=1
	    c+=1
	
	return im
	
def proportion_resize(img, prop):
	return img.resize((int(img.size[0]*prop), int(img.size[1]*prop)))

def equalize(img):
    h = img.histogram()
    lut = []
    for b in range(0, len(h), 256):
        # step size
        step = reduce(operator.add, h[b:b+256]) / 255
        # create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n / step)
            n = n + h[i+b]
    im = img.point(lut)
    return im
    
def posterize(img, level):
	lut = []
	for b in range(0, len(img.histogram()), 256):
		for i in range(level):
			lower = 256*i/level
			upper = 256*(i+1)/level
			lut[lower + b:upper + b] = [(lower + upper)/2]*(upper - lower)
	im = img.point(lut)
	return im

@static_vars(pixelStack=[])
def find_same_color(img, pixelTb, x, y, area):
	if pixelTb[y][x]:
		find_same_color.pixelStack.append((x, y))
		while len(find_same_color.pixelStack):
			x, y = find_same_color.pixelStack.pop()
			if pixelTb[y][x]:
				pixelTb[y][x] = 0
				area += 1
				if y + 1 < img.shape[0]:
					if pixelTb[y + 1][x]:
						if img[y + 1][x] == img[y][x]:
							find_same_color.pixelStack.append((x, y + 1))
				if x + 1 < img.shape[1]:
					if pixelTb[y][x + 1]:
						if img[y][x + 1] == img[y][x]:
							find_same_color.pixelStack.append((x + 1, y))
				if y > 0:
					if pixelTb[y - 1][x]:
						if img[y - 1][x] == img[y][x]:
							find_same_color.pixelStack.append((x, y - 1))
				if x > 0:
					if pixelTb[y][x - 1]:
						if img[y][x - 1] == img[y][x]:
							find_same_color.pixelStack.append((x - 1, y))
	return area 
			
def find_same_color2(img, pixelTb, x, y, area):
	if pixelTb[y][x]:
		pixelTb[y][x] = 0
		area += 1
		if x > 0:
			if pixelTb[y][x - 1]:
				if img[y][x - 1] == img[y][x]:
				 	area = find_same_color(img, pixelTb, x - 1, y, area)
		if y > 0:
			if pixelTb[y -1][x]:
				if img[y - 1][x] == img[y][x]:
				 	area = find_same_color(img, pixelTb, x, y - 1, area)
		if x + 1 < img.shape[1]:
			if pixelTb[y][x + 1]:
				if img[y][x + 1] == img[y][x]:
					area = find_same_color(img, pixelTb, x + 1, y, area)
		if y + 1 < img.shape[0]:
			if pixelTb[y + 1][x]:
				if img[y + 1][x] == img[y][x]:
					area = find_same_color(img, pixelTb, x, y + 1, area)
	return area

@test_run_time
def get_block_size_ls(imagePath, resize=(640, 360), postLv=4):
	img = Image.open(imagePath).convert('RGB')
	if img.size != resize:
		print '%s is resized from %s to %s' %(imagePath, img.size, resize)
		img = img.resize((640, 360))

	imgCorrected = equalize(img)
	npim = np.array(imgCorrected) #trans to np
	cvblur = cv2.medianBlur(npim, 7)
	imgblur = Image.fromarray(cvblur) #trans back
	imgCa = posterize(imgblur, 4)
	imgCaArr = np.empty((resize[1], resize[0]), dtype='uint32')
	for y in range(imgCaArr.shape[0]):
		for x in range(imgCaArr.shape[1]):
			color = imgCa.getpixel((x, y))
			imgCaArr[y][x] = (color[0] << 16) | (color[1] << 8) | (color[2])
	sizeLs = []
	pixelTb = np.ones((imgCaArr.shape[0], imgCaArr.shape[1]), dtype='uint8')
	for y in range(imgCaArr.shape[0]):
		for x in range(imgCaArr.shape[1]):
			area = find_same_color(imgCaArr, pixelTb, x, y, 0)
			if area:
				sizeLs.append(area)
	pixelNum = reduce(operator.add, sizeLs)
	if pixelNum != imgCa.size[0] * imgCa.size[1]:
		print 'pixelNum:', pixelNum
		print 'pixel:', imgCa.size[0] * imgCa.size[1]
		imgCa.show()
		tmpImg = Image.new('1', resize, color=1)
		for y in range(resize[1]):
			for x in range(resize[0]):
				if not pixelTb[y][x]:
					tmpImg.putpixel((x, y), 0)
		tmpImg.show()
		raise Exception('Error in find_same_color()')
	print 'Complete to count the sizes of all blobs'
	return sizeLs

if __name__ == '__main__':
	reWidth = 640
	reHeight = 360
	postLv = 4

	for file in os.listdir('.'):
		if not os.path.isfile(file):
			continue
		fn, extFn = os.path.splitext(file)
		if extFn in ['.jpg', '.png']:
			imagePath = file
			sizeLs = get_block_size_ls(imagePath, (reWidth, reHeight), postLv)
			with open('%s-%s_%s-%s.p' %(os.path.splitext(imagePath)[0], reWidth, reHeight, postLv), 'wb') as fd:
				pickle.dump(sizeLs, fd)
			print 'Successfully dump the list of sizes of color blocks.'
			print
#im = get_hist_img(img)
#im2 = get_hist_img(imgCorrected)
#im3 = get_hist_img(imgCa)
#proportion_resize(img, 0.2).show()
#proportion_resize(im, 1.5).show()
#proportion_resize(imgCorrected, 0.2).show()
#proportion_resize(im2, 1.5).show()
#proportion_resize(imgCa, 0.2).show()
#proportion_resize(im3, 1.5).show()