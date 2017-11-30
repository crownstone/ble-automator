import os, sys
import json

####################
# Read config file #
####################
def readAddresses(filename):
	"""
	Function to get BLE addresses from a json config file
	:param filename:
	:type filename: str
	:rtype List
	"""
	if not os.path.exists(filename):
		print "Config file does not seem to exist"
		return []
	try:
		configFile = open(filename)
		config = json.load(configFile)
	except Exception, e:
		print "Could not open/parse config file: %s" % (filename)
		print e
		return []
	return config["addresses"]

def readKeys(filename):
	"""
	Function get keys from a json config file
	:param filename:
	:type filename: str
	:rtype List
	"""
	if not os.path.exists(filename):
		print "Config file does not seem to exist"
		return []
	try:
		configFile = open(filename)
		config = json.load(configFile)
	except Exception, e:
		print "Could not open/parse config file: %s" % (filename)
		print e
		return []
	return config["keys"]


