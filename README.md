# autodecrypt
[![PyPI version](https://badge.fury.io/py/autodecrypt.svg)](https://badge.fury.io/py/autodecrypt)

Simple tool to decrypt iOS firmware images.

Going to the iPhone wiki and copying and pasting firmware keys to your terminal is boring.

autodecrypt will grab keys for you and decrypt the firmware image you want.

## Usage
```
usage: autodecrypt [-h] -f IMG_FILE -d DEVICE [-i IOS_VERSION] [-b BUILD] [-p] [-l] [-k IVKEY] [--download] [--beta]

optional arguments:
  -h, --help            show this help message and exit
  -f IMG_FILE, --file IMG_FILE
                        img file you want to decrypt
  -d DEVICE, --device DEVICE
                        device ID (eg : iPhone8,1)
  -i IOS_VERSION, --ios IOS_VERSION
                        iOS version for the said file
  -b BUILD, --build BUILD
                        build ID to set instead of iOS version
  -p, --pongo           use PongoOS over USB for decryption
  -l, --local           don't download firmware image
  -k IVKEY, --key IVKEY
                        specify iv + key
  --download            download firmware image
  --beta                specify beta firmware
```

## Dependencies
- [img4](https://github.com/xerub/img4lib)

To run autodecrypt, use poetry with a virtualenv:
- `virtualenv -p python3 env`
- `pip3 install poetry`
- `poetry install`


## Installation
`pip3 install autodecrypt`


## Examples

#### Download and decrypt iBSS using keys from theiphonewiki
```
» autodecrypt -f iBSS -i 10.3.3 -d iPhone6,2
[i] downloading iBSS.iphone6.RELEASE.im4p
[i] image : ibss
[i] grabbing keys for iPhone6,2/14G60
[x] iv  : f2aa35f6e27c409fd57e9b711f416cfe
[x] key : 599d9b18bc51d93f2385fa4e83539a2eec955fce5f4ae960b252583fcbebfe75
[i] decrypting iBSS.iphone6.RELEASE.im4p to iBSS.iphone6.RELEASE.bin...
[x] done
```

#### Download and decrypt SEP firmware by specifying keys
```
» autodecrypt -f sep-firmware -b 17C5053a -d iPhone11,8 -k 9f974f1788e615700fec73006cc2e6b533b0c6c2b8cf653bdbd347bc1897bdd66b11815f036e94c951250c4dda916c00
[i] downloading sep-firmware.n841.RELEASE.im4p
[x] iv  : 9f974f1788e615700fec73006cc2e6b5
[x] key : 33b0c6c2b8cf653bdbd347bc1897bdd66b11815f036e94c951250c4dda916c00
[i] decrypting sep-firmware.n841.RELEASE.im4p to sep-firmware.n841.RELEASE.bin...
[x] done
```

#### Use [foreman](https://github.com/GuardianFirewall/foreman) instance to grab firmware keys
```
» export FOREMAN_HOST="https://foreman-public.sudosecuritygroup.com"
» autodecrypt -f LLB -i 13.2.3 -d iPod9,1
[i] downloading LLB.n112.RELEASE.im4p
[i] image : llb
[i] grabbing keys for iPod9,1/17B111
[i] grabbing keys from https://foreman-public.sudosecuritygroup.com
[x] iv  : 85784a219eb29bcb1cc862de00a590e7
[x] key : f539c51a7f3403d90c9bdc62490f6b5dab4318f4633269ce3fbbe855b33a4bc7
[i] decrypting LLB.n112.RELEASE.im4p to LLB.n112.RELEASE.bin...
[x] done
```

#### Decrypt keys with PongoOS
> I you wanna use this on Linux, you may have some USB permissions. I recommend copying the file `66-pongos.rules` available on this repository to `/etc/udev/rules.d/`.

```
» autodecrypt -f iBoot -d iPhone8,1 -i 14.1 -p
[i] downloading iBoot.n71.RELEASE.im4p
[i] grabbing keys from PongoOS device
[i] kbag : 03C9E01CA99FE6475566C791777169C0625B04B7BD4E593DE0F61ABF4E8DB1A987D9D6155C5A1F41D9113694658AC61C
[x] iv  : 245a9b52e53a704fe73d7b58734b00ae
[x] key : d3aa3c8cc20fa9d61e466f46aee374a92a125abb5b3f57264025c8c72127e321
[i] decrypting iBoot.n71.RELEASE.im4p to iBoot.n71.RELEASE.bin...
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
11/02/2019 21:39:43 img4 -i iBoot.d10.RELEASE.im4p iBoot.d10.RELEASE.bin 978fd4680cd4b624b0dfea22a417f51f0ee2b871defed42277fe18885053b1eb5c7ffe82f38ab8cf7772c69a0db5d386
```


### Credits
- checkra1n team for AES patches, kbag.m and [PongoOS](https://github.com/checkra1n/pongoos)
- kennytm for img3 stuff (removed for the moment)
- xerub for [img4](https://github.com/xerub/img4lib)
- tihmstar for wiki parsing ([my method](https://github.com/matteyeux/ios-tools/blob/master/scrapkeys.py) was pretty bad)
