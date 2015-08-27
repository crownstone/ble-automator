#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import os, sys, time
from bleAutomator import *



charac='96d20001-4bcf-11e5-885d-feff819cdc9f'

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
	
	ble_rec = BleAutomator(options.interface, options.verbose)
	
	# Connect to peer device.
	if (not ble_rec.connect(options.address)):
		exit(1)
	
	# Get unix time
	posix_time = int(time.time())
	arr8 = convert_uint32_to_uint8_array(posix_time)
	hexStr = convert_uint8_array_to_hex_string(arr8)
	
	# Write unix time to characteristic
	if (not ble_rec.writeString(charac, hexStr)):
		exit(1)
	
	# Disconnect from peer device if not done already and clean up.
	ble_rec.disconnect()
	
	exit(0)
