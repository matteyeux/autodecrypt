"""Module used for decrypting and extracting img4 file format"""
import os
import sys
import subprocess
import pyimg4
from pyimg4 import Compression, Keybag


def decrypt_img(infile: str, magic: str, iv: str, key: str) -> int:
    """Decrypt IM4P file. This code is mostly copy/pasta from PyIMG4."""
    file = open(infile, 'rb').read()
    im4p = pyimg4.IM4P(file)

    if im4p.payload.encrypted is False:
        print("[i] payload is not encrypted")
        return 0

    if iv is None or key is None:
        print("[e] iv or key is None")
        return -1

    outfile = infile.replace("im4p", "bin")
    print(f"[i] decrypting {infile} to {outfile}...")

    im4p.payload.decrypt(Keybag(key=key, iv=iv))
    if im4p.payload.compression not in (Compression.NONE, Compression.UNKNOWN):
        print('[i] image4 payload data is compressed, decompressing...')
        im4p.payload.decompress()

    open(outfile, 'wb').write(im4p.payload.output().data)
    return 0


def get_image_type(filename: str):
    """Check if it is IM4P format."""
    if not os.path.isfile(filename):
        print("[e] %s : file not found" % filename)
        sys.exit(-1)
    with open(filename, "rb") as file:
        file.seek(7, 0)
        magic = file.read(4).decode()
        if "M4P" in magic:
            if magic != "IM4P":
                file.seek(-1, os.SEEK_CUR)
            magic = "img4"
        else:
            return None
        file.seek(2, os.SEEK_CUR)
        img_type = file.read(4)
        return magic, img_type


def get_kbag(firmware_image: str) -> str:
    """Return kbag of img4 file."""
    out = subprocess.check_output(["img4", "-i", firmware_image, "-b"])
    kbag = out.split()[0].decode("UTF-8")
    return kbag
