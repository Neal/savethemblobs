# savethemblobs

A simple script to grab all SHSH blobs from Apple that it's currently signing to save them locally and on Cydia server.

And now also grabs blobs already cached on Cydia and iFaith servers to save them locally.

Will automatically work with future firmwares!

## Usage

	savethemblobs.py [-h] [--save-dir SAVE_DIR] [--overwrite]
	                 [--overwrite-apple] [--overwrite-cydia]
	                 [--overwrite-ifaith] [--no-submit-cydia]
	                 [--skip-cydia] [--skip-ifaith]
	                 ecid device

	positional arguments:
	  ecid                 device ECID in int or hex (prefix hex with 0x)
	  device               device identifier/boardconfig (eg. iPhone3,1/n90ap)

	optional arguments:
	  -h, --help           show this help message and exit
	  --save-dir SAVE_DIR  local dir for saving blobs (default: ~/.shsh)
	  --overwrite          overwrite any existing blobs
	  --overwrite-apple    overwrite any existing blobs (only from Apple)
	  --overwrite-cydia    overwrite any existing blobs (only from Cydia)
	  --overwrite-ifaith   overwrite any existing blobs (only from iFaith)
	  --no-submit-cydia    don't submit blobs to Cydia server
	  --skip-cydia         skip fetching blobs from Cydia server
	  --skip-ifaith        skip fetching blobs from iFaith server


## License

savethemblobs is available under the MIT license. See the LICENSE file for more info.
