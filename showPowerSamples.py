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
		parser = optparse.OptionParser(usage="%prog [-v] [-f <input file>] \n\nExample:\n\t%prog -f file.txt",
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

		options, args = parser.parse_args()

	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)


	# First calibrate voltageMultiplication, then currentMultiplication and pZero
	voltageMultiplications = {"default":2.374,
							  "E3:F5:C5:FF:23:40":2.340,
							  "E5:20:4D:1D:CD:6C":2.35,
							  "FB:8D:71:D5:6B:C1":2.35,
							  "CF:75:73:30:69:86":2.62, #2.59
							  "CD:0D:98:06:6A:42":2.44,
							  }
	currentMultiplications = {"default":0.044,
							  "E3:F5:C5:FF:23:40":0.0455,
							  "E5:20:4D:1D:CD:6C":0.0470,
							  "FB:8D:71:D5:6B:C1":0.0462,
							  "CF:75:73:30:69:86":0.030, #0.0325
							  "CD:0D:98:06:6A:42":0.0455,
							  }
	pZeros = {"default":9.0,
			  "E3:F5:C5:FF:23:40":7.8,
			  "E5:20:4D:1D:CD:6C":8.4,
			  "FB:8D:71:D5:6B:C1":7.4,
			  "CF:75:73:30:69:86":7.7, #9.8
			  "CD:0D:98:06:6A:42":7.0,
			  }





	currentSamplesAll = []
	currentTimestampsAll = []
	voltageSamplesAll = []
	voltageTimestampsAll = []

	currentMinMeanMax = {"time":[], "min":[], "mean":[], "max":[]}
	voltageMinMeanMax = {"time":[], "min":[], "mean":[], "max":[]}

	voltageDiffAll = {"time":[], "val":[]}
	currentSamplesDiffAll = {"time":[], "val":[]}

	voltageTops = {"time":[], "val":[]}
	voltageTimeBetweenTops = {"time":[], "val":[]}

	voltageZeroes = {"time":[], "val":[]}
	voltageTimeBetweenZeroes = {"time":[], "val":[]}

	power = {"time":[], "val":[]}

	with open(options.data_file, 'r') as f:
		# data = f.read()
		# print data.split('\n')
		for line in f.xreadlines():
			words = line.split()
			if (len(words) < 10):
				continue
			# if (len(words) < 6):
			# 	break
			timestamp = float(words[0])
			address = words[1]

			powerSamplesStruct = list(int(x) for x in words[4:])
			# if (len(powerSamplesStruct) < 502):
			if (len(powerSamplesStruct) < 472):
				continue

			ind = 0
			currentSamplesLength = Conversion.uint8_array_to_uint16(powerSamplesStruct[ind:ind+2])
			ind += 2
			if (len(powerSamplesStruct[ind:]) < currentSamplesLength*2):
#				break
				continue
			currents = Conversion.uint8_array_to_uint16_array(powerSamplesStruct[ind:ind + currentSamplesLength * 2])
			ind += currentSamplesLength*2
			# print currents

			voltageSamplesLength = Conversion.uint8_array_to_uint16(powerSamplesStruct[ind:ind+2])
			ind += 2
			if (len(powerSamplesStruct[ind:]) < voltageSamplesLength*2):
#				break
				continue
			voltages = Conversion.uint8_array_to_uint16_array(powerSamplesStruct[ind:ind + voltageSamplesLength * 2])
			ind += voltageSamplesLength*2
			# print voltages

			currentTimestampsLength = Conversion.uint8_array_to_uint16(powerSamplesStruct[ind:ind+2])
			ind += 2
			currentTimestampsFirst = Conversion.uint8_array_to_uint32(powerSamplesStruct[ind:ind+4])
			ind += 4
			currentTimestampsLast = Conversion.uint8_array_to_uint32(powerSamplesStruct[ind:ind+4])
			ind += 4
			if (len(powerSamplesStruct[ind:]) < currentTimestampsLength-1):
#				break
				continue
			currentTimestamps = [currentTimestampsFirst]
			for i in range(0, currentTimestampsLength-1):
				currentTimestamps.append(currentTimestamps[i] + powerSamplesStruct[ind])
				ind += 1
			# print currentTimestamps

			voltageTimestampsLength = Conversion.uint8_array_to_uint16(powerSamplesStruct[ind:ind+2])
			ind += 2
			voltageTimestampsFirst = Conversion.uint8_array_to_uint32(powerSamplesStruct[ind:ind+4])
			ind += 4
			voltageTimestampsLast = Conversion.uint8_array_to_uint32(powerSamplesStruct[ind:ind+4])
			ind += 4
			if (len(powerSamplesStruct[ind:]) < voltageTimestampsLength-1):
#				break
				continue
			voltageTimestamps = [voltageTimestampsFirst]
			for i in range(0, voltageTimestampsLength-1):
				voltageTimestamps.append(voltageTimestamps[i] + powerSamplesStruct[ind])
				ind += 1
			# print voltageTimestamps


			if (currentSamplesLength == currentTimestampsLength and voltageSamplesLength == voltageTimestampsLength):


				currentSamplesAll.extend(currents)
				voltageSamplesAll.extend(voltages)
				if (len(currentTimestampsAll)):
					timeshift = - (currentTimestamps[0] - currentTimestampsAll[-1]) + (currentTimestamps[-1] - currentTimestamps[0])
					currentTimestamps = np.array(currentTimestamps) + timeshift
					voltageTimestamps = np.array(voltageTimestamps) + timeshift

				currentTimestampsAll.extend(currentTimestamps)
				voltageTimestampsAll.extend(voltageTimestamps)
				# currentSamplesAll.append(currentSamples)
				# currentTimestampsAll.append(currentTimestamps)
				# voltageSamplesAll.append(voltageSamples)
				# voltageTimestampsAll.append(voltageTimestamps)

				voltageDiff = np.diff(voltages)
				voltageDiffTime = voltageTimestamps[1:]
				voltageDiffAll["val"].extend(voltageDiff)
				voltageDiffAll["time"].extend(voltageDiffTime)

				#################################
				#     Calculate min and max     #
				#################################
				vMin = 1023
				vMinInd = -1
				vMax = 0
				vMaxInd = -1
				for i in range(0, len(voltages)):
					if (voltages[i] > vMax):
						vMax = voltages[i]
						vMaxInd = i
					if (voltages[i] < vMin):
						vMin = voltages[i]
						vMinInd = i
				vMean = (vMax - vMin)/2.0 + vMin

				voltageMinMeanMax["time"].append(voltageTimestamps[0])
				voltageMinMeanMax["min"].append(vMin)
				voltageMinMeanMax["mean"].append(vMean)
				voltageMinMeanMax["max"].append(vMax)



				cMin = 1023
				cMinInd = -1
				cMax = 0
				cMaxInd = -1
				for i in range(0, len(currents)):
					if (currents[i] > cMax):
						cMax = currents[i]
						cMaxInd = i
					if (currents[i] < cMin):
						cMin = currents[i]
						cMinInd = i
				cMean = (cMax - cMin)/2.0 + cMin

				currentMinMeanMax["time"].append(currentTimestamps[0])
				currentMinMeanMax["min"].append(cMin)
				currentMinMeanMax["mean"].append(cMean)
				currentMinMeanMax["max"].append(cMax)



				##################################
				#          Calculate tops        #
				##################################

				############# Config! ############
				threshUp =  vMax - 0.05*(vMax-vMin)
				threshLow = vMin + 0.05*(vMax-vMin)
				##################################

				tops=[]
				topTimes=[]
				overThreshInd = -1
				underThreshInd = -1
				localTop = 0
				localTopInd = -1
				for i in range(1, len(voltages)):
					v = voltages[i]
					# print v, overThreshInd, underThreshInd, localTop, localTopInd
					if (overThreshInd > -1):
						if (v > localTop):
							localTop = v
							localTopInd = i
						if (v < threshUp):
							topTimes.append(voltageTimestamps[localTopInd])
							tops.append(localTop)
							overThreshInd = -1

					elif (underThreshInd > -1):
						if (v < localTop):
							localTop = v
							localTopInd = i
						if (v > threshLow):
							topTimes.append(voltageTimestamps[localTopInd])
							tops.append(localTop)
							underThreshInd = -1

					elif (v > threshUp and voltages[i-1] <= threshUp):
						overThreshInd = i
						localTop = v
						localTopInd = i

					elif (v < threshLow and voltages[i-1] >= threshLow):
						underThreshInd = i
						localTop = v
						localTopInd = i
				voltageTops["time"].extend(topTimes)
				voltageTops["val"].extend(tops)


				############################################
				#          Calculate zero crossings        #
				############################################

				zeros = []
				zeroInds = []
				zeroTimes = []
				belowMean = -1
				aboveMean = -1
				for i in range(1, len(voltages)):
					v = voltages[i]
					vPrev = voltages[i-1]
					if (vPrev < vMean and v >= vMean) or (vPrev > vMean and v <= vMean):
						zeroTime = voltageTimestamps[i]
#						zeroTime = (vMean-vPrev)/(v-vPrev)*(voltageTimestamps[i] - voltageTimestamps[i-1])+voltageTimestamps[i-1]
						zeroTimes.append(zeroTime)
						zeros.append(vMean)
						zeroInds.append(i)
				voltageZeroes["time"].extend(zeroTimes)
				voltageZeroes["val"].extend(zeros)


				voltageTimeBetweenZeroes["val"].extend(np.diff(zeroTimes))
				voltageTimeBetweenZeroes["time"].extend(zeroTimes[1:])

				voltageTimeBetweenTops["val"].extend(np.diff(topTimes))
				voltageTimeBetweenTops["time"].extend(topTimes[1:])


				####################################
				#      Calculate power usage       #
				####################################

#				p=0.0
#				zeroCurrent = 168.5
#				zeroVoltage = 169.0
#				currentMultiplication = 0.044
#
#				voltageMultiplication = 2.357
#
#				tSum = 0
#				for i in range(zeroInds[0], zeroInds[-1]+1):
#					dt = voltageTimestamps[i] - voltageTimestamps[i-1]
#					dt /= 32768.0
#
#					v = (voltages[i] - zeroVoltage)
#					v *= voltageMultiplication
#
#					c = (currents[i] - zeroCurrent)
#					# # multiplication is lower for lower values...
#					# if (abs(c) < 20):
#					# 	currentMultiplication = 15.0 + abs(c)/20.0 * 5.0
#					c *= currentMultiplication
#
#					# print v, c, dt
#
#					p += v * c * dt
#					tSum += dt
#
#				p /= tSum
#				p -= 14
#				power["time"].append(voltageTimestamps[0])
#				power["val"].append(p)

				voltageMultiplication = voltageMultiplications["default"]
				currentMultiplication = currentMultiplications["default"]
				pZero = pZeros["default"]
				if (address in voltageMultiplications):
					voltageMultiplication = voltageMultiplications[address]
				if (address in currentMultiplications):
					currentMultiplication = currentMultiplications[address]
				if (address in pZeros):
					pZero = pZeros[address]

				tSum = 0.0
				pSum = 0.0
				endTime = voltageTimestamps[0] + 20.0*32768/1000
				for i in range(1, len(voltageTimestamps)):
					if (voltageTimestamps[i] <= endTime):
						dt = voltageTimestamps[i] - voltageTimestamps[i-1]
						dt /= 32768.0
						v = (voltages[i] - vMean) * voltageMultiplication
						c = (currents[i] - vMean) * currentMultiplication
						pSum += v * c * dt
						tSum += dt

				pSum /= tSum
				pSum -= pZero
				power["time"].append(voltageTimestamps[0])
				power["val"].append(pSum)

				# break



	fig, axes = plt.subplots(nrows=2, sharex=True)
	# for i in range(0, len(currentSamplesAll)):
	axes[0].plot(currentTimestampsAll, currentSamplesAll, "o", label="current")
	axes[1].plot(voltageTimestampsAll, voltageSamplesAll, "o", label="voltage")
	axes[1].plot(voltageTops["time"], voltageTops["val"], "rv", label="tops")
	axes[1].plot(voltageZeroes["time"], voltageZeroes["val"], "gv", label="zero crossings")
	# axes[1].plot(voltageMinMeanMax["time"], voltageMinMeanMax["min"], "o", label="min")
	# axes[1].plot(voltageMinMeanMax["time"], voltageMinMeanMax["mean"], "o", label="mean")
	# axes[1].plot(voltageMinMeanMax["time"], voltageMinMeanMax["max"], "o", label="max")
#	axes[2].plot(voltageTimeBetweenZeroes["time"], np.array(voltageTimeBetweenZeroes["val"]) / 32.7680, "o", label="time between zero crossings")
	axes[0].set_title(options.data_file)

#	axes[3].plot(voltageTimeBetweenTops["time"], np.array(voltageTimeBetweenTops["val"]) / 32.7680, "o", label="time between tops")
#	axes[2].plot(voltageDiffAll["time"], voltageDiffAll["val"], "o", label="voltage diff")

	plt.show()
	exit(0)

	plt.figure()
	plt.plot(range(0, len(voltageMinMeanMax["min"])), voltageMinMeanMax["min"], label="Vmin")
	plt.plot(range(0, len(voltageMinMeanMax["mean"])), voltageMinMeanMax["mean"], label="Vmean")
	plt.plot(range(0, len(voltageMinMeanMax["max"])), voltageMinMeanMax["max"], label="Vmax")
	plt.legend()
	plt.title(options.data_file)

	plt.figure()
	plt.plot(range(0, len(currentMinMeanMax["min"])), currentMinMeanMax["min"], label="Imin")
	plt.plot(range(0, len(currentMinMeanMax["mean"])), currentMinMeanMax["mean"], label="Imean")
	plt.plot(range(0, len(currentMinMeanMax["max"])), currentMinMeanMax["max"], label="Imax")
	plt.legend()
	plt.title(options.data_file)

	plt.figure()
	plt.plot(power["time"], np.array(power["val"]), "ro", label="power (W)")
	plt.legend()
	plt.title(options.data_file)

	plt.figure()
	dts = np.diff(np.array(voltageTimestampsAll))
	dtMean = 0.0
	dtMeanNum = 0
	for dt in dts:
		if (dt < 100):
			dtMean += dt
			dtMeanNum += 1
	dtMean /= dtMeanNum
	plt.plot(dts, "o", alpha=0.1, label="dt")
	plt.plot([0, len(dts)], [dtMean, dtMean], label="mean")
	plt.legend()
	plt.title(options.data_file)

	# for addr in powerSamples:
	# 	# # Plot missing notifications
	# 	# x = np.array(range(0, len(powerSamples[addr])))
	# 	# y = np.array(powerSamples[addr]) - powerSamples[addr][0] - x
	# 	# plt.plot(x, y, label=addr)
	# 	# plt.legend()
	# 	# plt.xlabel("received notification")
	# 	# plt.ylabel("missed notifications")
	#
	# 	# Plot received power samples
	# 	plt.plot(range(0,len(powerSamples[addr])), powerSamples[addr], "o")

	plt.show()