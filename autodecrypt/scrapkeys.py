#!/usr/bin/env python
"""Module to scrapkeys and deal with foreman."""
import re
import requests
from pyquery import PyQuery


def getfirmwarekeyspage(device: str, buildnum: str) -> str:
    """Return the URL of theiphonewiki to parse."""
    wiki = "https://www.theiphonewiki.com"
    response = requests.get(wiki+"/w/index.php", params={'search': buildnum+" "+device})
    html = response.text
    link = re.search(r"\/wiki\/.*_" + buildnum + r"_\(" + device + r"\)", html)
    if link is not None:
        pagelink = wiki+link.group()
    else:
        pagelink = None
    return pagelink


def getkeys(device: str, buildnum: str, img_file: str = None) -> str:
    """Return a json or str."""
    pagelink = getfirmwarekeyspage(device, buildnum)
    if pagelink is None:
        return None

    html = requests.get(pagelink).text
    query = PyQuery(html)

    for span in query.items('span.mw-headline'):
        name = span.text().lower()

        if name == "sep-firmware":
            name = "sepfirmware"

        fname = span.parent().next("* > span.keypage-filename").text()
        ivkey = span.parent().siblings("*>*>code#keypage-" + name + "-iv").text()
        ivkey += span.parent().siblings("*>*>code#keypage-" + name + "-key").text()

        if fname == img_file and img_file is not None:
            return ivkey
    return None


def foreman_get_json(foreman_host: str, device: str, build: str) -> dict:
    """Get json file from foreman host"""
    url = foreman_host + "/api/find/combo/" + device + "/" + build
    resp = requests.get(url=url).json()
    return resp


def foreman_get_keys(json_data: dict, img_file: str) -> str:
    """Return key from json data for a specify file"""
    try:
        images = json_data['images']
    except KeyError:
        return None

    for key in images.keys():
        if img_file.split('.')[0] in key:
            return json_data['images'][key]
    return None
