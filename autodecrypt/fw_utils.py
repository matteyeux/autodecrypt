"""Module to deal with ipsw files."""
import os
import shutil
import sys

import requests
from bs4 import BeautifulSoup
from remotezip import RemoteZip


def grab_file(url: str, filename: str) -> str:
    """Partialzip file from remote server."""
    if "developer.apple.com" in url:
        return None
    with RemoteZip(url) as zipfile:
        filenames = zipfile.namelist()
        for fname in filenames:
            zinfo = zipfile.getinfo(fname)
            if filename in zinfo.filename and ".plist" not in zinfo.filename:
                filename = zinfo.filename.split("/")[-1]
                print("[i] downloading %s" % filename)
                extract_and_clean(zipfile, zinfo.filename, filename)
                return filename
        return filename


def extract_and_clean(zipper: str, zip_path: str, filename: str):
    """
    Clean partialziped file and put it at
    the root of the current dir.
    """
    zipper.extract(zip_path)
    if "/" in zip_path:
        os.rename(zip_path, filename)
        shutil.rmtree(zip_path.split("/")[0])


IMAGE_TYPES = [
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
    ["sepi", "sepi", "sepfirmware"],
]


def get_image_type_name(image: str) -> str:
    """Get image name."""
    image = image.decode("utf-8")
    for i, _ in enumerate(IMAGE_TYPES):
        if image in (IMAGE_TYPES[i][0], IMAGE_TYPES[i][1]):
            img_type = str(IMAGE_TYPES[i][2])
            return img_type
    return None


def get_json_data(model: str, fw_type: str = "ota") -> dict:
    """Setup json data to parse."""
    url = "https://api.ipsw.me/v4/device/" + model
    if fw_type == "ota":
        url += "?type=ota"
    resp = requests.get(url=url)
    return resp.json()


def get_firmware_url(json_data: dict, buildid: str) -> str:
    """Return URL of IPSW file."""
    for firmware in json_data["firmwares"]:
        if firmware["buildid"] == buildid:
            return firmware["url"]
    return None


def get_board_config(json_data: dict) -> str:
    """Return boardconfig of said device"""
    return json_data["boardconfig"]


def get_build_id(json_data: dict, ios_vers: str, fw_type: str = "ota") -> str:
    """Return build ID of iOS version."""
    release = ""

    if ios_vers is None:
        print("[e] no iOS version specified")
        return sys.exit(1)

    for firmware in json_data["firmwares"]:
        curent_vers = firmware["version"]
        if fw_type == "ota":
            release = firmware["releasetype"]

        if ios_vers in curent_vers and release == "":
            return firmware["buildid"]


def get_ios_vers(json_data: dict, buildid: str) -> str:
    """"Return iOS version of build ID."""
    if json_data is None:
        return None
    for firmware in json_data["firmwares"]:
        if firmware["buildid"] == buildid:
            return firmware["version"]
    return None


def get_build_list(json_data: dict) -> list:
    """Return a list of build IDs for a device"""
    builds = []
    for firmware in json_data["firmwares"]:
        builds.append(firmware["buildid"])
    return builds


def get_beta_url(model, build, version):
    """Get iOS beta URL from theiphonewiki."""

    major = f"{version.split('.')[0]}.x"
    matches = [build, 'Restore']

    # URL should look like :
    # https://www.theiphonewiki.com/wiki/Beta_Firmware/iPhone/14.x
    wiki_url = (
        f"https://www.theiphonewiki.com/wiki/Beta_Firmware/iPhone/{major}"
    )
    html_text = requests.get(wiki_url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    found = False
    for link in soup.find_all('a'):
        href = link.get('href')
        if href is None:
            continue

        if model in href:
            found = True

        if found is True and all(x in href for x in matches):
            return href
    return None
