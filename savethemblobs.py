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

USER_AGENT = 'savethemblobs'
IACQUA_USER_AGENT = 'iacqua-1.5-941'

def firmwares_being_signed(device):
	url = 'http://api.ineal.me/tss/%s' % (device)
	headers = {'User-Agent': USER_AGENT}
	r = requests.get(url, headers=headers)
	return r.text

def tss_request_manifest(board, build, ecid):
	url = 'http://api.ineal.me/tss/manifest/%s/%s' % (board, build)
	headers = {'User-Agent': USER_AGENT}
	r = requests.get(url, headers=headers)
	manifest = r.text.replace('<string>$ECID$</string>', '<integer>%s</integer>' % (ecid))
	return manifest

def available_blobs_on_cydia(ecid):
	url = 'http://cydia.saurik.com/tss@home/api/check/%s' % (ecid)
	headers = {'User-Agent': USER_AGENT}
	r = requests.get(url, headers=headers)
	return r.text

def available_blobs_on_ifaith(ecid, board):
	url = 'http://iacqua.ih8sn0w.com/submit.php?ecid=%s&board=%s' % ("{0:0{1}X}".format(int(ecid), 16), board)
	headers = {'User-Agent': IACQUA_USER_AGENT}
	r = requests.get(url, headers=headers)
	return r.text

def request_blobs_from_apple(manifest):
	url = 'http://gs.apple.com/TSS/controller?action=2'
	headers = {'User-Agent': USER_AGENT}
	r = requests.post(url, headers=headers, data=manifest)
	return parse_tss_response(r.text)

def request_blobs_from_cydia(manifest):
	url = 'http://cydia.saurik.com/TSS/controller?action=2'
	headers = {'User-Agent': USER_AGENT}
	r = requests.post(url, headers=headers, data=manifest)
	return parse_tss_response(r.text)

def request_blobs_from_ifaith(ecid, board, ios):
	url = 'http://iacqua.ih8sn0w.com/submit.php?ecid=%s&board=%s&ios=%s' % ("{0:0{1}X}".format(int(ecid), 16), board, ios)
	headers = {'User-Agent': IACQUA_USER_AGENT}
	r = requests.get(url, headers=headers)
	return r.text

def submit_blobs_to_cydia(cpid, bdid, ecid, data):
	url = 'http://cydia.saurik.com/tss@home/api/store/%s/%s/%s' % (cpid, bdid, ecid)
	headers = {'User-Agent': USER_AGENT}
	requests.post(url, headers=headers, data=data)

def write_to_file(file_path, data):
	f = open(file_path, 'w')
	f.write(data)
	f.close()

def parse_tss_response(response):
	ret = {}
	for v in response.split('&'):
		r = v.split('=',1)
		ret[r[0]] = r[1]
	return ret

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('ecid', help='device ECID in int or hex (prefix hex with 0x)')
	parser.add_argument('device', help='device identifier/boardconfig (eg. iPhone3,1/n90ap)')
	parser.add_argument('--save-dir', help='local dir for saving blobs (default: ~/.shsh)', default=os.path.join(os.path.expanduser('~'), '.shsh'))
	parser.add_argument('--overwrite', help='overwrite any existing blobs', action='store_true')
	parser.add_argument('--overwrite-apple', help='overwrite any existing blobs (only from Apple)', action='store_true')
	parser.add_argument('--overwrite-cydia', help='overwrite any existing blobs (only from Cydia)', action='store_true')
	parser.add_argument('--overwrite-ifaith', help='overwrite any existing blobs (only from iFaith)', action='store_true')
	parser.add_argument('--no-submit-cydia', help='don\'t submit blobs to Cydia server', action='store_true')
	parser.add_argument('--skip-cydia', help='skip fetching blobs from Cydia server', action='store_true')
	parser.add_argument('--skip-ifaith', help='skip fetching blobs from iFaith server', action='store_true')
	return parser.parse_args()


def main(argv):
	args = parse_args()

	ecid = int(args.ecid, 0)

	if not os.path.exists(args.save_dir):
		os.makedirs(args.save_dir)

	print 'Fetching firmwares Apple is currently signing for %s' % (args.device)
	devices = json.loads(firmwares_being_signed(args.device))
	for device_name, device_info in devices.items():
		board = device_info['board']
		model = device_info['model']
		cpid = device_info['cpid']
		bdid = device_info['bdid']
		for f in device_info['firmwares']:
			save_path = os.path.join(args.save_dir, '%s_%s_%s-%s.shsh' % (ecid, model, f['version'], f['build']))

			if not os.path.exists(save_path) or args.overwrite_apple or args.overwrite:
				print 'Grabbing TSS request manifest for firmware build %s' % (f['build'])
				manifest = tss_request_manifest(board, f['build'], ecid)

				print 'Requesting blobs from Apple'
				r = request_blobs_from_apple(manifest)

				if r['MESSAGE'] == 'SUCCESS':
					print 'Saving blobs to %s' % (save_path)
					write_to_file(save_path, r['REQUEST_STRING'])

					if not args.no_submit_cydia:
						print 'Submitting blobs to Cydia server'
						submit_blobs_to_cydia(cpid, bdid, ecid, r['REQUEST_STRING'])

				else:
					print 'Error receiving blobs: %s [%s]' % (r['MESSAGE'], r['STATUS'])

			else:
				print 'Skipping build %s; blobs already exist at %s' % (f['build'], save_path)

	if not args.skip_cydia:
		print 'Fetching blobs available on Cydia server'
		blobs_available_on_cydia = json.loads(available_blobs_on_cydia(ecid))
		if blobs_available_on_cydia:
			for b in blobs_available_on_cydia:
				save_path = os.path.join(args.save_dir, '%s_%s_%s-%s.shsh' % (ecid, b['model'], b['firmware'], b['build']))

				if not os.path.exists(save_path) or args.overwrite_cydia or args.overwrite:
					print 'Grabbing TSS request manifest for firmware build %s' % (b['build'])
					manifest = tss_request_manifest(board, b['build'], ecid)

					print 'Requesting blobs from Cydia'
					r = request_blobs_from_cydia(manifest)

					if r['MESSAGE'] == 'SUCCESS':
						print 'Saving blobs to %s' % (save_path)
						write_to_file(save_path, r['REQUEST_STRING'])

					else:
						print 'Error receiving blobs: %s [%s]' % (r['MESSAGE'], r['STATUS'])

				else:
					print 'Skipping build %s; blobs already exist at %s' % (b['build'], save_path)

		else:
			print 'No blobs found on Cydia server'

	if not args.skip_ifaith:
		print 'Fetching blobs available on iFaith server'
		blobs_available_on_ifaith = available_blobs_on_ifaith(ecid, board)
		if '.shsh' in blobs_available_on_ifaith:
			for b in blobs_available_on_ifaith.split('.shsh'):
				if b:
					ios = b.split(' ')[0]
					bld = b.split(' ')[1].replace('(', '').replace(')', '')
					save_path = os.path.join(args.save_dir, '%s_%s_%s-%s.ifaith' % (ecid, model, ios, bld))

					if not os.path.exists(save_path) or args.overwrite_ifaith or args.overwrite:
						print 'Requesting blobs from iAcqua'
						blobs = request_blobs_from_ifaith(ecid, board, b)

						print 'Saving blobs to %s' % (save_path)
						write_to_file(save_path, blobs)

					else:
						print 'Skipping build %s; blobs already exist at %s' % (bld, save_path)

		else:
			print 'No blobs found on iFaith server'


if __name__ == '__main__':
	main(sys.argv[1:])
