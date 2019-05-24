#!/bin/bash

pip3 install -r requirements.txt

sudo install -v autodecrypt/*.py /usr/local/bin/

sudo rm -f /usr/local/bin/autodecrypt
sudo ln -s /usr/local/bin/autodecrypt.py /usr/local/bin/autodecrypt
