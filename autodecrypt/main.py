#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main module for autodecrypt."""
import argparse

from autodecrypt import decrypt_img
from autodecrypt import fw_utils
from autodecrypt import utils


__author__ = "matteyeux"


def parse_arguments():
    """Parse arguments from cmdline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        dest="img_file",
        help="img file you want to decrypt",
    )
    parser.add_argument(
        "-d",
        "--device",
        required=True,
        dest="device",
        help="device ID  (eg : iPhone8,1)",
    )
    parser.add_argument(
        "-i", "--ios", dest="ios_version", help="iOS version for the said file"
    )
    parser.add_argument(
        "-b",
        "--build",
        dest="build",
        help="build ID to set instead of iOS version",
    )
    parser.add_argument(
        "-p",
        "--pongo",
        action="store_true",
        help="use PongoOS over USB for decryption",
    )
    parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        help="don't download firmware image",
    )
    parser.add_argument("-k", "--key", dest="ivkey", help="specify iv + key")
    parser.add_argument(
        "--download", action="store_true", help="download firmware image"
    )

    parser.add_argument(
        "--beta", action="store_true", help="specify beta firmware"
    )

    return parser.parse_args()


def main():
    """Main function."""
    parser = parse_arguments()
    ivkey = parser.ivkey
    build = parser.build

    json_data = fw_utils.get_json_data(parser.device)

    if build is None:
        build = fw_utils.get_build_id(json_data, parser.ios_version)

    if parser.local is False:
        if parser.beta is True:
            img_file = utils.download_beta_file(parser, json_data)
        else:
            img_file = utils.download_file(parser, json_data)

    if img_file is None:
        print("[e] could not grab file")
        return 1

    # if you only need to download file,
    # you can stop here
    if parser.download is True:
        return 0

    magic, image_type = decrypt_img.get_image_type(img_file)

    if parser.pongo is True:
        ivkey = utils.grab_key_from_pongo(img_file)

    if ivkey is None and parser.pongo is False:
        ivkey = utils.get_firmware_keys(
            parser.device, build, img_file, image_type
        )
    if ivkey is None:
        return

    iv, key = utils.split_key(ivkey)
    print("[x] iv  : %s" % iv)
    print("[x] key : %s" % key)

    decrypt_img.decrypt_img(img_file, magic, key, iv)
    print("[x] done")
    return 0


if __name__ == "__main__":
    main()
