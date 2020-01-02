"""Module to deal with ipsw files."""
import os
import shutil
import requests
from remotezip import RemoteZip


def grab_file(url: str, filename: str) -> str:
    """Partialzip file from remote server."""
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
        shutil.rmtree(zip_path.split('/')[0])


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
    ["sepi", "sepi", "sepfirmware"]
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
    for i in range(0, len(json_data['firmwares'])):
        if json_data['firmwares'][i]['buildid'] == buildid:
            return json_data['firmwares'][i]['url']
    return None


def get_board_config(json_data: dict) -> str:
    """Return boardconfig of said device"""
    return json_data["boardconfig"]


def get_build_id(json_data: dict, ios_version: str, fw_type: str = "ota") -> str:
    """Return build ID of iOS version."""
    release = ""
    for i in range(0, len(json_data['firmwares'])):
        curent_vers = json_data['firmwares'][i]['version']
        if fw_type == "ota":
            release = json_data['firmwares'][i]['releasetype']

        if ios_version in curent_vers and release == "":
            return json_data['firmwares'][i]['buildid']
    return None


def get_ios_vers(json_data: dict, buildid) -> str:
    """"Return iOS version of build ID."""
    if json_data is None:
        return None
    for i in range(0, len(json_data['firmwares'])):
        if json_data['firmwares'][i]['buildid'] == buildid:
            return json_data['firmwares'][i]['version']
    return None


def get_build_list(json_data: dict) -> list:
    """Return a list of build IDs for a device"""
    builds = []
    for i in range(len(json_data['firmwares'])):
        builds.append(json_data['firmwares'][i]['buildid'])
    return builds
