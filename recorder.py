#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import os, sys, datetime
from bleAutomator import *


if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] -a <dfu_target_address>\n\nExample:\n\tdfu.py -i hci0 -a cd:e3:4a:47:1c:e4 -f data.txt',
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
		
		options, args = parser.parse_args()
	
	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)
	
	if (not options.address):
		parser.print_help()
		exit(2)
	
	#test = pexpect.spawn("gatttool -b '%s' -i '%s' -t random --char-read -a 0x0016" % (options.address.upper(), options.interface))
	#test.logfile = sys.stdout
	#try:
		#test.expect('Characteristic value ([0-9a-fA-F ]+) \r?\n', timeout=10)
	#except pexpect.EOF, e:
		#print e
	#print test.match.groups()
	#time.sleep(10)
	
	ble_rec = BleAutomator(options.interface, options.verbose)
	
	# Connect to peer device.
	ble_rec.connect(options.address)
	
	# Get all handles and cache them
	ble_rec.getHandles()
	
	# Make the crownstone sample the current, give it some time to sample
	ble_rec.writeString('5b8d0002-6f20-11e4-b116-123b93f75cba', '03')
	time.sleep(1)
	
	# Read the current curve
	uuid = '5b8d0003-6f20-11e4-b116-123b93f75cba'
	curve = ble_rec.readString(uuid)
	if (curve != False):
		f = open(options.data_file, 'a')
		f.write('%f %s %s' % (time.time(), options.address, uuid))
		curve_array = convert_buffer_to_uint16_array(curve)
		for i in curve_array:
			f.write(' %i' % (i))
		f.write('\n')
		f.close()
	
	# wait a second to be able to receive the disconnect event from peer device.
	time.sleep(1)
	
	# Disconnect from peer device if not done already and clean up.
	ble_rec.disconnect()
