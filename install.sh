#!/bin/bash

TOOL=autodecrypt

pip3 install -r requirements.txt
sudo install -v $TOOL *.py /usr/local/bin/
