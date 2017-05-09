from gnuradio import analog, channels, gr, blocks, uhd
import numpy as np
import numpy.fft, cPickle, gzip
import time
import pickle
import scipy.signal
import adaptfilt as ad

import seaborn as sns
from matplotlib import pyplot as plt

class Radio(object):
	def __init__(self):
		self.total_time = 15
		self.samp_rate = 64000
		self.freq = 2.8e9
		self.gain = 64
		self.antenna = 'RX2'
		self.bandwidth = 10e6
		self.src = analog.sig_source_c(self.samp_rate, analog.GR_SIN_WAVE, 1000, 1, 0)
		self.snk = blocks.vector_sink_c()
		self.snk_ref = blocks.vector_sink_c()
		self.usrp_ref = uhd.usrp_source(",".join(("", "serial=F4F59F")),
										uhd.stream_args(cpu_format="fc32", channels=range(1),),)
		self.usrp_rx = uhd.usrp_source(",".join(("", "serial=F4F57F")),
										uhd.stream_args(cpu_format="fc32", channels=range(1),),)
		self.usrp_tx = uhd.usrp_sink(",".join(("", "serial=F4F597")),
										uhd.stream_args(cpu_format="fc32", channels=range(1),),)

		self._set_properties(self.usrp_ref)
		self._set_properties(self.usrp_rx)
		self._set_properties(self.usrp_tx)
		
		self.usrp_ref.set_antenna(self.antenna, 0)
		self.usrp_rx.set_antenna(self.antenna, 0)

	def _set_properties(self, usrp):
		usrp.set_samp_rate(self.samp_rate)
		usrp.set_center_freq(self.freq, 0)
		usrp.set_gain(self.gain, 0)

	def track(self):
		# Start tracking time
		self.t_start = time.time()
		self.t_end = self.t_start + self.total_time

		# Connect blocks
		self.tb = gr.top_block()
		self.tb.connect(self.src, self.usrp_tx)
		self.tb.connect(self.usrp_rx, self.snk)
		self.tb.connect(self.usrp_ref, self.snk_ref)

		self._activity_static()

		data = np.real(self._resample(self.snk.data(), 16))
		data_ref = np.real(self._resample(self.snk_ref.data(), 16))
		
		overall = self._filter(data, data_ref)
		
		#return data
		return 1

	def _filter(self, d, u, M=150):

		len_u = len(u)
		len_d = len(d)

		if len_u > len_d:
			u = u[:-(len_u - len_d)]
		elif len_d > len_u:
			d = d[:-(len_d - len_u)]

		y, e, w = ad.lms(u, d, M, 0.1)

		return y

	def _resample(self, data, div):
		k = len(data) / div
		X = np.array([data[i*div] for i in range(0, k)])
		return X

	def _activity_movement(self, count):
		while time.time() < self.t_end:
			t = time.time()
			ref = t_start + 5 * count

			if t == ref:
				print 'Starting.'
				self.tb.start()

			if t == ref + 2:
				print 'Pausing'
				self.tb.stop()
				count += 1
				print count

	def _activity_static(self):
		self.tb.start()
		while time.time() < self.t_end:
			pass

		self.tb.stop()

if "__name__" == "__main__":
	radio = Radio()
	data = radio.track()

	plt.plot(data)
	plt.show()

	#import scipy.io
	#scipy.io.savemat('data/2_breath_150', {'data': overall})