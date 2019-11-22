#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import shutil
import sys
import zipfile
from remotezip import RemoteZip
from optparse import OptionParser

import decrypt_img
from scrapkeys import KeyGrabber
from ipsw_dl import IpswDownloader

__author__ = "matteyeux"

logging.basicConfig(filename="autodecrypt.log",
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

def grab_file(url, filename):
    """partialzip file from remote server"""
    with RemoteZip(url) as zip:
        filenames = zip.namelist()
        for fname in filenames:
            zinfo = zip.getinfo(fname)
            if filename in zinfo.filename and not ".plist" in zinfo.filename:
                filename = zinfo.filename.split("/")[-1]
                print("[i] downloading %s" % filename)
                extract_and_clean(zip, zinfo.filename, filename)
                return filename
        return filename

def extract_and_clean(zipper, zip_path, filename):
    """
    clean partialziped file and put it at 
    the root of the current dir
    """
    zipper.extract(zip_path)
    if "/" in zip_path :
        os.rename(zip_path, filename)
        shutil.rmtree(zip_path.split('/')[0])

image_types = [
    ["ogol", "logo", "applelogo"],
    ["0ghc", "chg0", "batterycharging0"],
    ["1ghc", "chg1", "batterycharging1"],
    ["Ftab", "batF", "Ftab"],
    ["Ftab", "batF", "batteryfull"],
    ["0tab", "bat0", "batterylow0"],
    ["1tab", "bat1", "batterylow1"],
    ["ertd", "dtre", "devicetree"],
    ["Cylg", "glyC", "glyphcharging"],
    ["Pylg", "glyP", "glyphplugin"],
    ["tobi", "ibot", "iboot"],
    ["blli", "illb", "llb"],
    ["ssbi", "ibss", "ibss"],
    ["cebi", "ibec", "ibec"],
    ["lnrk", "krnl", "kernelcache"],
    ["sepi", "sepi", "sepfirmware"]
]

def get_image_type_name(image):
    """get image name"""
    image = image.decode("utf-8")
    for i in range(0, len(image_types)):
        if image == image_types[i][0] or image == image_types[i][1]:
            img_type = image_types[i][2]
            return img_type
    return None


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",  required=True, dest="img_file", help="img file you want to decrypt")
    parser.add_argument("-d","--device", required=True, dest="device", help="device ID  (eg : iPhone8,1)")
    parser.add_argument("-i","--ios", dest="ios_version", help="iOS version for the said file")
    parser.add_argument("-b","--build", dest="build_id", help="build ID to set instead of iOS version")
    parser.add_argument("-l","--local", action='store_true', help="don't download firmware image")
    parser.add_argument("-k","--key", dest="ivkey", help="specify iv + key")
    parser.add_argument("--ip", dest='ip_addr', help="specify ip address of gidaes server")
    parser.add_argument("--beta", action='store_true', help="specify beta firmware")
    parser.add_argument("--download", action='store_true', help="download firmware image")

    return parser.parse_args()

def main():
    build = None
    codename = None
    ios_version = None
    ivkey = None
    parser = parse_arguments()
    logging.info('Launching "{}"'.format(sys.argv))

    if parser.ios_version is not None:
        ios_version = parser.ios_version

    if parser.build_id is not None:
        build = parser.build_id

    scrapkeys = KeyGrabber()

    if parser.beta is not True:
        # TODO : make the function return 2 values
        # build and iOS version
        if parser.ios_version is not None:
            build = scrapkeys.version_or_build(parser.device, ios_version, build)
        else:
            ios_version = scrapkeys.version_or_build(parser.device, ios_version, build)

    logging.info("codename : {}".format(codename))

    if parser.local is not True:
        ipsw = IpswDownloader()
        logging.info("grabbing IPSW file URL for {}/{}".format(parser.device, ios_version))
        ipsw_url = ipsw.parse_json(parser.device, ios_version, build, parser.beta)[0]

        logging.info("downloading {}...".format(parser.img_file))
        parser.img_file = grab_file(ipsw_url, parser.img_file)

        # Just download image file
        # won't decrypt
        if parser.download is True:
            return 0

    if  parser.ip_addr is not None:
        logging.info("grabing keys from gidaes server on {}".format(parser.ip_addr))
        kbag = decrypt_img.get_kbag(parser.img_file)
        ivkey = decrypt_img.get_gidaes_keys(parser.ip_addr, kbag)
        magic = "img4"

    if ivkey is None and parser.ip_addr is None:
        url = scrapkeys.getFirmwareKeysPage(parser.device, build)
        logging.info("url : {}".format(url))

        magic, image_type = decrypt_img.get_image_type(parser.img_file)
        image_name = get_image_type_name(image_type)

        if image_name is None:
            print("[e] image type not found")

        print("[i] image : %s" % image_name)
        print("[i] grabbing keys from %s" % url)
        ivkey = scrapkeys.parse_iphonewiki(url, image_name)

    iv = ivkey[:32]
    key = ivkey[-64:]
    print("[x] iv  : %s" % iv)
    print("[x] key : %s" % key)

    decrypt_img.decrypt_img(parser.img_file, parser.img_file + ".dec", magic, key, iv, openssl='openssl')
    print("[x] done")


if __name__ == '__main__':
    main()
