#!/usr/bin/env python

__author__ = 'Bart van Vliet'


from bleAutomator2 import *
from Bluenet import *
from ConversionUtils import *
from Crypto.Cipher import AES
from Crypto.Util import Counter
import Crypto.Random

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] -a <ble address>\n\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4',
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

		options, args = parser.parse_args()

	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)

	if (not options.address):
		parser.print_help()
		exit(2)

	ble = BleAutomator(options.interface, options.verbose)

	# Connect to peer device.
	if (not ble.connect(options.address)):
		exit(1)

	########################################
	# Get session nonce and validation key #
	########################################
	arr8 = ble.readCharacteristic(CHAR_SETUP_SESSION_NONCE)
	if (not arr8):
		print "Couldn't read session nonce"
		exit(1)

	sessionNonce = arr8
	validationKey = arr8[0:4]
	print "Session nonce:", list(sessionNonce)
	print "Validation key:", list(validationKey)


	################################
	# Get encryption key for setup #
	################################
	arr8 = ble.readCharacteristic(CHAR_SETUP_KEY)
	if (not arr8):
		print "Couldn't read session key"
		exit(1)
	sessionKey = arr8
	print "Session key:", list(sessionKey)


	#######################
	# Write Crownstone ID #
	#######################
	# crownstoneID = 7357
	# data = Conversion.uint16_to_uint8_array(crownstoneID)
	# dataSize = len(data)
	# payloadData = [ConfigTypes.CONFIG_CROWNSTONE_ID, ValueOpCode.WRITE_VALUE]
	# payloadData.extend(Conversion.uint16_to_uint8_array(dataSize))
	# payloadData.extend(data)
	# print "Payload data:", payloadData
	#
	# arr8 = Bluenet.encryptCtr(payloadData, sessionNonce, validationKey, sessionKey, EncryptionAccessLevel.SETUP)
	# print "Write:", list(arr8)
	# if (not ble.writeCharacteristic(CHAR_SETUP_CONFIG_CONTROL, arr8)):
	# 	print "failed to write to CHAR_SETUP_CONFIG_CONTROL"
	# 	exit(1)

	#########################
	# Write Crownstone name #
	#########################
	# crownstoneName = "test"
	# data = Conversion.string_to_uint8_array(crownstoneName)
	# dataSize = len(data)
	# payloadData = [ConfigTypes.CONFIG_NAME, ValueOpCode.WRITE_VALUE]
	# payloadData.extend(Conversion.uint16_to_uint8_array(dataSize))
	# payloadData.extend(data)
	# print "Payload data:", payloadData
	#
	# arr8 = Bluenet.encryptCtr(payloadData, sessionNonce, validationKey, sessionKey, EncryptionAccessLevel.SETUP)
	# print "Write:", list(arr8)
	# if (not ble.writeCharacteristic(CHAR_SETUP_CONFIG_CONTROL, arr8)):
	# 	print "failed to write to CHAR_SETUP_CONFIG_CONTROL"
	# 	exit(1)


	##############################
	# Put Crownstone in DFU mode #
	##############################
	# data = []
	# dataSize = len(data)
	# payloadData = [CommandTypes.CMD_GOTO_DFU, 0]
	# payloadData.extend(Conversion.uint16_to_uint8_array(dataSize))
	# payloadData.extend(data)
	# print "Payload data:", payloadData
	#
	# arr8 = Bluenet.encryptCtr(payloadData, sessionNonce, validationKey, sessionKey, EncryptionAccessLevel.SETUP)
	# print "Write:", list(arr8)
	# if (not ble.writeCharacteristic(CHAR_SETUP_CONTROL, arr8)):
	# 	print "failed to write to CHAR_SETUP_CONTROL"
	# 	exit(1)

	############################
	# Factory reset Crownstone #
	############################
	# data = Conversion.hex_string_to_uint8_array(FACTORY_RESET_CODE)
	# dataSize = len(data)
	# payloadData = [CommandTypes.CMD_FACTORY_RESET, 0]
	# payloadData.extend(Conversion.uint16_to_uint8_array(dataSize))
	# payloadData.extend(data)
	# print "Payload data:", payloadData
	#
	# arr8 = Bluenet.encryptCtr(payloadData, sessionNonce, validationKey, sessionKey, EncryptionAccessLevel.SETUP)
	# print "Write:", list(arr8)
	# if (not ble.writeCharacteristic(CHAR_SETUP_CONTROL, arr8)):
	# 	print "failed to write to CHAR_SETUP_CONTROL"
	# 	exit(1)

	##################
	# Switch off pwm #
	##################
	# data = [0]
	# dataSize = len(data)
	# payloadData = [CommandTypes.CMD_PWM, 0]
	# payloadData.extend(Conversion.uint16_to_uint8_array(dataSize))
	# payloadData.extend(data)
	# print "Payload data:", payloadData
	#
	# arr8 = Bluenet.encryptCtr(payloadData, sessionNonce, validationKey, sessionKey, EncryptionAccessLevel.SETUP)
	# print "Write:", list(arr8)
	# if (not ble.writeCharacteristic(CHAR_SETUP_CONTROL, arr8)):
	# 	print "failed to write to CHAR_SETUP_CONTROL"
	# 	exit(1)


	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()

	exit(0)
