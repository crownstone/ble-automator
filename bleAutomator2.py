#!/usr/bin/env python

__author__ = 'Bart van Vliet'

import os, sys
import pexpect
import optparse
import time
import json

import bluepy.btle


######################
# BleAutomator class #
######################
class BleAutomator(object):
	def __init__(self, interface, verbose=False):
		self.targetAddress = ""
		self.flags = "-t random"
		self.interface = interface
		self.verbose = verbose
		self.handles = {}
		self.connected = False
#		self.connection = bluepy.btle.Peripheral(None, bluepy.btle.ADDR_TYPE_PUBLIC, self.interface)
		self.connection = bluepy.btle.Peripheral()

	def connect(self, targetAddress, flags="default"):
		self.targetAddress = targetAddress
		if (flags != "default"):
			self.flags = flags

		try:
			self.connection.connect(self.targetAddress, bluepy.btle.ADDR_TYPE_RANDOM, self.interface)
		except bluepy.btle.BTLEException, e:
			print e
			return False

		self.connected = True
		print "Connected."
		return True


	def disconnect(self):
		self.clearHandles()
		self.connection.disconnect()

	# Get handles of all characteristics, cache results
	def getHandles(self):
		if (not self.connected):
			print "Unable to get handles, not connected"
			return False

		try:
			chars = self.connection.getCharacteristics()
		except bluepy.btle.BTLEException, e:
			print e
			return False

		for char in chars:
			self.handles[str(char.uuid)] = char.getHandle()
			print "handle:", char.getHandle(), "uuid:", char.uuid

		print self.handles
		# services = self.connection.discoverServices()
		# print services
		# for srvUUID in services:
		# 	service = services[srvUUID]
		# 	print str(service)
		# 	chrs = service.getCharacteristics()
		# 	for chr in chrs:
		# 		print chr.getHandle(), "uuid", chr.uuid

		return True

	def clearHandles(self):
#		 self.handles = {}
		pass

	# Get handle of a specific characteristic, cache result
	def getHandle(self, uuid):
		if (uuid not in self.handles):
			if (not self.connected):
				print "Unable to get handle, not connected"
				return False
			else:
				self.getHandles()
				if (uuid not in self.handles):
					return False
		return self.handles[uuid]

	def readCharacteristic(self, uuid):
		"""
		Read the value from a specific characteristic
		:param uuid: The uuid of the characteristic
		:type uuid: str
		:rtype: bytearray
		"""
		handle = self.getHandle(uuid)
		if not handle:
			print "no such handle"
			return []
		try:
			data = self.connection.readCharacteristic(handle)
		except bluepy.btle.BTLEException, e:
			print e
			return []
		return bytearray(data)

	def writeCharacteristic(self, uuid, data):
		"""
		Write a value to a specific characteristic
		:param uuid: The uuid of the characteristic
		:type uuid: str
		:param data: The data to send
		:type data: bytearray | List
		:rtype: bool
		"""
		handle = self.getHandle(uuid)
		if not handle:
			return False
		try:
			self.connection.writeCharacteristic(handle, bytearray(data), False)
		except bluepy.btle.BTLEException, e:
			print e
			return False
		return True

if __name__ == '__main__':
	ble = BleAutomator("hci1")
#	ble.connect("E7:64:B5:70:AC:25")
	ble.connect("E7:87:47:1F:B3:7C")
	ble.getHandles()

	ble.writeCharacteristic("5b8d0002-6f20-11e4-b116-123b93f75cba", [3])
	time.sleep(1)
	curve = ble.readCharacteristic("5b8d0003-6f20-11e4-b116-123b93f75cba") # Power curve
	print "lenght:", len(curve)
	print "data:", curve[0], curve[1], curve[2], curve[3], "..."

	temp = ble.readCharacteristic("f5f90001-59f9-11e4-aa15-123b93f75cba") # temperature
	print "temperature:", temp[0]
	time.sleep(1)
	ble.disconnect()