#!/usr/bin/env python

#TODO: crc calculation has a problem for bootloader and softdevice,
# but works for application ??!!

import sys
import os
import optparse
import time
from intelhex import IntelHex
import logging
from Bluenet import *
# import manifestTemplates
import shutil
import struct
import json
import copy

manifestTemplate = {
    "manifest": {
        "dfu_version": 0.5
    }
}

deviceTemplate = {
    "bin_file": "",
    "dat_file": "",
    "init_packet_data": {
        "application_version": 4294967295,
        "device_revision": 65535,
        "device_type": 65535,
        "firmware_crc16": 0,
        "softdevice_req": []
    }
}

def hexFileToArr(filename):
	ih = IntelHex(filename)
	buf = ih.tobinarray()
	return buf

def crcFromHex(filename):
	buf = hexFileToArr(filename)
	crc = Bluenet.crc16_ccitt(buf, len(buf))
	# print hex(crc)
	return crc

def verifyFile(filename):
	if not os.path.isfile(filename):
		# log.e("Hex file not found!")
		print "Hex file not found!"
		exit(2)
	path, ext = os.path.splitext(filename)
	if ext != '.hex':
		# log.e("Only HEX file upload supported")
		print "Only HEX file upload supported"
		exit(2)

def createDatFile(name, crc, sd_req):
	buf = struct.pack('<IHHHHH', 0xffffffff, 0xffff, 0xffff, 1, int(sd_req, 16), crc)
	file = open('tmp/%s.dat' %name, 'wb')
	file.write(buf)
	file.close()

def createApplicationDFU(filename, sd_req):
	createDFU("application", filename, sd_req)

def createDFU(type, filename, sd_req):
	verifyFile(filename)

	path, nameExt = os.path.split(filename)
	name, ext = os.path.splitext(nameExt)

	os.mkdir('tmp')
	try:
		# os.chdir('tmp')
		crc = crcFromHex(filename)
		createDatFile(name, crc, sd_req)

		createManifest(type, name, crc, sd_req)

		shutil.copyfile(filename, 'tmp/' + nameExt)

		# os.chdir('..')
		shutil.make_archive(type, 'zip', 'tmp')
	finally:
		shutil.rmtree('tmp')

def createManifest(type, name, crc, sd_req):
	manifest = copy.deepcopy(manifestTemplate)
	device = copy.deepcopy(deviceTemplate)
	device["bin_file"] = '%s.hex' %name
	device["dat_file"] = '%s.dat' %name
	device["init_packet_data"]["firmware_crc16"] = crc
	device["init_packet_data"]["softdevice_req"].append(int(sd_req, 16))
	manifest["manifest"][type] = device

	file = open('tmp/manifest.json', 'w')
	json.dump(manifest, file, indent = 4, sort_keys = True)
	file.close()

def createBootloaderDFU(filename, sd_req):
	createDFU("bootloader", filename, sd_req)

def createSoftdeviceDFU(filename, sd_req):
	createDFU("softdevice", filename, sd_req)

if __name__ == '__main__':

	print os.getcwd()

	log = logging.Logger(logging.LogLevel.INFO)
	try:
		parser = optparse.OptionParser(usage='%prog -a <application_hex> -b <bootloader_hex> -s <softdevice_hex> -r <required_softdevice>\n\nExample:\n\t%prog.py -a crownstone.hex',
									   version='0.1')

		parser.add_option('-a', '--application',
				action='store',
				dest="application_hex",
				type="string",
				default=None,
				help='Application hex file'
		)
		parser.add_option('-b', '--bootloader',
				action='store',
				dest="bootloader_hex",
				type="string",
				default=None,
				help='Bootloader hex file'
		)
		parser.add_option('-s', '--softdevice',
				action='store',
				dest="softdevice_hex",
				type="string",
				default=None,
				help='Softdevice hex file'
		)
		parser.add_option('-r', '--sd-req',
				action='store',
				dest="sd_req",
				type="string",
				default="0xfffe",
				help='supported Soft Device'
		)
		parser.add_option('-v', '--verbose',
				action='store_true',
				dest="verbose",
				help='Be verbose.'
		)
		parser.add_option('-d', '--debug',
				action='store_true',
				dest="debug",
				help='Debug mode.'
		)

		options, args = parser.parse_args()

	except Exception, e:
		log.e(str(e))
		log.i("For help use --help")
		exit(2)

	# if (options.application_hex and options.bootloader_hex) or \
	#    (options.application_hex and options.softdevice_hex) or \
	#    (options.bootloader_hex and options.softdevice_hex):
	# 	log.e("Only single update supported for now!")
	# 	exit(2)

	if not (options.application_hex or options.bootloader_hex or options.softdevice_hex):
		log.e("At least one hex file has to be provided!")
		parser.print_help()
		exit(2)

	if (options.verbose):
		log.setLogLevel(logging.LogLevel.DEBUG)
	if (options.debug):
		log.setLogLevel(logging.LogLevel.DEBUG2)

	if options.application_hex:
		createApplicationDFU(options.application_hex, options.sd_req)

	if options.bootloader_hex:
		createBootloaderDFU(options.bootloader_hex, options.sd_req)

	if options.softdevice_hex:
		createSoftdeviceDFU(options.softdevice_hex, options.sd_req)
