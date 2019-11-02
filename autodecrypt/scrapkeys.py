#!/usr/bin/python3
import logging
import sys
import os
import json
from urllib.request import urlopen
import mechanicalsoup

class KeyGrabber:
    def parse_iphonewiki(self, url2parse, img_type):
        """parse the iphone wiki to get the correct key"""
        br = mechanicalsoup.StatefulBrowser()
        html = br.open(url2parse)

        keypage = list()
        keypage =   ["rootfs-key", "updateramdisk-iv", "updateramdisk-key",
                    "restoreramdisk-iv", "restoreramdisk-key", "applelogo-iv",
                    "applelogo-key", "batterycharging0-iv", "batterycharging0-key",
                    "batterycharging1-iv", "batterycharging1-key", "batteryfull-iv",
                    "batteryfull-key", "batterylow0-iv", "batterylow0-key",
                    "batterylow1-iv", "batterylow1-key", "devicetree-iv",
                    "devicetree-key", "glyphcharging-iv", "glyphcharging-key",
                    "glyphplugin-iv", "glyphplugin-key",
                    "ibec-iv", "ibec-key", "iboot-iv", "iboot-key",
                    "ibss-iv", "ibss-key", "kernelcache-iv",
                    "kernelcache-key", "llb-iv", "llb-key",
                    "recoverymode-iv", "recoverymode-key",
                    "sepfirmware-iv", "sepfirmware-key"
                ]
        j = 0
        key = ""
        for i in range(0, len(keypage)):
            for hit in br.get_current_page().find_all(attrs={'id': "keypage-" + keypage[i]}):
                if img_type == None:
                    bl = keypage[i]
                    print(bl + ":\n\t %s" % hit.text)
                elif img_type != None and img_type == keypage[i].split('-')[0]:
                    j += 1
                    key += hit.text
                    if j == 2:
                        return key

    def version_or_build(self, device, version, build):
        """
        Used to 'convert' version -> build ID and vice versa
        I just parse firmwares.json on api.ipsw.me
        """
        get_buildid = False
        get_version = False

        logging.info("requesting IPSW's API for {}".format(device))

        try:
            json_file = urlopen("https://api.ipsw.me/v4/device/" + device)
        except:
            print("[e] failed to retrieve json file for {}".format(device))
            sys.exit(1)

        with open(device, 'wb') as output:
            output.write(json_file.read())

        logging.info("done, now looking for version or build")
        data = json.load(open(device))

        if build is None:
            get_buildid = True
        elif version is None:
            get_version = True
        i = 0

        with open(device):
            try :
                while True:
                    if get_buildid is True:
                        result = data["firmwares"][i]["buildid"]
                        ios_version = data["firmwares"][i]["version"]
                        if ios_version == version:
                            break

                    elif get_version is True:
                        buildid = data["firmwares"][i]["buildid"]
                        result= data["firmwares"][i]["version"]
                        if build == buildid:
                            break
                    i += 1
            except:
                print("[e] version not found")
                os.remove(device)
                sys.exit(-1)

        os.remove(device)
        return result

    # we need to get the codename of the firmware to access the URL
    def get_codename(self, device, version, build):
        """
        get the codename of the firmware to access the wiki URL
        """
        version = version.split('.')[0] + ".x"
        url = "https://www.theiphonewiki.com/wiki/Firmware_Keys/" + version

        br = mechanicalsoup.StatefulBrowser()
        html = br.open(url) #.read()

        i = 0
        checker = False
        data = br.get_current_page().find_all('a')
        device = "(%s)" % device

        for hit in data:
            # some beta may have the same codename, first in first out
            if checker is False:
                try:
                    if data[i].get('href').split('_')[1] == build and data[i].get('href').split('_')[2] == device:
                        checker = True
                        codename = data[i].get('href').split('/')[2].split('_')[0]
                        return codename
                except:
                    pass
            i += 1
