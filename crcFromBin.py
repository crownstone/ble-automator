from Bluenet import *
from intelhex import IntelHex

import sys
import os

def binFileToArr(filename):
	buf = bytearray(os.path.getsize(filename))
	with open(filename, 'rb') as f:
		f.readinto(buf)
	return buf

def crcFromBin(filename):
	buf = binFileToArr(filename)
	crc = Bluenet.crc16_ccitt(buf, len(buf))
	print hex(crc)
	return crc

def hexFileToArr(filename):
	ih = IntelHex(filename)
	buf = ih.tobinarray()
	return buf

def crcFromHex(filename):
	buf = hexFileToArr(filename)
	crc = Bluenet.crc16_ccitt(buf, len(buf))
	print hex(crc)
	return crc

if __name__ == '__main__':
	pass
	# print hex(crc)
