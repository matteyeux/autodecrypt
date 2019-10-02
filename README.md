# autodecrypt
Simple tool to decrypt iOS firmware images

Going to the iPhone wiki and copying and pasting firmware keys to your terminal is boring.

autodecrypt will grab keys for you and decrypt the firmware image you want.

#### Usage
```
usage : ./autodecrypt.py -f <img file> -i [iOS version] -d [device]
options : 
 -f [IMG file]		 set img file you want to decrypt
 -i |iOS version]	 iOS version for the said file
 -b [build version]	 build ID for the said file (optional)
 -d [device]		 set device ID (eg : iPhone8,1)
 -l 			 local mode, it does not download firmware image
 -beta			 specify beta version
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
./autodecrypt.py -f iBoot.n56.RELEASE.im4p -b 16E5191d -i 12.2 -d iPhone7,1 -beta
[i] downloading iBoot.n56.RELEASE.im4p
[i] image : iboot
[i] grabbing keys from https://www.theiphonewiki.com/wiki/PeaceESeed_16E5191d_(iPhone7,1)
[x] iv  : c7f8e518dbc56bac9f330b301e3b1ccf
[x] key : 9cd1e1b5f0f16ebcf30f84900dc5ba3d70a84cd6f162bba6b51a09b0cd844b12
[i] decrypting iBoot.n56.RELEASE.im4p to iBoot.n56.RELEASE.im4p.dec...
[x] done
```

#### TODO
- [ ] test on Apple Watch firmwares
- [ ] catch all errors

### Credits
- kennytm for img3 stuff
- xerub for [img4](https://github.com/xerub/img4lib)
