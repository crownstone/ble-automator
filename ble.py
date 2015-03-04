#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import os, sys
import pexpect
import optparse
import time
from intelhex import IntelHex


def getHandle(ble_connection, uuid):
	ble_connection.sendline('characteristics')
	try:
		ble_connection.expect('char value handle: 0x([0-9a-fA-F]+), uuid: %s' % (uuid), timeout=2)
		#handle = '0x%s' % (ble_connection.match.groups()[0])
		handle = ble_connection.match.groups()[0]
		print 'handle = %s' % (handle)
		return handle
	except pexpect.TIMEOUT, e:
		return False

def convert_uint32_to_array(value):
	""" Convert a number into an array of 4 bytes (LSB). """
	return [
		(value >> 0 & 0xFF),
		(value >> 8 & 0xFF),
		(value >> 16 & 0xFF),
		(value >> 24 & 0xFF)
	]

def convert_uint16_to_array(value):
	""" Convert a number into an array of 2 bytes (LSB). """
	return [
		(value >> 0 & 0xFF),
		(value >> 8 & 0xFF)
	]

def convert_array_to_hex_string(arr):
	hex_str = ""
	for val in arr:
		if val > 255:
			raise Exception("Value is greater than it is possible to represent with one byte")
		hex_str += "%02x" % val
	return hex_str


class BleRecorder(object):
	# for S130
	#ctrlpt_handle = 0x10
	#ctrlpt_cccd_handle = 0x11
	#data_handle = 0x0E

	# for S110
	ctrlpt_handle = '0d'      # this is automatically being discovered in the _dfu_check_mode function
	ctrlpt_cccd_handle = '0e' # these are automatically discovered in _dfu_get_handles
	data_handle = '0b'        # these are automatically discovered in _dfu_get_handles

	def __init__(self, target_mac, interface, verbose=False):
		self.target_mac = target_mac
		self.interface = interface
		self.verbose = verbose
		self.characteristics = {}
		self.handles = {}
		print verbose
		print "gatttool -b '%s' -i '%s' -t random --interactive" % (target_mac, interface)
		self.ble_conn = pexpect.spawn("gatttool -b '%s' -i '%s' -t random --interactive" % (target_mac, interface))
		if (verbose):
			self.ble_conn.logfile = sys.stdout

	# Connect to peer device.
	def scan_and_connect(self):
		print "Wait for scan result and connect"
		try:
			self.ble_conn.expect('\[LE\]>', timeout=10)
		except pexpect.TIMEOUT, e:
			print "Timeout on scan for target"
			return False
		
		print "Send: connect"
		self.ble_conn.sendline('connect')
		
		try:
			res = self.ble_conn.expect(['successful','CON'], timeout=10)
		except pexpect.TIMEOUT, e:
			print "timeout on connect to target"
			return False
		
		print 'Connected.'
		return True

	# Get handles of all characteristics, cache results
	def getHandles(self):
		self.ble_conn.sendline('characteristics')
		while (True):
			try:
				self.ble_conn.expect('char value handle: 0x([0-9a-fA-F]+), uuid: ([0-9a-zA-Z\-]+)\r?\n', timeout=2)
				#handle = '0x%s' % (ble_connection.match.groups()[0])
				handle = self.ble_conn.match.groups()[0]
				uuid = self.ble_conn.match.groups()[1]
				print 'uuid=%s -- handle=%s' % (uuid, handle)
				self.handles[uuid] = handle
			except pexpect.TIMEOUT, e:
				break

	# Get handle of a specific characteristic, cache result
	def getHandle(self, uuid):
		if (uuid not in self.handles):
			handle = getHandle(self.ble_conn, uuid)
			if not handle:
				return False
			self.handles[uuid] = handle
		return self.handles[uuid]

	# Read the value of a specific characteristic
	# Uuid must be a string
	# Value is returned as string
	def readUUID(self, uuid):
		handle = self.getHandle(uuid)
		if not handle:
			return False
		self.ble_conn.sendline('char-read-hnd 0x%02s' % (handle))
		
		try:
			self.ble_conn.expect('Characteristic value/descriptor: ([0-9a-fA-F ]+) \r?\n', timeout=2)
			# Check if the match group contains any item, not sure if this can go wrong at all
			if (len(self.ble_conn.match.groups()) < 1):
				return False
			return self.ble_conn.match.groups()[0]
		except pexpect.TIMEOUT, e:
			print "Timeout on read of %s" % (uuid)
			return False
		
		# This way doesn't work well: it only returns first 20 bytes
		#try:
			#self.ble_conn.sendline('char-read-uuid %s' % (uuid))
			#self.ble_conn.expect('handle: (0x[0-9a-fA-F]+)\s+value: (0x[0-9a-fA-F ]+) \r?\n', timeout=2)

	# Write a value to a specific characteristic
	# Uuid must be a string
	# Value must be a string
	def writeUUID(self, uuid, value):
		handle = self.getHandle(uuid)
		if not handle:
			return False
		
		self.ble_conn.sendline('char-write-req 0x%02s %s' % (handle, value))
		try:
			self.ble_conn.expect('Characteristic value was written successfully', timeout=2)
			return True
		except pexpect.TIMEOUT, e:
			print "Failed to write %s to %s" % (value, uuid)
			return False

	# Disconnect from peer device if not done already and clean up.
	def disconnect(self):
		self.ble_conn.sendline('exit')
		self.ble_conn.close()


if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] -a <dfu_target_address>\n\nExample:\n\tdfu.py -i hci0 -a cd:e3:4a:47:1c:e4',
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
	
	#test = pexpect.spawn("gatttool -b '%s' -i '%s' -t random --char-read -a 0x0016" % (options.address.upper(), options.interface))
	#test.logfile = sys.stdout
	#try:
		#test.expect('Characteristic value ([0-9a-fA-F ]+) \r?\n', timeout=10)
	#except pexpect.EOF, e:
		#print e
	#print test.match.groups()
	#time.sleep(10)
	
	ble_rec = BleRecorder(options.address.upper(), options.interface, options.verbose)
	
	# Connect to peer device.
	ble_rec.scan_and_connect()
	
	# Get all handles and cache them
	ble_rec.getHandles()
	
	# Read some characteristics
	print ble_rec.readUUID('5b8d0001-6f20-11e4-b116-123b93f75cba')
	print ble_rec.readUUID('5b8d0002-6f20-11e4-b116-123b93f75cba')
	print ble_rec.readUUID('5b8d0003-6f20-11e4-b116-123b93f75cba')
	print ble_rec.readUUID('5b8d0004-6f20-11e4-b116-123b93f75cba')
	
	# Write some characteristics
	ble_rec.writeUUID('5b8d0001-6f20-11e4-b116-123b93f75cba', 'ff')
	ble_rec.writeUUID('5b8d0001-6f20-11e4-b116-123b93f75cba', '00')
	ble_rec.writeUUID('5b8d0001-6f20-11e4-b116-123b93f75cba', 'ff')
	ble_rec.writeUUID('5b8d0001-6f20-11e4-b116-123b93f75cba', '00')
	ble_rec.writeUUID('5b8d0001-6f20-11e4-b116-123b93f75cba', 'ff')
	ble_rec.writeUUID('5b8d0001-6f20-11e4-b116-123b93f75cba', '00')
	
	# wait a second to be able to receive the disconnect event from peer device.
	time.sleep(1)
	
	# Disconnect from peer device if not done already and clean up.
	ble_rec.disconnect()
