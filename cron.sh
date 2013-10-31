#!/usr/bin/env bash

COMMAND="python savethemblobs.py"
OPTIONS="--skip-cydia --skip-ifaith"

pushd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" > /dev/null

	${COMMAND} ${OPTIONS} __ECID__ iPhone6,1 # My iPhone 5s
	${COMMAND} ${OPTIONS} __ECID__ iPhone5,2 # My iPhone 5
	${COMMAND} ${OPTIONS} __ECID__ iPhone3,1 # My iPhone 4
	${COMMAND} ${OPTIONS} __ECID__ iPhone5,2 # My old (pre-swap) iPhone 5 (probably destroyed by now)

popd > /dev/null
