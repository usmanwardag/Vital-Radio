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
		self.total_time = 10
		self.samp_rate = 64000
		self.freq = 3e9
		self.gain = 64
		self.antenna = 'RX2'
		self.bandwidth = 10e6
		self.snk = blocks.vector_sink_c()
		self.usrp_rx = uhd.usrp_source(",".join(("", "serial=F4F597")),
							uhd.stream_args(cpu_format="fc32", channels=range(1),),)
		
		self._set_properties(self.usrp_rx)
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
		self.tb.connect(self.usrp_rx, self.snk)
		
		self._activity_static()

		data = np.real(self._resample(self.snk.data(), 16))
		
		return len(data)

	def _resample(self, data, div):
		k = len(data) / div
		X = np.array([data[i*div] for i in range(0, k)])
		return X

	def _activity_static(self):
		self.tb.start()
		while time.time() < self.t_end:
			pass

		self.tb.stop()

if __name__ == "__main__":
	radio = Radio()
	data = radio.track()

	plt.plot(data)
	plt.show()

	#import scipy.io
	#scipy.io.savemat('data/2_breath_150', {'data': overall})