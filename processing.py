from numpy import NaN, Inf, arange, isscalar, asarray, array

import numpy as np

def peakdet(v, delta, x = None):
    maxtab = []
    mintab = []
       
    if x is None:
        x = arange(len(v))
    
    v = asarray(v)
    
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    
    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')
    
    if delta <= 0:
        sys.exit('Input argument delta must be positive')
    
    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN
    
    lookformax = True
    
    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        
        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return array(maxtab), array(mintab)

def resample(data, R):

	new_data = np.zeros((len(data)/R), dtype=np.complex128)

	for i in range(0, len(new_data)):
		new_data[i] = data[i*R]

	return new_data

def find_fft_peaks(data):

	d = resample(np.abs(data), 200)
	d = d/np.mean(d)
	fft = np.abs(np.fft.rfft(d))[2:20]
	fft = fft / np.max(fft)
	fft_peaks = peakdet(fft, 0.6)[0]
	print(fft_peaks)

	try:
		if fft_peaks[0][0] == 0:
			print("Static")
			return -1
		elif fft_peaks[0][0] > 4:
			print("Static")
			return -1
		else:
			fft_peaks = fft_peaks[0][0] + 2
	except:
		print("Exception")
		return -1
	
	#from matplotlib import pyplot as plt
	#plt.plot(fft)
	#plt.show()

	return fft_peaks