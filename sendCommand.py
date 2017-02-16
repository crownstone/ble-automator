#!/usr/bin/env python
__author__ = 'Bart van Vliet'


from bleAutomator2 import *
from ConversionUtils import *
from Bluenet import *

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='''%prog [-v] [-i <interface>] -a <ble address> -t <type> -d <value> [-n]
											\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4 -t 1 -n -d 100
											Example:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4 -t 13 -r -d "1 5000" -l "1 2"''',
									version='0.1')

		parser.add_option('-a', '--address',
				action='store',
				dest="address",
				type="string",
				default=None,
				help='DFU target address. (Can be found by running "hcitool lescan")'
				)
		parser.add_option('-i', '--interface',
				action='store',
				dest="interface",
				type="string",
				default="hci0",
				help='HCI interface to be used.'
				)
		parser.add_option('-v', '--verbose',
				action='store_true',
				dest="verbose",
				help='Be verbose.'
				)
		parser.add_option('-e', '--encryption',
				action='store_true',
				dest="encryption",
				help='Use encryption.'
				)
		parser.add_option('-t', '--type',
				action='store',
				dest="commandType",
				type="int",
				default=0,
				help='What command to send (integer)'
				)
		parser.add_option('-n', '--number',
				action='store_true',
				dest="as_number",
				help='parameter value as number'
				)
		parser.add_option('-r', '--array',
				action='store_true',
				dest="as_array",
				help='parameter value provided as array like "0 1 2"'
				)
		parser.add_option('-d', '--data',
				action='store',
				dest="paramValue",
				type="string",
				default=None,
				help='Value to set'
				)
		parser.add_option('-s', '--size',
				action='store',
				dest="paramSize",
				type="int",
				default=0,
				help='Size of the parameter data (amount of bytes) (integer)'
				)
		parser.add_option('-l', '--size_list',
				action='store',
				dest="paramSizeList",
				type="string",
				default=None,
				help='array of size of the parameter data (amount of bytes) when used with -r'
				)
		parser.add_option('-m', '--mesh',
				action='store_true',
				dest="viaMesh",
				help='Send command over the mesh'
				)
		parser.add_option('-b', '--broadcast',
				action='store_true',
				dest="broadcast"
				)
		parser.add_option('-g', '--target',
				action='store',
				dest="target",
				type="string",
				default=None,
				help='target crownstone id'
				)

		parser.add_option('-p', '--setup',
				action='store_true',
				dest="viaSetup",
				help='Write value setup'
				)

		options, args = parser.parse_args()

	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)

	if (not options.address or options.commandType == None or (options.paramValue == None and options.paramSize != 0)):
		parser.print_help()
		exit(2)

	if (options.as_array and not options.paramSizeList):
		print "Need to provide number of array elements as list of sizes (-l) if -r is used"
		exit(2)

	ble = BleAutomator(options.interface, options.verbose)

	# Connect to peer device.
	if (not ble.connect(options.address)):
		exit(1)

	adminKey = "adminKeyForCrown"
	memberKey = "memberKeyForHome"
	guestKey = "guestKeyForGirls"

	sessionNonce = None
	validationKey = None
	if (options.encryption):
		sessionPacket = ble.readCharacteristic(CHAR_SESSION_NONCE)
		sessionPacket = Bluenet.decryptEcb(sessionPacket, guestKey)
		sessionNonce = sessionPacket[ENCRYPTION_VALIDATION_KEY_LENGTH : ENCRYPTION_VALIDATION_KEY_LENGTH+ENCRYPTION_SESSION_NONCE_LENGTH]
		validationKey = sessionPacket[ENCRYPTION_VALIDATION_KEY_LENGTH : ENCRYPTION_VALIDATION_KEY_LENGTH+ENCRYPTION_VALIDATION_KEY_LENGTH]

		if (options.verbose):
			print "CAFEBABE:", list(sessionPacket[0:ENCRYPTION_VALIDATION_KEY_LENGTH])
			print CAFEBABE, " = ", Conversion.uint8_array_to_uint32(sessionPacket[0:ENCRYPTION_VALIDATION_KEY_LENGTH])
			print "sessionNonce:", list(sessionNonce)
			print "validationKey:", list(validationKey)

	# First byte is the type
	# Second byte is reserved for byte alignment
	arr8 = [options.commandType, 0]

	if (options.paramValue):
		data = []
		if (options.as_number):
			# Write value as number
			valInt = int(options.paramValue)
			if (valInt < 0):
				print "Cannot write values lower than 0!"
				exit(1)

			if (valInt > 65535 or options.paramSize == 4):
				data = Conversion.uint32_to_uint8_array(valInt)
			elif (valInt > 255 or options.paramSize == 2):
				data = Conversion.uint16_to_uint8_array(valInt)
			else:
				data = [valInt]
		elif (options.as_array):
			# split the param string and convert into integer values
			dataList = map(int, options.paramValue.split())
			# split the size string and convert into integer values
			sizeList = map(int, options.paramSizeList.split())
			# check if split was successful by comparing the number
			# of provided parameters
			if (len(dataList) == 0 or len(dataList) != len(sizeList)):
				print "Wrong number of parameters provided"
				exit(1)

			# loop through parameters and convert them into little endian byte arrays
			# depending on size
			for i in xrange(0, len(dataList)):
				valInt = dataList[i]
				if (valInt > 65535 or sizeList[i] == 4):
					data.extend(Conversion.uint32_to_uint8_array(valInt))
				elif (valInt > 255 or sizeList[i] == 2):
					data.extend(Conversion.uint16_to_uint8_array(valInt))
				else:
					data.extend([valInt])

			# need to overwrite the paramSize otherwise the check will further
			# down will fail
			# options.paramSize = len(data)
		else:
			# Write value as string
			data = Conversion.string_to_uint8_array(options.paramValue)

		# Third and fourth bytes is the length of the data, as uint16_t
		dataSize = len(data)
		if (options.paramSize):
			dataSize = options.paramSize
			if (len(data) < dataSize):
				# append zeroes
				data.extend([0]*(dataSize - len(data)))
			elif (len(data) > dataSize):
				print "Invalid data size"
				print "Expected %i, got %i" % (dataSize, len(data))
				exit(1)

		arr8.extend(Conversion.uint16_to_uint8_array(dataSize))

		# Add the data
		arr8.extend(data)

		print "command", list(arr8)
	else:
		arr8.extend([0, 0])

	if (options.viaMesh):

		if (options.target):
			# split the param string and convert into integer values
			targetList = map(int, options.target.split())
			targetListLen = len(targetList)

			if (targetListLen == 0):
				print "invalid target list"
				exit(1)
		elif (options.broadcast):
			targetListLen = 0
		else:
			print "need to provide target crownstone id. use -b for broadcast instead"
			exit(1)

		meshArr8 = [4, 0] # Handle
		# meshArr8.extend(Conversion.uint16_to_uint8_array(6+2+len(arr8))) # Length of target address + mesh message type + data
		meshArr8.extend(Conversion.uint16_to_uint8_array(3+ targetListLen*2 + len(arr8))) # Length of target address + mesh message type + data

		meshArr8.extend(Conversion.uint16_to_uint8_array(MeshDataMessageType.CONTROL_MESSAGE))
		# meshArr8.extend(Conversion.uint16_to_uint8_array(MeshDataMessageType.CONFIG_MESSAGE))
		# meshArr8.extend(Conversion.uint16_to_uint8_array(MeshDataMessageType.STATE_MESSAGE))

		meshArr8.extend([targetListLen])

		if (targetListLen > 0):
			for i in xrange(0, targetListLen):
				meshArr8.extend(Conversion.uint16_to_uint8_array(targetList[i]))

		meshArr8.extend(arr8)
		print meshArr8
		if (options.encryption):
			encryptedArr8 = Bluenet.encryptCtr(arr8, sessionNonce, validationKey, adminKey, EncryptionAccessLevel.ADMIN, options.verbose)
		else:
			encryptedArr8 = arr8
		if (not ble.writeCharacteristic(CHAR_MESH_CONTROL, encryptedArr8)):
			print "failed to write to CHAR_MESH_CONTROL"
			exit(1)

		print "mesh", list(meshArr8)
	elif (options.viaSetup):
		if (not ble.writeCharacteristic(CHAR_SETUP_CONTROL, arr8)):
			print "failed to write to CHAR_SETUP_CONTROL"
			exit(1)
	else:
		if (options.verbose):
			print "Write", arr8

		if (options.encryption):
			encryptedArr8 = Bluenet.encryptCtr(arr8, sessionNonce, validationKey, adminKey, EncryptionAccessLevel.ADMIN, options.verbose)
		else:
			encryptedArr8 = arr8
		if (not ble.writeCharacteristic(CHAR_CONTROL, encryptedArr8)):
			print "Characteristic not found"
			exit(1)

	time.sleep(0.5)

	if (options.viaSetup):
		arr8 = ble.readCharacteristic(CHAR_SETUP_CONTROL)
	elif (options.viaMesh):
		arr8 = ble.readCharacteristic(CHAR_MESH_CONTROL)
	else:
		arr8 = ble.readCharacteristic(CHAR_CONTROL)

	if (len(arr8) != 2):
		print "wrong response length", arr8
	else:
		err = Conversion.uint8_array_to_uint16(arr8);
		if (err == 0):
			print "success", err
		else:
			print "failed with error:", err

	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()

	exit(0)
