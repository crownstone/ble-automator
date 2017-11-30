#!/usr/bin/env python
__author__ = 'Bart van Vliet'

from bleAutomator2 import *
from Bluenet import *
import ConfigUtils

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
		parser.add_option('-e', '--encryption',
				action='store_true',
				dest="encryption",
				help='Use encryption.'
				)
		parser.add_option('-d', '--dfu-mode',
				action='store_true',
				dest="dfu",
				help="Reset and enter dfu mode."
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
	
	# Get keys
	keys = ConfigUtils.readKeys(options.configFile)
	if (not keys):
		print "Could not find keys in the config file: " + options.configFile
		sys.exit(1)

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


	resetCode = RESET_CODE_RESET
	if (options.dfu):
		resetCode = RESET_CODE_DFU

	if (options.encryption):
		encryptedArr8 = Bluenet.encryptCtr([resetCode], sessionNonce, validationKey, adminKey, EncryptionAccessLevel.ADMIN, options.verbose)
	else:
		encryptedArr8 = [resetCode]

	# Write 1 to reset
	# Write should fail, since we won't get a response
	if (ble.writeCharacteristic(CHAR_RESET, encryptedArr8)):
		print "Failed to reset"
		exit(1)

	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()

	print "Reset successful"
	exit(0)
