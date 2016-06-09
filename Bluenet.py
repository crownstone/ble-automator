__author__ = 'Bart van Vliet'

import math
from ConversionUtils import *

CHAR_CONTROL                       = "24f00001-7d10-4805-bfc1-7663a01c3bff"
CHAR_MESH_CONTROL                  = "24f00002-7d10-4805-bfc1-7663a01c3bff"
CHAR_CONFIG_CONTROL                = "24f00004-7d10-4805-bfc1-7663a01c3bff"
CHAR_CONFIG_READ                   = "24f00005-7d10-4805-bfc1-7663a01c3bff"
CHAR_STATE_CONTROL                 = "24f00006-7d10-4805-bfc1-7663a01c3bff"
CHAR_STATE_READ                    = "24f00007-7d10-4805-bfc1-7663a01c3bff"

CHAR_MAC_ADDRESS                   = "24f10002-7d10-4805-bfc1-7663a01c3bff"

CHAR_TEMPERATURE                   = "24f20001-7d10-4805-bfc1-7663a01c3bff"
CHAR_RESET                         = "24f20002-7d10-4805-bfc1-7663a01c3bff"

CHAR_PWM                           = "24f30001-7d10-4805-bfc1-7663a01c3bff"
CHAR_RELAY                         = "24f30002-7d10-4805-bfc1-7663a01c3bff"
CHAR_POWER_SAMPLES                 = "24f30003-7d10-4805-bfc1-7663a01c3bff"
CHAR_CURRENT_CONSUMPTION           = "24f30004-7d10-4805-bfc1-7663a01c3bff"

CHAR_TRACKED_DEVICE                = "24f40001-7d10-4805-bfc1-7663a01c3bff"
CHAR_TRACKED_DEVICE_LIST           = "24f40002-7d10-4805-bfc1-7663a01c3bff"
CHAR_SCAN_DEVICE                   = "24f40003-7d10-4805-bfc1-7663a01c3bff"
CHAR_LIST_DEVICE                   = "24f40004-7d10-4805-bfc1-7663a01c3bff"
CHAR_RSSI                          = "24f40005-7d10-4805-bfc1-7663a01c3bff"

CHAR_CURRENT_TIME                  = "24f50001-7d10-4805-bfc1-7663a01c3bff"
CHAR_WRITE_SCHEDULE_ENTRY          = "24f50002-7d10-4805-bfc1-7663a01c3bff"
CHAR_LIST_SCHEDULE_ENTRIES         = "24f50003-7d10-4805-bfc1-7663a01c3bff"

CHAR_SUPPORTED_NEW_ALERT           = "24f60001-7d10-4805-bfc1-7663a01c3bff"
CHAR_NEW_ALERT                     = "24f60002-7d10-4805-bfc1-7663a01c3bff"
CHAR_SUPPORTED_UNREAD_ALERT        = "24f60003-7d10-4805-bfc1-7663a01c3bff"
CHAR_UNREAD_ALERT                  = "24f60004-7d10-4805-bfc1-7663a01c3bff"
CHAR_ALERT_CONTROL_POINT           = "24f60005-7d10-4805-bfc1-7663a01c3bff"

CHAR_MESH_METADATA                 = "2a1e0004-fd51-d882-8ba8-b98c0000cd1e"
CHAR_MESH_VALUE                    = "2a1e0005-fd51-d882-8ba8-b98c0000cd1e"

RESET_CODE_RESET = 1
RESET_CODE_DFU = 66

class MeshHandleType:
	HUB   = 1
	DATA  = 2

class MeshDataMessageType:
	CONTROL_MESSAGE       = 0
	BEACON_MESSAGE        = 1
	CONFIG_MESSAGE        = 2
	STATE_MESSAGE         = 3
	SCAN_MESSAGE          = 101
	POWER_SAMPLES_MESSAGE = 102
	EVENT_MESSAGE         = 103

class CommandTypes:
	CMD_SWITCH                      = 0  # 0x00
	CMD_PWM                         = 1  # 0x01
	CMD_SET_TIME                    = 2  # 0x02
	CMD_GOTO_DFU                    = 3  # 0x03
	CMD_RESET                       = 4  # 0x04
	CMD_FACTORY_RESET               = 5  # 0x05
	CMD_KEEP_ALIVE_STATE            = 6  # 0x06
	CMD_KEEP_ALIVE                  = 7  # 0x07
	CMD_ENABLE_MESH                 = 8  # 0x08
	CMD_ENABLE_ENCRYPTION           = 9  # 0x09
	CMD_ENABLE_IBEACON              = 10 # 0x0A
	CMD_ENABLE_CONT_POWER_MEASURE   = 11 # 0x0B
	CMD_ENABLE_SCANNER              = 12 # 0x0C
	CMD_SCAN_DEVICES                = 13 # 0x0D
	CMD_SAMPLE_POWER                = 14 # 0x0E
	CMD_USER_FEEDBACK               = 15 # 0x0F
	CMD_SCHEDULE_ENTRY              = 16 # 0x10

class ConfigTypes:
	CONFIG_NAME                             = 0  # 0x00
	CONFIG_DEVICE_TYPE                      = 1  # 0x01
	CONFIG_ROOM                             = 2  # 0x02
	CONFIG_FLOOR                            = 3  # 0x03
	CONFIG_NEARBY_TIMEOUT                   = 4  # 0x04
	CONFIG_PWM_FREQ                         = 5  # 0x05
	CONFIG_IBEACON_MAJOR                    = 6  # 0x06
	CONFIG_IBEACON_MINOR                    = 7  # 0x07
	CONFIG_IBEACON_UUID                     = 8  # 0x08
	CONFIG_IBEACON_TXPOWER                  = 9  # 0x09
	CONFIG_WIFI_SETTINGS                    = 10 # 0x0A
	CONFIG_TX_POWER                         = 11 # 0x0B
	CONFIG_ADV_INTERVAL                     = 12 # 0x0C
	CONFIG_PASSKEY							= 13 # 0x0D
	CONFIG_MIN_ENV_TEMP                     = 14 # 0x0E
	CONFIG_MAX_ENV_TEMP                     = 15 # 0x0F
	CONFIG_SCAN_DURATION                    = 16 # 0x10
	CONFIG_SCAN_SEND_DELAY                  = 17 # 0x11
	CONFIG_SCAN_BREAK_DURATION              = 18 # 0x12
	CONFIG_BOOT_DELAY                       = 19 # 0x13
	CONFIG_MAX_CHIP_TEMP                    = 20 # 0x14
	CONFIG_SCAN_FILTER                      = 21 # 0x15
	CONFIG_SCAN_FILTER_SEND_FRACTION        = 22 # 0x16
	CONFIG_CURRENT_LIMIT                    = 23 # 0x17
	CONFIG_MESH_ENABLED                     = 24 # 0x18
	CONFIG_ENCRYPTION_ENABLED               = 25 # 0x19
	CONFIG_IBEACON_ENABLED                  = 26 # 0x1A
	CONFIG_SCANNER_ENABLED                  = 27 # 0x1B
	CONFIG_CONT_POWER_SAMPLER_ENABLED       = 28 # 0x1C
	CONFIG_TRACKER_ENABLED                  = 29 # 0x1D
	CONFIG_ADC_SAMPLE_RATE                  = 30 # 0x1E
	CONFIG_POWER_SAMPLE_BURST_INTERVAL      = 31 # 0x1F
	CONFIG_POWER_SAMPLE_CONT_INTERVAL       = 32 # 0x20
	CONFIG_POWER_SAMPLE_CONT_NUM_SAMPLES    = 33 # 0x21
	CONFIG_CROWNSTONE_ID                    = 34 # 0x22

class ValueOpCode:
	READ_VALUE   = 0
	WRITE_VALUE  = 1
	NOTIFY_VALUE = 2

class ScheduleTimeType:
	TIME_REPEAT = 0
	DAILY       = 1

class ScheduleActionType:
	PWM         = 0
	FADE        = 1

class ScheduleOverride:
	PRESENCE    = 1

class ScheduleDaily:
	ALL_DAYS    = 0
	SUNDAYS     = 1
	MONDAYS     = 2
	TUESDAYS    = 3
	WEDNESDAYS  = 4
	THURSDAYS   = 5
	FRIDAYS     = 6
	SATURDAYS   = 7

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

	# Copied implementation of nordic
	@staticmethod
	def crc16_ccitt(arr8, length):
		"""
		:param arr8:
		:param length:
		:return:
		"""
		crc = 0xFFFF
		for i in range(0, length):
			crc = (crc >> 8 & 0xFF) | (crc << 8 & 0xFFFF)
			crc ^= arr8[i]
			crc ^= (crc & 0xFF) >> 4
			crc ^= (crc << 8 & 0xFFFF) << 4 & 0xFFFF
			crc ^= ((crc & 0xFF) << 4 & 0xFFFF) << 1 & 0xFFFF
		return crc

