#!/usr/bin/env python
#
# savethemblobs.py
#   A simple script to grab all SHSH blobs from Apple that it's currently signing to save them locally and on Cydia server.
#   And now also grabs blobs already cached on Cydia and iFaith servers to save them locally.
#
# Copyright (c) 2013 Neal <neal@ineal.me>
#
# examples:
#   savethemblobs.py 1050808663311 iPhone3,1
#   savethemblobs.py 0x000000F4A913BD0F iPhone3,1 --overwrite
#   savethemblobs.py 1050808663311 n90ap --skip-cydia --skip-ifaith
#

import sys, os, argparse
import requests
import json


def firmwares_being_signed(device):
	url = 'http://api.ineal.me/tss/%s' % (device)
	headers = {'User-Agent': 'savethemblobs'}
	r = requests.get(url, headers=headers)
	return r.text

def tss_request_manifest(board, build):
	url = 'http://api.ineal.me/tss/manifest/%s/%s' % (board, build)
	headers = {'User-Agent': 'savethemblobs'}
	r = requests.get(url, headers=headers)
	return r.text

def available_blobs_on_cydia(ecid):
	url = 'http://cydia.saurik.com/tss@home/api/check/%s' % (ecid)
	headers = {'User-Agent': 'savethemblobs'}
	r = requests.get(url, headers=headers)
	return r.text

def available_blobs_on_ifaith(ecid, board):
	url = 'http://iacqua.ih8sn0w.com/submit.php?ecid=%s&board=%s' % ("{0:0{1}X}".format(int(ecid), 16), board)
	headers = {'User-Agent': 'iacqua-1.5-941'}
	r = requests.get(url, headers=headers)
	return r.text

def request_blobs_from_apple(manifest):
	url = 'http://gs.apple.com/TSS/controller?action=2'
	headers = {'User-Agent': 'savethemblobs'}
	r = requests.post(url, headers=headers, data=manifest)
	return r.text

def request_blobs_from_cydia(manifest):
	url = 'http://gs.apple.com/TSS/controller?action=2'
	headers = {'User-Agent': 'savethemblobs'}
	r = requests.post(url, headers=headers, data=manifest)
	return r.text

def request_blobs_from_ifaith(ecid, board, ios):
	url = 'http://iacqua.ih8sn0w.com/submit.php?ecid=%s&board=%s&ios=%s' % ("{0:0{1}X}".format(int(ecid), 16), board, ios)
	headers = {'User-Agent': 'iacqua-1.5-941'}
	r = requests.get(url, headers=headers)
	return r.text

def submit_blobs_to_cydia(cpid, bdid, ecid, data):
	url = 'http://cydia.saurik.com/tss@home/api/store/%s/%s/%s' % (cpid, bdid, ecid)
	headers = {'User-Agent': 'savethemblobs'}
	r = requests.post(url, headers=headers, data=data)
	return r.text


def main(argv):
	parser = argparse.ArgumentParser()
	parser.add_argument('ecid', help='device ECID in int or hex (prefix hex with 0x)')
	parser.add_argument('device', help='device identifier/boardconfig (eg. iPhone3,1/n90ap)')
	parser.add_argument('--save-dir', help='local dir for saving blobs (default: $HOME/.shsh)', default=os.path.join(os.getenv('HOME'), '.shsh'))
	parser.add_argument('--overwrite', help='overwrite any existing blobs', action='store_true')
	parser.add_argument('--no-submit-cydia', help='don\'t submit blobs to Cydia server', action='store_false')
	parser.add_argument('--skip-cydia', help='skip fetching blobs from Cydia server', action='store_true')
	parser.add_argument('--skip-ifaith', help='skip fetching blobs from iFaith server', action='store_true')

	args = parser.parse_args()

	ecid = args.ecid
	device = args.device
	save_dir = args.save_dir
	overwrite = args.overwrite
	submit_to_cydia = args.no_submit_cydia
	skip_fetching_from_cydia = args.skip_cydia
	skip_fetching_from_ifaith = args.skip_ifaith

	if not os.path.exists(save_dir):
		os.makedirs(save_dir)

	ecid = str(int(ecid, 0))
	firmwares_apple_is_signing = []

	print 'Fetching firmwares Apple is currently signing for %s' % (device)
	devices = json.loads(firmwares_being_signed(device))
	for device_name, device_info in devices.items():
		board = str(device_info['board'])
		model = str(device_info['model'])
		cpid = str(device_info['cpid'])
		bdid = str(device_info['bdid'])
		for firmware in device_info['firmwares']:
			firmwares_apple_is_signing.append([ str(firmware['build']), str(firmware['version']) ])

	for b in firmwares_apple_is_signing:
		build = b[0]
		version = b[1]
		save_path = os.path.join(save_dir, '%s_%s_%s-%s.shsh' % (ecid, model, version, build))

		if not os.path.exists(save_path) or overwrite:
			print 'Grabbing TSS request manifest for firmware build %s' % (build)
			manifest = tss_request_manifest(board, build).replace('<string>$ECID$</string>', '<integer>' + ecid + '</integer>')

			print 'Requesting blobs from Apple'
			blobs = request_blobs_from_apple(manifest).replace('STATUS=0&MESSAGE=SUCCESS&REQUEST_STRING=', '')

			print 'Saving blobs to %s' % (save_path)
			f = open(save_path, 'w')
			f.write(blobs)
			f.close()

			if submit_to_cydia:
				print 'Submitting blobs to Cydia server'
				submit_blobs_to_cydia(cpid, bdid, ecid, blobs)

		else:
			print 'Skipping build %s; blobs already exist at %s' % (build, save_path)

	if not skip_fetching_from_cydia:
		print 'Fetching blobs available on Cydia server'
		blobs_available_on_cydia = json.loads(available_blobs_on_cydia(ecid))
		for b in blobs_available_on_cydia:
			save_path = os.path.join(save_dir, '%s_%s_%s-%s.shsh' % (ecid, model, b['firmware'], b['build']))

			if not os.path.exists(save_path) or overwrite:
				print 'Grabbing TSS request manifest for firmware build %s' % (b['build'])
				manifest = tss_request_manifest(board, b['build']).replace('<string>$ECID$</string>', '<integer>' + ecid + '</integer>')

				print 'Requesting blobs from Cydia'
				blobs = request_blobs_from_cydia(manifest).replace('STATUS=0&MESSAGE=SUCCESS&REQUEST_STRING=', '')

				print 'Saving blobs to %s' % (save_path)
				f = open(save_path, 'w')
				f.write(blobs)
				f.close()

			else:
				print 'Skipping build %s; blobs already exist at %s' % (b['build'], save_path)

	if not skip_fetching_from_ifaith:
		print 'Fetching blobs available on iFaith server'
		blobs_available_on_ifaith = available_blobs_on_ifaith(ecid, board)
		for b in blobs_available_on_ifaith.split('.shsh'):
			if b:
				ios = b.split(' ')[0]
				bld = b.split(' ')[1].replace('(', '').replace(')', '')
				save_path = os.path.join(save_dir, '%s_%s_%s-%s.ifaith' % (ecid, model, ios, bld))

				if not os.path.exists(save_path) or overwrite:
					print 'Requesting blobs from iAcqua'
					blobs = request_blobs_from_ifaith(ecid, board, b)

					print 'Saving blobs to %s' % (save_path)
					f = open(save_path, 'w')
					f.write(blobs)
					f.close()

				else:
					print 'Skipping build %s; blobs already exist at %s' % (bld, save_path)


if __name__ == '__main__':
	main(sys.argv[1:])
