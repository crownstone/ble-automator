#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import os, sys, datetime, math
from bleAutomator import *

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
		ble_rec.connect(addresses[address_ind])
		
		# Make the crownstone sample the current, give it some time to sample
		ble_rec.writeString('5b8d0002-6f20-11e4-b116-123b93f75cba', '03')
		time.sleep(1)
		
		# Read the current curve
		uuid = '5b8d0003-6f20-11e4-b116-123b93f75cba'
		# Read the current consumption (average of curve)
		#uuid = '5b8d0004-6f20-11e4-b116-123b93f75cba'
		curve = ble_rec.readString(uuid)
		if (curve != False):
			
			print curve
			
			f = open(options.data_file, 'a')
			f.write('%f %s %s' % (time.time(), addresses[address_ind], uuid))
			
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
			## old ## int8_t   sampleIncrements[]     interlaced difference with previous current/voltage sample, array is of length numSamples-2
			# int8_t   currentIncrements[]    difference with previous current sample, array is of length numSamples-1
			# int8_t   voltageIncrements[]    difference with previous voltage sample, array is of length numSamples-1
			# int8_t   timeIncrements[]       difference with previous timestamp, array is of length numSamples-1
			
			index=0
			
			# Read num samples
			numSamples = convert_hex_string_to_uint16_array(curve, index, 1)[0]
			f.write(' %i' % (numSamples))
			index+=2
			
			# Read first current sample
			current = convert_hex_string_to_uint16_array(curve, index, 1)[0]
			index+=2
			
			# Skip reading last current sample
			index+=2
			
			# Read first voltage sample
			voltage = convert_hex_string_to_uint16_array(curve, index, 1)[0]
			index+=2
			
			# Skip reading last voltage sample
			index+=2
			
			# Read first and last time stamp
			tStart = convert_hex_string_to_uint32_array(curve, index, 1)[0]
			index+=4
			tEnd = convert_hex_string_to_uint32_array(curve, index, 1)[0]
			index+=4
			t=tStart
			
			if (numSamples > 1):
				#dSamples = convert_hex_string_to_uint8_array(curve, index, numSamples-2)
				#index += numSamples-2
				
				numCurrentSamples = int(math.floor(numSamples/2))
				numVoltageSamples = int(math.floor(numSamples/2))
				
				currentIncrements = convert_hex_string_to_uint8_array(curve, index, numCurrentSamples-1)
				index += numCurrentSamples-1
				
				voltageIncrements = convert_hex_string_to_uint8_array(curve, index, numVoltageSamples-1)
				index += numVoltageSamples-1
				
				dts = convert_hex_string_to_uint8_array(curve, index, numSamples-1)
				index += numSamples-1
				
				#currentSamples = [current]
				#voltageSamples = [voltage]
				#n=0
				#for inc in dSamples:
					## convert uint8 to int8
					#diff = inc
					#if (diff > 127):
						#diff -= 256
					#if (n%2 == 0):
						#current += diff
						#currentSamples.append(current)
					#else:
						#voltage += diff
						#voltageSamples.append(voltage)
					#n+=1
				
				#for current in currentSamples:
					#f.write(' %i' % (current))
				
				#for voltage in voltageSamples:
					#f.write(' %i' % (voltage))
				
				f.write(' %i' % (current))
				for inc in currentIncrements:
					# convert uint8 to int8
					diff = inc
					if (diff > 127):
						diff -= 256
					current += diff
					f.write(' %i' % (current))
				
				f.write(' %i' % (voltage))
				for inc in voltageIncrements:
					# convert uint8 to int8
					diff = inc
					if (diff > 127):
						diff -= 256
					voltage += diff
					f.write(' %i' % (voltage))
				
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
		ble_rec.disconnect()
		
		time.sleep(1)
		address_ind = (address_ind+1) % len(addresses)
