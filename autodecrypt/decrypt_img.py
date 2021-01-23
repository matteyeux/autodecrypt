"""Module used for decrypting and extracting img4 file format"""
import logging
import os
import subprocess
import sys


def get_image_type(filename: str):
    """Check if it is IMG4 format."""
    if not os.path.isfile(filename):
        print("[e] %s : file not found" % filename)
        sys.exit(-1)
    with open(filename, "rb") as file:
        file.seek(7, 0)
        magic = file.read(4)
        if magic == b"IM4P":
            magic = "img4"
        else:
            return None
        file.seek(2, os.SEEK_CUR)
        img_type = file.read(4)
        return magic, img_type


def decrypt_img(infile: str, magic: str, key: str, init_vector: str):
    """Decrypt IMG4 image file."""
    image_type = get_image_type(infile)
    if image_type is None:
        print("[e] %s is not an IMG4 file" % infile)
        sys.exit(1)

    outfile = infile.replace("im4p", "bin")
    if magic == "img4":
        print("[i] decrypting %s to %s..." % (infile, outfile))
        fnull = open(os.devnull, "w")

        ivkey = init_vector + key
        logging.info("img4 -i %s %s %s", infile, outfile, ivkey)

        try:
            subprocess.Popen(
                ["img4", "-i", infile, outfile, ivkey], stdout=fnull
            )
        except FileNotFoundError:
            print("[e] can't decrypt file, is img4 tool in $PATH ?")
            sys.exit(1)
    else:
        print("{} is not supported".format(magic))
        return


def get_kbag(firmware_image: str) -> str:
    """Return kbag of img4 file."""
    out = subprocess.check_output(["img4", "-i", firmware_image, "-b"])
    kbag = out.split()[0].decode("UTF-8")
    return kbag
