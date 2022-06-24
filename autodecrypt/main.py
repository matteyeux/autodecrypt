#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main module for autodecrypt."""
import typer
from rich import traceback
from typing import Optional

from autodecrypt import decrypt_img
from autodecrypt import fw_utils
from autodecrypt import utils

__author__ = "matteyeux"


traceback.install()


def main(
    file: str = typer.Option(
        ...,
        "--filename",
        "-f",
        help="File",
    ),
    device: str = typer.Option(
        ...,
        "--device",
        "-d",
        help="Device",
    ),
    ios_version: str = typer.Option(
        None,
        "--ios_version",
        "-i",
        help="iOS version",
    ),
    build: str = typer.Option(
        None,
        "--build",
        "-b",
        help="Build ID of iOS version",
    ),
    ivkey: str = typer.Option(
        None,
        "--ivkey",
        "-k",
        help="IV and key to decrypt file",
    ),
    local: Optional[bool] = typer.Option(
        False,
        "--local",
        "-l",
        help="Use path to local file",
    ),
    download: Optional[bool] = typer.Option(
        False,
        "--download",
        "-D",
        help="Download file",
    ),
    beta: Optional[bool] = typer.Option(
        False,
        "--beta",
        "-B",
        help="Specify that it is a beta firmware",
        is_flag=True,
        show_default=False,
    ),
    pongo: Optional[bool] = typer.Option(
        False,
        "--pongo",
        "-P",
        help="Use PongoOS over USB for decryption",
        is_flag=True,
        show_default=False,
    ),
) -> int:
    img_file: str = None
    if build is None and ios_version is None:
        msg = typer.style(
            "Please specify iOS version or build ID",
            fg=typer.colors.WHITE,
            bg=typer.colors.RED,
        )
        typer.echo(msg)
        return -1

    json_data = fw_utils.get_json_data(device)

    if build is None:
        build = fw_utils.get_build_id(json_data, ios_version)

    if local is False:
        if beta is True:
            img_file = utils.download_beta_file(
                file, device, build, ios_version, json_data
            )
        else:
            img_file = utils.download_file(
                file, device, build, ios_version, json_data
            )

    if img_file is None:
        print("[e] could not grab file")
        return 1

    # if you only need to download file,
    # you can stop here
    if download is True:
        return 0

    magic, image_type = decrypt_img.get_image_type(img_file)

    if pongo is True:
        ivkey = utils.grab_key_from_pongo(img_file)

    if ivkey is None and pongo is False:
        ivkey = utils.get_firmware_keys(device, build, img_file, image_type)
    if ivkey is None:
        return

    iv, key = None, None

    if ivkey != "0":
        iv, key = utils.split_key(ivkey)
        print("[x] iv  : %s" % iv)
        print("[x] key : %s" % key)

    decrypt_img.decrypt_img(img_file, magic, iv, key)
    print("[x] done")
    return 0


app = typer.run(main)

# if __name__ == "__main__":
#    typer.run(main)
