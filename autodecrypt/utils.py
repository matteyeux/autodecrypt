import argparse
import logging
import os
from typing import Tuple

import decrypt_img
import fw_utils
import pongo
import scrapkeys


logging.basicConfig(
    filename="/tmp/autodecrypt.log",
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)


def split_key(ivkey: str) -> Tuple[str, str]:
    """Split IV and key."""
    iv = ivkey[:32]
    key = ivkey[-64:]
    return iv, key


def get_firmware_keys(device: str, build: str, img_file: str, image_type: str):
    """
    Get firmware keys using the key scrapper
    or by requesting of foreman instance.
    If one is set in env.
    """
    logging.info("grabbing keys")
    foreman_host = os.getenv("FOREMAN_HOST")
    image_name = fw_utils.get_image_type_name(image_type)

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
        board=img_file.split("iBSS.")[1].split(".RELEASE")[0]
        print("[e] unable to get keys for {}/{} using board {}".format(device, build,board))
        return None
    return ivkey


def grab_key_from_pongo(img_file: str):
    """Send command and grab PongoOS output."""
    print("[i] grabbing keys from PongoOS device")
    kbag = decrypt_img.get_kbag(img_file)
    print("[i] kbag : {}".format(kbag))
    pongo.pongo_send_command(f"aes cbc dec 256 gid0 {kbag}")
    ivkey = pongo.pongo_get_key()
    return ivkey


def get_ipsw_url(device, ios_version, build):
    """Get URL of IPSW by specifying device and iOS version."""
    json_data = fw_utils.get_json_data(device, "ipsw")

    if build is None:
        build = fw_utils.get_build_id(json_data, ios_version, "ipsw")

    fw_url = fw_utils.get_firmware_url(json_data, build)

    if fw_url is None:
        print("[w] could not get IPSW url, exiting...")
    return fw_url

def get_board_name(parser: argparse.Namespace, json_data: dict) -> str:
    fw_url = get_fw_ipsw_url(parser, json_data)
    board_names = fw_utils.collect_all_board_names(fw_url, parser.img_file)

    return board_names

def board_filter(parser: argparse.Namespace, json_data: dict, build: str) -> str:
    "Checking for multiple boards"
    board_names = get_board_name(parser, json_data)

    if len(board_names) > 1:
        board_names_short=', '.join([str(x.split("{}.".format(parser.img_file))[1].split(".RELEASE")[0]) for x in board_names])
        print("Found multiple boards: {}".format(board_names_short))

    image_name = parser.img_file

    if image_name is None:
        print("[e] image type not found")

    for board in board_names:
        ivkey_tmp = scrapkeys.getkeys(parser.device, build, board)

        if ivkey_tmp is None:
            board_tmp_name=board.split("{}.".format(parser.img_file))[1].split(".RELEASE")[0]
            print("Eliminating board {} as it's not valid for device".format(board_tmp_name))
            board_names.remove(board)

    return board_names

def get_fw_ipsw_url(parser: argparse.Namespace, json_data: dict) -> str:
    """Download file from IPSW or OTA."""
    fw_url = fw_utils.get_firmware_url(json_data, parser.build)
    if fw_url is None:
        print("[w] could not get OTA url, trying with IPSW url")
        fw_url = get_ipsw_url(parser.device, parser.ios_version, parser.build)
    return fw_url


def download_file(parser: argparse.Namespace, json_data: dict, board: str) -> str:
    fw_url = get_fw_ipsw_url(parser,json_data)

    if fw_url is None:
        return None

    img_file = fw_utils.grab_file(fw_url, parser.img_file, board)
    return img_file


def download_beta_file(parser: argparse.Namespace, json_data: dict) -> str:
    """Download file from beta firmware."""
    if parser.ios_version is None:
        print("[i] please specify iOS version")
        return None

    fw_url = fw_utils.get_beta_url(
        parser.device, parser.build, parser.ios_version
    )
    if fw_url is None:
        print("[e] could not get Beta firmware URL")
        return None
    img_file = fw_utils.grab_file(fw_url, parser.img_file)
    return img_file
