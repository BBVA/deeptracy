#!/bin/bash

SCAN_DIR=/tmp/scan
APP_DIR=/opt/app

mkdir $SCAN_DIR
cp $APP_DIR/* $SCAN_DIR

cd $SCAN_DIR && npm install

retire -c -p --outputformat text --outputpath $APP_DIR/${OUTPUT_FILE} --jspath $SCAN_DIR