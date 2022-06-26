#!/bin/bash

set -e

echo "=== print help ==="
autodecrypt --help

echo "=== normal behavior ==="
autodecrypt -f iBSS.iphone6.RELEASE.im4p -i 10.3.3 -d iPhone6,2

echo "=== specify key ==="
autodecrypt -d iPhone11,8 -i 13.4 -f sep-firmware.n104.RELEASE.im4p -k 46d48ecd42ae0b76a698eacf8446f8226688e0f54a1263ab31c045d5a89ffc92f880965c4ca29f93bd395f35d80033e6

echo "=== beta firmware ==="
autodecrypt -d iPhone9,3 -b 18D5043d -f iBoot.d10.RELEASE.im4p -i 14.4 --beta

echo "=== beta firmware iPad ==="
autodecrypt -d iPad13,1 -b 19A5325f -i 15.0 -f iBoot.j307.RELEASE.im4p --beta
