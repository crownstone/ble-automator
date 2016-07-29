#!/usr/bin/env python

__author__ = 'Bart van Vliet'

import matplotlib.pyplot as plt
import optparse
import sys
import numpy as np

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage="%prog [-v] [-f <output file>] [-t] \n\nExample:\n\t%prog -f file.txt",
									version="0.1")

		parser.add_option('-v', '--verbose',
				action="store_true",
				dest="verbose",
				help="Be verbose."
				)
		parser.add_option('-f', '--file',
				action='store',
				dest="data_file",
				type="string",
				default="data.txt",
				help='File to store the data'
				)
		parser.add_option('-t', '--timediff',
				action="store_true",
				dest="time_diff",
				help="Values are time differences between samples."
				)

		options, args = parser.parse_args()

	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)


	with open(options.data_file, 'r') as f:
		# data = f.read()
		# print data.split('\n')
		values = []
		for line in f.xreadlines():
			values.append(int(line))
		timestamps = range(0, len(values))

		# values = values[0:10000]
		# timestamps = timestamps[0:10000]

		if (not options.time_diff):
			# valuesPin1 = values[0::2]
			# valuesPin2 = values[1::2]
			# timestampsPin1 = timestamps[0::2]
			# timestampsPin2 = timestamps[1::2]
			# plt.plot(timestampsPin1, valuesPin1, "o")
			# plt.plot(timestampsPin2, valuesPin2, "o")
			plt.plot(timestamps, values, "o")
			plt.ylabel("value")
			plt.xlabel("sample")

			sp = np.fft.fft(values)
			freq = np.fft.fftfreq(len(values), d=0.01) # Sample time interval of 0.01s
			plt.figure()
			plt.plot(freq, sp.real, "o")
			plt.title("FFT - real")
			plt.figure()
			plt.plot(freq, sp.imag, "o")
			plt.title("FFT - imaginary")

			plt.figure()
			# plt.plot(timestamps[0:-1], np.diff(np.array(values)), "o")
			plt.plot(timestamps[0::2][0:-1], np.diff(np.array(values[0::2])), "o")
			plt.plot(timestamps[1::2][0:-1], np.diff(np.array(values[1::2])), "o")


		else:
			values = np.array(values)
			timeValues = values
			timeValues = values / 32768.0 * 1000.0 # RTC
			# timeValues = values / 1000.0 # HF timer
			plt.plot(timestamps, timeValues, "o", alpha=0.1)
			plt.xlabel("sample")
			plt.ylabel("time since last sample (ms)")

			plt.figure()
			numBins = np.max(values) - np.min(values)
			# norm = np.linalg.norm(timeValues)
			# plt.hist(timeValues, numBins)
			# plt.hist(timeValues, numBins, normed=True)
			weights = np.ones_like(timeValues)/len(timeValues)
			plt.hist(timeValues, numBins, weights=weights)
			plt.xlabel("time since last sample (ms)")
			# plt.ylabel("occurrences")
			plt.ylabel("probability")

			plt.figure()
			plt.plot(timestamps[0:-1], np.diff(np.array(values)), "o")

		plt.show()


	sys.exit(0)