#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main module for autodecrypt."""
import argparse
import logging
import os
import sys
try:
    from autodecrypt import decrypt_img
    from autodecrypt import scrapkeys
    from autodecrypt import ipsw_utils
except ImportError:
    import decrypt_img
    import ipsw_utils
    import scrapkeys

__author__ = "matteyeux"

logging.basicConfig(filename="/tmp/autodecrypt.log",
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)


def parse_arguments():
    """Parse arguments from cmdline."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, dest="img_file",
                        help="img file you want to decrypt")
    parser.add_argument("-d", "--device", required=True, dest="device",
                        help="device ID  (eg : iPhone8,1)")
    parser.add_argument("-i", "--ios", dest="ios_version", help="iOS version for the said file")
    parser.add_argument("-b", "--build", dest="build_id",
                        help="build ID to set instead of iOS version")
    parser.add_argument("-l", "--local", action='store_true', help="don't download firmware image")
    parser.add_argument("-k", "--key", dest="ivkey", help="specify iv + key")
    parser.add_argument("--ip", dest='ip_addr', help="specify ip address of gidaes server")
    parser.add_argument("--download", action='store_true', help="download firmware image")

    return parser.parse_args()


def get_firmware_keys(device: str, build: str, img_file: str, image_type: str):
    """
    Get firmware keys using the key scrapper
    or by requesting of foreman instance.
    If one is set in env.
    """
    logging.info("grabbing keys")
    foreman_host = os.getenv('FOREMAN_HOST')
    image_name = ipsw_utils.get_image_type_name(image_type)

    if image_name is None:
        print("[e] image type not found")

    print("[i] image : %s" % image_name)
    print("[i] grabbing keys for {}/{}".format(device, build))
    if foreman_host is not None and foreman_host != "":
        print("[i] grabbing keys from %s" % foreman_host)
        foreman_json = scrapkeys.foreman_get_json(foreman_host, device, build)
        ivkey = scrapkeys.foreman_get_keys(foreman_json, img_file)
    else:
        ivkey = scrapkeys.getkeys(device, build, img_file)

    if ivkey is None:
        print("[e] unable to get keys for {}/{}".format(device, build))
        return None
    return ivkey


def main():
    """Main function."""
    build = None
    ios_version = None

    parser = parse_arguments()
    ivkey = parser.ivkey

    logging.info('Launching %s', sys.argv)
    json_data = ipsw_utils.get_json_data(parser.device)

    ios_version = parser.ios_version
    build = parser.build_id

    if build is None:
        # I assume you have at least specified
        # iOS version (eg : 10.2.1)
        build = ipsw_utils.get_build_id(json_data, ios_version)

    if parser.local is not True:
        logging.info("grabbing OTA file URL for %s/%s", parser.device, ios_version)
        fw_url = ipsw_utils.get_firmware_url(json_data, build)
        if fw_url is None:
            print("[w] could not get OTA url, trying with IPSW url")
            json_data = ipsw_utils.get_json_data(parser.device, "ipsw")
            build = ipsw_utils.get_build_id(json_data, ios_version, "ipsw")
            fw_url = ipsw_utils.get_firmware_url(json_data, build)
            if fw_url is None:
                print("[e] could not get IPSW url, exiting...")
                sys.exit(1)
        parser.img_file = ipsw_utils.grab_file(fw_url, parser.img_file)
        if parser.download is True:
            # Just download image file
            # won't decrypt
            return 0

    magic, image_type = decrypt_img.get_image_type(parser.img_file)

    if parser.ip_addr is not None:
        print("[i] grabbing keys from gidaes server on %s:12345", parser.ip_addr)
        kbag = decrypt_img.get_kbag(parser.img_file)
        print("kbag : {}".format(kbag))
        ivkey = decrypt_img.get_gidaes_keys(parser.ip_addr, kbag)
        magic = "img4"

    if ivkey is None and parser.ip_addr is None:
        ivkey = get_firmware_keys(parser.device, build, parser.img_file, image_type)

    init_vector = ivkey[:32]
    key = ivkey[-64:]
    print("[x] iv  : %s" % init_vector)
    print("[x] key : %s" % key)

    decrypt_img.decrypt_img(parser.img_file, parser.img_file + ".dec", magic, key, init_vector)
    print("[x] done")
    return 0


if __name__ == '__main__':
    main()
