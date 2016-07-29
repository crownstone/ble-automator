#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import math
from bleAutomator2 import *
import ConfigUtils
from ConversionUtils import *
from Bluenet import *
import time
import datetime

def getConsumption(address):
	while True:
		notification = ble.waitForNotification(10000.0)
		if (notification):
			powerConsumption = Conversion.uint32_to_int32(Conversion.uint8_array_to_uint32(notification["data"]))
			print time.time(), address, datetime.datetime.now(), powerConsumption
			break

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] [-f <output file>] [-c <config file>] \n\nExample:\n\t%prog -i hci0 -f data.txt -c config.json',
									version='0.1')
		
		parser.add_option('-i', '--interface',
				action='store',
				dest="interface",
				type="string",
				default="hci0",
				help='HCI interface to be used.'
				)
		parser.add_option('-f', '--file',
				action='store',
				dest="data_file",
				type="string",
				default="data.txt",
				help='File to store the data'
				)
		parser.add_option('-v', '--verbose',
				action='store_true',
				dest="verbose",
				help='Be verbose.'
				)
		parser.add_option('-c', '--config',
				action='store',
				dest="configFile",
				default="config.json",
				help='Config file (json)'
				)
		
		options, args = parser.parse_args()
	
	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)
	
	ble = BleAutomator(options.interface, options.verbose)
	
	addresses = ConfigUtils.readAddresses(options.configFile)
	if (not addresses):
		sys.exit(1)
	address_ind = 0

	if (len(addresses) == 1):
		if not ble.connect(addresses[0]):
			exit(1)
		# Subscribe for notifications
		handle = ble.getHandle(CHAR_POWER_CONSUMPTION) + 2
		if (not ble.writeCharacteristicHandle(handle, Conversion.uint16_to_uint8_array(1))):
			exit(1)
		while (True):
			getConsumption(addresses[0])
#			time.sleep(0.1)

	else:
		while (True):
			# Connect to peer device.
			if (ble.connect(addresses[address_ind])):
				# Subscribe for notifications
				handle = ble.getHandle(CHAR_POWER_CONSUMPTION) + 2
				if (ble.writeCharacteristicHandle(handle, Conversion.uint16_to_uint8_array(1))):
					getConsumption(addresses[address_ind])

			# Disconnect from peer device if not done already and clean up.
			ble.disconnect()

			time.sleep(1)
			address_ind = (address_ind+1) % len(addresses)


