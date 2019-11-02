# autodecrypt
Simple tool to decrypt iOS firmware images

Going to the iPhone wiki and copying and pasting firmware keys to your terminal is boring.

autodecrypt will grab keys for you and decrypt the firmware image you want.

#### Usage
```
usage: autodecrypt.py [-h] -f IMG_FILE -d DEVICE [-i IOS_VERSION]
                      [-b BUILD_ID] [-c CODENAME] [-l] [--beta] [--download]

optional arguments:
  -h, --help            show this help message and exit
  -f IMG_FILE, --file IMG_FILE
                        img file you want to decrypt
  -d DEVICE, --device DEVICE
                        device ID (eg : iPhone8,1)
  -i IOS_VERSION, --ios IOS_VERSION
                        iOS version for the said file
  -b BUILD_ID, --build BUILD_ID
                        build ID to set instead of iOS version
  -c CODENAME, --codename CODENAME
                        codename of iOS version
  -l, --local           don't download firmware image
  --beta                specify beta firmware
  --download            download firmware image
```

By default it automatically downloads image file from apple.com using ipsw.me API.

#### Dependencies
- Python3
- python3-pip
- [img4](https://github.com/xerub/img4lib)

To install python3 modules, run : `pip3 install -r requirements.txt`
#### Examples

Decrypting SEP from iOS 10.3.3 
```
./autodecrypt.py -f sep-firmware.n51.RELEASE.im4p -i 10.3.3 -d iPhone6,1
[i] downloading sep-firmware.n51.RELEASE.im4p
[i] image : sepfirmware
[i] grabbing keys from https://www.theiphonewiki.com/wiki/Greensburg_14G60_(iPhone6,1)
[x] iv  : b370c7d85476823ef83d3991cb8078b9
[x] key : 54c3a8ffe7f2437ea23c4c7ea72a66544644b869849e4635dfbf74824a61a733
[i] decrypting sep-firmware.n51.RELEASE.im4p to sep-firmware.n51.RELEASE.im4p.dec...
[x] done
```

Decrypting iBoot from iOS 12.2 beta 2. To decrypt beta firmware images, use `-b`, `-i` and `-beta` flags the tool will parse OTA json.
```
./autodecrypt.py -f iBoot.n56.RELEASE.im4p -b 16E5191d -i 12.2 -d iPhone7,1 --beta
[i] downloading iBoot.n56.RELEASE.im4p
[i] image : iboot
[i] grabbing keys from https://www.theiphonewiki.com/wiki/PeaceESeed_16E5191d_(iPhone7,1)
[x] iv  : c7f8e518dbc56bac9f330b301e3b1ccf
[x] key : 9cd1e1b5f0f16ebcf30f84900dc5ba3d70a84cd6f162bba6b51a09b0cd844b12
[i] decrypting iBoot.n56.RELEASE.im4p to iBoot.n56.RELEASE.im4p.dec...
[x] done
```

#### Log

For debugging purposes you can check `autodecrypt.log` :
```
11/02/2019 21:39:41 Launching "['autodecrypt/autodecrypt.py', '-d', 'iPhone9,3', '-f', 'iBoot', '-i', '12.3.1']"
11/02/2019 21:39:41 requesting IPSW's API for iPhone9,3
11/02/2019 21:39:41 done, now looking for version or build
11/02/2019 21:39:41 grabbing firmware codename for 16F203
11/02/2019 21:39:42 codename : PeaceF
11/02/2019 21:39:42 grabbing IPSW file URL for iPhone9,3/12.3.1
11/02/2019 21:39:42 downloading iBoot...
11/02/2019 21:39:43 img4 -i iBoot.d10.RELEASE.im4p iBoot.d10.RELEASE.im4p.dec 978fd4680cd4b624b0dfea22a417f51f0ee2b871defed42277fe18885053b1eb5c7ffe82f38ab8cf7772c69a0db5d386
```

#### TODO
- [ ] test on Apple Watch firmwares

### Credits
- kennytm for img3 stuff
- xerub for [img4](https://github.com/xerub/img4lib)
