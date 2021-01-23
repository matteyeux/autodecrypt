#!/usr/bin/env python
"""Module to scrapkeys and deal with foreman."""
import re

import requests
from pyquery import PyQuery


def get_fw_keys_page(device: str, build: str) -> str:
    """Return the URL of theiphonewiki to parse."""
    wiki = "https://www.theiphonewiki.com"
    data = {"search": build + " " + device}
    response = requests.get(wiki + "/w/index.php", params=data)
    html = response.text
    link = re.search(r"\/wiki\/.*_" + build + r"_\(" + device + r"\)", html)
    if link is not None:
        pagelink = wiki + link.group()
    else:
        pagelink = None
    return pagelink


def getkeys(device: str, build: str, img_file: str = None) -> str:
    """Return a json or str."""
    pagelink = get_fw_keys_page(device, build)
    if pagelink is None:
        return None

    oldname = None
    html = requests.get(pagelink).text
    query = PyQuery(html)

    for span in query.items("span.mw-headline"):
        name = span.text().lower()
        # on some pages like
        # https://www.theiphonewiki.com/wiki/Genoa_13G36_(iPhone8,1)
        # the name of file comes with a non-breaking
        # space in Latin1 (ISO 8859-1)
        # I can either replace or split.
        name = name.split("\xa0")[0]

        if name == "sep-firmware":
            name = "sepfirmware"

        # Name is the same for both files except
        # that the id has a "2" for the second file:
        # n71m : keypage-ibec-key
        # n71  : keypage-ibec2-key
        if oldname == name:
            name += "2"

        fname = span.parent().next("* > span.keypage-filename").text()
        code = "*>*>code#keypage-"
        ivkey = span.parent().siblings(code + name + "-iv").text()
        ivkey += span.parent().siblings(code + name + "-key").text()

        if fname == img_file and img_file is not None:
            return ivkey
        oldname = name
    return None


def foreman_get_json(foreman_host: str, device: str, build: str) -> dict:
    """Get json file from foreman host"""
    url = foreman_host + "/api/find/combo/" + device + "/" + build
    resp = requests.get(url=url).json()
    return resp


def foreman_get_keys(json_data: dict, img_file: str) -> str:
    """Return key from json data for a specify file"""
    try:
        images = json_data["images"]
    except KeyError:
        return None

    for key in images.keys():
        if img_file.split(".")[0] in key:
            return json_data["images"][key]
    return None
