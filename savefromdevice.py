#!/usr/bin/env python
# savefromdevice.py - save blobs etc from a device

import sys, os, argparse
import requests
import json
import savethemblobs
from MobileDevice import *

def get_connected_devices(): 
	print "Checking for connected devices..."
	return list_devices().values()

def get_user_friendly_name(identifier):
	url = 'http://api.ios.icj.me/v2/%s/latest/name' % (identifier)
	r = requests.get(url, headers={'User-Agent': savethemblobs.USER_AGENT})
	return r.text	

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--save-dir', help='local dir for saving blobs (default: ~/.shsh)', default=os.path.join(os.path.expanduser('~'), '.shsh'))
	parser.add_argument('--overwrite', help='overwrite any existing blobs', action='store_true')
	parser.add_argument('--overwrite-apple', help='overwrite any existing blobs (only from Apple)', action='store_true')
	parser.add_argument('--overwrite-cydia', help='overwrite any existing blobs (only from Cydia)', action='store_true')
	parser.add_argument('--overwrite-ifaith', help='overwrite any existing blobs (only from iFaith)', action='store_true')
	parser.add_argument('--no-submit-cydia', help='don\'t submit blobs to Cydia server', action='store_true')
	parser.add_argument('--skip-cydia', help='skip fetching blobs from Cydia server', action='store_true')
	parser.add_argument('--skip-ifaith', help='skip fetching blobs from iFaith server', action='store_true')
	return parser.parse_args()

def main():
	devices = get_connected_devices()

	for device in devices:
		device.connect()

		identifier = device.get_value(name=u'ProductType')
		version = device.get_value(name=u'ProductVersion')
		buildid = device.get_value(name=u'BuildVersion')

		print ""

		response = raw_input("Found %s on %s (%s).\nWould you like to save blobs for it? (y/n): " % (get_user_friendly_name(identifier), version, buildid))

		if(response != "y"):
			continue

		ecid = device.get_value(name=u'UniqueChipID')
		print "ECID: %s, Identifier: %s" % (ecid, identifier)

		print ""

		args = parse_args()
		args.device = identifier
		args.ecid = str(ecid)

		savethemblobs.main(args)


if __name__ == '__main__':
	main()
