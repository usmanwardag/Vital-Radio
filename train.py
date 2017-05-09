from gnuradio import analog, channels, gr, blocks, uhd
import numpy as np
import numpy.fft, cPickle, gzip
import time
import pickle
import scipy.signal
import adaptfilt as ad

import seaborn as sns
from matplotlib import pyplot as plt

samp_rate = 64000
freq = 3e9
gain = 64
#bandwidth = 10e6
antenna = 'RX2'

def set_properties(usrp):
	usrp.set_samp_rate(samp_rate)
	usrp.set_center_freq(freq, 0)
	usrp.set_gain(gain, 0)
	#usrp.set_bandwidth(bandwidth, 0)

# --------------- Definitions ----------------- #
src = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0)
snk = blocks.vector_sink_c()
snk_ref = blocks.vector_sink_c()

usrp_ref = uhd.usrp_source(",".join(("", "serial=F4F59F")),
		uhd.stream_args(cpu_format="fc32", channels=range(1),),)
usrp_rx = uhd.usrp_source(",".join(("", "serial=F4F57F")),
		uhd.stream_args(cpu_format="fc32", channels=range(1),),)
usrp_tx = uhd.usrp_sink(",".join(("", "serial=F4F597")),
		uhd.stream_args(cpu_format="fc32", channels=range(1),),)

set_properties(usrp_ref)
set_properties(usrp_rx)
set_properties(usrp_tx)
usrp_ref.set_antenna(antenna, 0)
usrp_rx.set_antenna(antenna, 0)

# Start tracking time
t_start = time.time()
t_end = t_start + 30

# Connect blocks
tb = gr.top_block()
tb.connect(src, usrp_tx)
tb.connect(usrp_rx, snk)
tb.connect(usrp_ref, snk_ref)

count = 1

# -------------- End Definitions --------------------- #
     
def filter(u, d=None, M=150):
	"""
	Parameters
	----------
	u : array-like
		One-dimensional filter input - surveillance signal

	d : array-like
		Desired output - reference signal
		If d is None, a sinusoid of 1KHz is assumed.

	M : int
		Number of filter taps

	Returns
	-------
	e : array-like
		Returns error signal which corresponds to variations
		caused by human movement

	"""
	if d is None:
		t = np.linspace(-np.pi, np.pi, len(u))
		d = np.sin(1000*2*np.pi*t)
		#d = scipy.signal.square(1000*2*np.pi*t)

	len_u = len(u)
	len_d = len(d)

	if len_u > len_d:
		u = u[:-(len_u - len_d)]
	elif len_d > len_u:
		d = d[:-(len_d - len_u)]

	y, e, w = ad.lms(u, d, M, 0.1)

	return y

def plot(data):
	plt.plot(data)
	plt.show()

def resample(data, div):
	k = len(data) / div
	X = np.array([data[i*div] for i in range(0, k)])
	return X

def activity_movement(count):
	while time.time() < t_end:
		t = time.time()
		ref = t_start + 5 * count

		if t == ref:
			print 'Starting.'
			tb.start()

		if t == ref + 2:
			print 'Pausing'
			tb.stop()
			count += 1
			print count

def activity_static():
	tb.start()
	while time.time() < t_end:
		pass

	tb.stop()

activity_static()
#activity_movement(count)
data_real = np.real(resample(snk.data(), 16))
data_imag = np.imag(resample(snk.data(), 16))
data_ref_real = np.real(resample(snk_ref.data(), 16))
data_ref_imag = np.imag(resample(snk_ref.data(), 16))
overall_real = filter(data_real, data_ref_real)
overall_imag = filter(data_imag, data_ref_imag)

print len(data_real), len(data_imag), len(data_ref_real), len(data_ref_imag)


#overall_real = overall_real[~np.isnan(overall_real)]
#overall_imag = overall_imag[~np.isnan(overall_imag)]

overall = overall_real + 1j* overall_imag
print len(data_ref_real)

plot(overall_real)

import scipy.io
scipy.io.savemat('data/2_breath_150', {'data': overall})