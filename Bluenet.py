__author__ = 'Bart van Vliet'

import math
from ConversionUtils import *

CHAR_TEMPERATURE =      "f5f90001-59f9-11e4-aa15-123b93f75cba"
CHAR_RESET =            "f5f90005-59f9-11e4-aa15-123b93f75cba"
CHAR_CONFIG_WRITE =     "f5f90007-59f9-11e4-aa15-123b93f75cba"
CHAR_CONFIG_SELECT =    "f5f90008-59f9-11e4-aa15-123b93f75cba"
CHAR_CONFIG_READ =      "f5f90009-59f9-11e4-aa15-123b93f75cba"

CHAR_PWM =              "5b8d0001-6f20-11e4-b116-123b93f75cba"
CHAR_SAMPLE_POWER =     "5b8d0002-6f20-11e4-b116-123b93f75cba"
CHAR_READ_POWER_CURVE = "5b8d0003-6f20-11e4-b116-123b93f75cba"

CHAR_SET_TIME =         "96d20001-4bcf-11e5-885d-feff819cdc9f"

class Bluenet:
	@staticmethod
	def getPowerCurve(arr8):
		"""
		Reads a bytearray and returns dict with current and voltage measurements, with timestamp
		:param arr8:
		:type arr8: bytearray
		:return: dict with "currentSamples", "currentTimestamps", "voltageSamples", "voltageTimestamps"
		"""

		# Layout of the data:
		# type                            description
		#-------------------------------------------
		# uint16_t numSamples             number of current + voltage samples, including first samples
		# uint16_t firstCurrentSample
		# uint16_t lastCurrentSample
		# uint16_t firstVoltageSample
		# uint16_t lastVoltageSample
		# uint32_t timeStart              timestamp of first sample
		# uint32_t timeEnd                timestamp of last sample
		# int8_t   currentIncrements[]    difference with previous current sample, array is of length floor(numSamples/2)-1
		# int8_t   voltageIncrements[]    difference with previous voltage sample, array is of length floor(numSamples/2)-1
		# int8_t   timeIncrements[]       difference with previous timestamp, array is of length numSamples-1
		res = {}

		index=0
		if (len(arr8) < 2):
			return res

		# Read num samples
		numSamples = Conversion.uint8_array_to_uint16(arr8[index:index+2])
		index+=2

		if (numSamples < 1):
			print "No power samples"
			return res

		reqLen = 5*2 + 2*4 + 2*(int(math.floor(numSamples/2))-1) + numSamples-1
		if (len(arr8) < reqLen):
			print "Invalid length for power curve: %i should be: %i" % (len(arr8), reqLen)
			return res

		# Read first current sample
		current = Conversion.uint8_array_to_uint16(arr8[index:index+2])
		index+=2

		# Read the last current sample
		currentLast = Conversion.uint8_array_to_uint16(arr8[index:index+2])
		index+=2

		# Read first voltage sample
		voltage = Conversion.uint8_array_to_uint16(arr8[index:index+2])
		index+=2

		# Read the last voltage sample
		voltageLast = Conversion.uint8_array_to_uint16(arr8[index:index+2])
		index+=2

		# Read first and last time stamp
		tStart = Conversion.uint8_array_to_uint32(arr8[index:index+4])
		index+=4
		tEnd = Conversion.uint8_array_to_uint32(arr8[index:index+4])
		index+=4
		t=tStart

		numCurrentSamples = int(math.floor(numSamples/2))
		numVoltageSamples = int(math.floor(numSamples/2))

		currentIncrements = arr8[index : index+numCurrentSamples-1]
		index += numCurrentSamples-1

		voltageIncrements = arr8[index : index+numVoltageSamples-1]
		index += numVoltageSamples-1

		dts = arr8[index : index+numSamples-1]
		index += numSamples-1


		res["currentSamples"] = [current]
		for inc in currentIncrements:
			diff = Conversion.uint8_to_int8(inc)
			current += diff
			res["currentSamples"].append(current)
		if (currentLast != current):
			print "Warning: inconsistent data in power curve:"
			print "Last current: %i should be: %i" % (current, currentLast)

		res["voltageSamples"] = [voltage]
		for inc in voltageIncrements:
			diff = Conversion.uint8_to_int8(inc)
			voltage += diff
			res["voltageSamples"].append(voltage)
		if (voltageLast != voltage):
			print "Warning: inconsistent data in power curve:"
			print "Last voltage: %i should be: %i" % (voltage, voltageLast)

		res["currentTimestamps"] = [t]
		res["voltageTimestamps"] = []
		currentTimestamp = False
		for dt in dts:
			diff = Conversion.uint8_to_int8(dt)
			t += diff
			if (currentTimestamp):
				res["currentTimestamps"].append(t)
			else:
				res["voltageTimestamps"].append(t)
			currentTimestamp = not currentTimestamp
		if (tEnd != t):
			print "Warning: inconsistent data in power curve:"
			print "Last timestamp: %i should be: %i" % (t, tEnd)

		return res