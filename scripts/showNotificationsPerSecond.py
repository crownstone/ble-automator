#!/usr/bin/env python

__author__ = 'Bart van Vliet'

import matplotlib.pyplot as plt
import optparse
import sys
import numpy as np
import time, datetime

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


	counts = []
	timestamps = {}
	ts = []
	msgData = []
	samples = {}
	with open(options.data_file, 'r') as f:
		# data = f.read()
		# print data.split('\n')
		for line in f.xreadlines():
			words = line.split()
			if (len(words) < 3):
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
			handle = int(words[3]) + int(words[4]) * 256
			datalen = int(words[5])

			if (len(words) < 6+datalen):
				break

			for i in range(6, 6+datalen):
				msgData.append(words[i])

			if (opcode == 34):
				sourceAddress = ""
				for j in range(5,-1, -1):
					sourceAddress += hex(int(msgData[j]))[2:4] + ":"
				sourceAddress = sourceAddress[0:-1]
				messageType = msgData[6:8]
				sampleTimestamp = msgData[8:12]
				firstSample = int(msgData[12]) + int(msgData[13])*256
				sampleDiffs = msgData[14:]
				if (sourceAddress in samples):
					samples[sourceAddress].append(firstSample)
				else:
					samples[sourceAddress] = [firstSample]

	print np.mean(counts)
	plt.plot(ts, counts, "o")

	plt.figure()
	for addr in samples:
		# Plot missing notifications
		x = np.array(range(0,len(samples[addr])))
		y = np.array(samples[addr]) - samples[addr][0] - x
		plt.plot(x, y, label=addr)
		plt.legend()
		plt.xlabel("received notification")
		plt.ylabel("missed notifications")

	plt.figure()
	for addr in samples:
		# Plot missing notifications
		x = np.array(range(0,len(samples[addr])))
		y = np.array(samples[addr])
		plt.plot(x, y, label=addr)
		plt.legend()
		plt.xlabel("received notification")
		plt.ylabel("notification nr")

	plt.show()