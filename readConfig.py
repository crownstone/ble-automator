#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import os, sys, datetime
from bleAutomator import *



charac_select='f5f90008-59f9-11e4-aa15-123b93f75cba'
charac_read='f5f90009-59f9-11e4-aa15-123b93f75cba'

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] -a <ble address> -t <type>\n\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4 -t 3',
									version='0.1')
		
		parser.add_option('-a', '--address',
				action='store',
				dest="address",
				type="string",
				default=None,
				help='DFU target address. (Can be found by running "hcitool lescan")'
				)
		parser.add_option('-t', '--type',
				action='store',
				dest="configType",
				type="int",
				default=0,
				help='what configuration to read (integer)'
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
	
	# Write type to select
	if (not ble_rec.writeString(charac_select, convert_uint8_to_hex_string(options.configType))):
		exit(1)
	
	# Read the value of selected type
	readStr = ble_rec.readString(charac_read)
	if (readStr == False):
		print "Couldn't read value"
		exit(1)
	arr8 = convert_hex_string_to_uint8_array(readStr)
	valStr = ""
	for i in range(0, len(arr8)):
		valStr += chr(arr8[i])
	
	print "Value: %s" % (valStr)
	
	# Disconnect from peer device if not done already and clean up.
	ble_rec.disconnect()
	
	exit(0)
