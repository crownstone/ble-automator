#!/usr/bin/env python

__author__ = 'Bart van Vliet'

import matplotlib.pyplot as plt
import optparse
import sys
import numpy as np
import time, datetime
from ConversionUtils import *

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage="%prog [-v] [-f <input file>] [-t] \n\nExample:\n\t%prog -f file.txt",
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
				help='File to get the data from'
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


	counts = []
	timestamps = {}
	ts = []
	msgData = []
	powerSamples = {}
	with open(options.data_file, 'r') as f:
		# data = f.read()
		# print data.split('\n')
		for line in f.xreadlines():
			words = line.split()
			if (len(words) < 2):
				continue
			if (len(words) < 6):
				break
			timestampStr = words[0] + " " + words[1]
			timestamp = time.mktime(datetime.datetime.strptime(timestampStr, "%I:%M:%S %f").timetuple())
			if (timestamp in timestamps):
				counts[timestamps[timestamp]] += 1
			else:
				timestamps[timestamp] = len(timestamps)
				counts.append(1)
				ts.append(timestamp)

			opcode = int(words[2])
			if (opcode == 32):
				msgData = []
			handle = Conversion.uint8_to_uint16(int(words[3]), int(words[4]))
			datalen = int(words[5])

			if (len(words) < 6+datalen):
				break

			for i in range(6, 6+datalen):
				msgData.append(int(words[i]))

			if (opcode == 34):
				sourceAddress = ""
				for j in range(5,-1, -1):
					sourceAddress += hex(msgData[j])[2:4] + ":"
				sourceAddress = sourceAddress[0:-1]
				messageType = Conversion.uint8_array_to_uint16(msgData[6:8])
				sampleTimestamp = Conversion.uint8_array_to_uint32(msgData[8:12])
				# firstSample = Conversion.uint8_array_to_uint16(msgData[12:14])
				# sampleDiffs = msgData[14:]
				# samples = [firstSample]
				# for i in range(0, len(sampleDiffs)):
				# 	samples.append(samples[i] + Conversion.uint8_to_int8(sampleDiffs[i]))
				samples = Conversion.uint8_array_to_uint16_array(msgData[12:99])

				if (sourceAddress in powerSamples):
					powerSamples[sourceAddress].extend(samples)
				else:
					powerSamples[sourceAddress] = samples
				# print msgData
				# print samples

	# print np.mean(counts)
	# plt.plot(ts, counts, "o")

	plt.figure()
	for addr in powerSamples:
		# # Plot missing notifications
		# x = np.array(range(0, len(powerSamples[addr])))
		# y = np.array(powerSamples[addr]) - powerSamples[addr][0] - x
		# plt.plot(x, y, label=addr)
		# plt.legend()
		# plt.xlabel("received notification")
		# plt.ylabel("missed notifications")

		# Plot received power samples
		plt.plot(range(0,len(powerSamples[addr])), powerSamples[addr], "o")

	plt.show()