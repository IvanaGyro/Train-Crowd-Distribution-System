import pickle
import os
from PIL import Image
import numpy as np
import operator
from math import *
from matplotlib import pyplot as plt

threshold = 1024
dataDc = {}
for file in os.listdir('.'):
	if not os.path.isfile(file):
		continue
	print file
	data = {}
	fn, extFn = os.path.splitext(file)
	if extFn == '.py':
		continue
	if extFn == '.p':
		fn, res, data['PostLv'] = fn.split('-')
		data['Res'] = tuple(int(val) for val in res.split('_'))
		with open(file, 'rb') as fd:		
			data['BlkSizes'] = pickle.load(fd)
	else:
		data['ImgFn'] = file
	if fn not in dataDc:
		dataDc[fn] = data
	else:
		dataDc[fn].update(data)

maxRes = max([ data['Res'][0] * data['Res'][1] for fn, data in dataDc.iteritems() ])
bins = [ 2**i for i in range( 0, int(ceil(log(maxRes, 2)))+1 ) ]
print 'bins:', bins
for fn, data in dataDc.iteritems():
	quietSizeLs = filter(lambda a: a >= threshold, data['BlkSizes'])
	data['QuietBlkSizes'] = quietSizeLs
	Image.open(data['ImgFn']).resize(data['Res']).show()
	data['QuietMean'] = np.mean(quietSizeLs)
	data['QuietStd'] = np.std(quietSizeLs)
	data['QuietVar'] = np.var(quietSizeLs)
	data['QuietMax'] = max(quietSizeLs)
	data['QuietMin'] = min(quietSizeLs)
	data['QuietHist'], data['Bins'] = np.histogram(quietSizeLs, bins=bins)
	print 'filename:', fn
	print 'mean:', data['QuietMean']
	print 'std:', data['QuietStd']
	print 'var:', data['QuietVar']
	print 'max:', data['QuietMax']
	print 'min:', data['QuietMin']
	print 'log-hist:', data['QuietHist']
	print 'len:', len(quietSizeLs)
	print
	
plt.clf()
plt.figure(figsize=(16, 9))
plt.xscale('log')
#plt.yscale('log')
plt.hist([ data['QuietBlkSizes'] for fn, data in dataDc.iteritems() ], bins=bins, label=[ '%s-%s-%s' %(fn, int(data['QuietMean']), int(data['QuietStd'])) for fn, data in dataDc.iteritems() ])
plt.title('All')
plt.legend(loc='upper right')
plt.show()

