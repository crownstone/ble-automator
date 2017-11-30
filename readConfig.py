#!/usr/bin/env python

__author__ = 'Bart van Vliet'


from bleAutomator2 import *
import ConfigUtils
from ConversionUtils import *
from Bluenet import *
import struct


if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='''%prog [-v] [-i <interface>] -a <ble address> -t <type> [-n]
											\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4 -t 0 -s''',
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
				dest="configType",
				type="int",
				default=None,
				help='What configuration to read (integer)'
				)
		parser.add_option('-n', '--number',
				action='store_true',
				dest="as_number",
				help='Read value as number, not as string'
				)
		parser.add_option('-f', '--float',
				action='store_true',
				dest="as_float",
				help='Read value as float, not as string'
				)
		parser.add_option('-r', '--array',
				action='store_true',
				dest="as_array",
				help='Read value as array (hex), not as string'
				)
		parser.add_option('-c', '--configuration-file',
				action='store',
				dest="configFile",
				default="config.json",
				help='Config file (json).'
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

	if (not options.address or options.configType == None):
		parser.print_help()
		exit(2)

	ble = BleAutomator(options.interface, options.verbose)
	
	keys = ConfigUtils.readKeys(options.configFile)
	if (not keys):
		print "Could not find keys in the config file: " + options.configFile
		sys.exit(1)

	print "Gotten keys from the config file"
	adminKey = keys["admin"].decode("hex")	
	memberKey = keys["member"].decode("hex")	
	guestKey = keys["guest"].decode("hex")	

	# Connect to peer device.
	print "Connect to Bluetooth Low Energy device at address " + options.address
	if (not ble.connect(options.address)):
		print "Do not connect too often! Connections needs to be correctly broken off at the OS level."
		exit(1)

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


	# Write type to select, first byte is the type, second byte is the
	# opCode
	arr8 = [options.configType, ValueOpCode.READ_VALUE]
	
	if (options.viaSetup):
		if (not ble.writeCharacteristic(CHAR_SETUP_CONFIG_CONTROL, arr8)):
			exit(1)
	else:
		if (options.encryption):
			encryptedArr8 = Bluenet.encryptCtr(arr8, sessionNonce, validationKey, adminKey, EncryptionAccessLevel.ADMIN, options.verbose)
		else:
			encryptedArr8 = arr8

		if (not ble.writeCharacteristic(CHAR_CONFIG_CONTROL, encryptedArr8)):
			print "Characteristic not found"
			exit(1)

	time.sleep(1)

	# Read the value of selected type

	if (options.viaSetup):
		arr8 = ble.readCharacteristic(CHAR_SETUP_CONFIG_READ)
	else:
		arr8 = ble.readCharacteristic(CHAR_CONFIG_READ)
	if (not arr8):
		print "Couldn't read value"
		exit(1)

	if (options.encryption):
		decryptedArr8 = Bluenet.decryptCtr(arr8, sessionNonce, validationKey, adminKey, memberKey, guestKey, options.verbose)
	else:
		decryptedArr8 = arr8

	# First byte is the type
	print "Type: %i" % (decryptedArr8[0])
	if (options.configType != decryptedArr8[0]):
		print "Type mismatch"
		exit(1)

	# Second byte is the op code, not really necessary to check that, would be READ_VALUE (0x0) in this case

	# Third and fourth bytes is the length of the data, as uint16_t
	length = Conversion.uint8_array_to_uint16(decryptedArr8[2:4])

	# Fifth and on bytes is the data
	data = decryptedArr8[4:]
	if (len(data) < length):
		print "Size mismatch"
		print "data:", list(decryptedArr8)
		exit(1)
	data = data[0:length]

	if (options.verbose):
		print "data:", list(decryptedArr8)

	# Output as string or as single uint8
	if (options.as_number):
		if (length == 1):
			print "Value: %i" % (data[0])
		elif (length == 2):
			print "Value: %i" % (Conversion.uint8_array_to_uint16(data))
		elif (length == 4):
			print "Value: %i" % (Conversion.uint8_array_to_uint32(data))
		else:
			print "Value:", list(data)
	elif (options.as_array):
		valStr = Conversion.uint8_array_to_hex_string(data)
		print "Value: %s" %valStr
	elif (options.as_float):
		# valStr = '{0:032b}'.format(Conversion.uint8_array_to_uint32(data))
		# val = (data[0] << 24) + (data[1] << 16) + (data[2] << 8) + data[3]
		# valStr = '{0:032b}'.format(val)
		# print "Value: %s" %valStr
		print "Float:", Conversion.uint8_array_to_float(data)
	else:
		valStr = Conversion.uint8_array_to_string(data)
		print "Value: %s" % (valStr)

	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()

	exit(0)
