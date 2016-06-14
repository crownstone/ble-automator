#!/usr/bin/env python

__author__ = 'Bart van Vliet'

""" This script is deprecated! """
import os, sys, datetime
from bleAutomator import *

## TODO: TBU, NEEDS TO BE UPDATED

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

	ble_rec = BleAutomator(options.interface, options.verbose)

	addresses = readAddresses(options.configFile)
	if (addresses == False):
		sys.exit(1)
	address_ind = 0

	# Endless loop:
	while (True):
		# Connect to peer device.
		ble.connect(addresses[address_ind])

		# Make the crownstone sample the current, give it some time to sample
		ble.writeString('5b8d0002-6f20-11e4-b116-123b93f75cba', '03')
		time.sleep(1)

		# Read the current curve
		uuid = '5b8d0003-6f20-11e4-b116-123b93f75cba'
		# Read the current consumption (average of curve)
		#uuid = '5b8d0004-6f20-11e4-b116-123b93f75cba'
		curve = ble.readString(uuid)
		if (curve != False):

			print curve

			f = open(options.data_file, 'a')
			f.write('%f %s %s' % (time.time(), addresses[address_ind], uuid))

			# Layout of the data:
			# byte         type                     description
			#-----------------------------------------------
			# 0   - 1      uint16_t numSamples      number of samples, including firstSample
			# 2   - 3      uint16_t firstSample
			# 4   - 5      uint16_t lastSample
			# 6   - 9      uint32_t timeStart       timestamp of first sample
			# 10  - 13     uint32_t timeEnd         timestamp of last sample
			# 14  - N+12   int8_t   increments[]    difference with previous sample, array is of length numSamples-1
			# N+13- 2*N+11 int8_t   dts[]            difference with previous timestamp, array is of length numSamples-1

			numSamples = convert_hex_string_to_uint16_array(curve, 0, 1)[0]
			f.write(' %i' % (numSamples))

			tStart = convert_hex_string_to_uint32_array(curve, 6, 9)[0]
			tEnd = convert_hex_string_to_uint32_array(curve, 10, 13)[0]
#			f.write(' %i' % (tStart))
			t=tStart

			current = convert_hex_string_to_uint16_array(curve, 2, 3)[0]
			f.write(' %i' % (current))

			if (numSamples > 1):

				increments = convert_hex_string_to_uint8_array(curve, 14, numSamples+12)
				dts = convert_hex_string_to_uint8_array(curve, numSamples+13, 2*numSamples+11)
				for inc in increments:
					# convert uint8 to int8
					diff = inc
					if (diff > 127):
						diff -= 256
					current += diff

					f.write(' %i' % (current))

				f.write(' %i' % (t))
				for dt in dts:
					# convert uint8 to int8
					diff = dt
					if (diff > 127):
						diff -= 256
					t += diff

					f.write(' %i' % (t))

#			f.write(' %i' % (tEnd))
			f.write('\n')
			f.close()

		# wait a second to be able to receive the disconnect event from peer device.
		time.sleep(1)

		# Disconnect from peer device if not done already and clean up.
		ble.disconnect()

		time.sleep(1)
		address_ind = (address_ind+1) % len(addresses)
