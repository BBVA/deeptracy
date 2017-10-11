#!/bin/bash

# Directories that need to be mapped in run
export SOURCE_CODE_DIR=/opt/app
export RESULTS_PATH=/tmp/results

# Temporal dir used to run the app to avoid the modification of original source
# code
export SCAN_DIR=/tmp/scan

mkdir $SCAN_DIR
cp -R $SOURCE_CODE_DIR/* $SCAN_DIR/

#
# Install project dependencies
#
cd $SCAN_DIR && npm install

#
# Launch app
#
retire -c -p --outputformat json --outputpath ${RESULTS_PATH}/${OUTPUT_FILE}

exit 0
