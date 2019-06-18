#!/usr/bin/env python3
import sys
import os
import zipfile
import shutil
from remotezip import RemoteZip
from optparse import OptionParser

sys.path.insert(0, ".")
import decrypt_img
from scrapkeys import KeyGrabber
from ipsw_dl import IpswDownloader

def grab_file(url, filename):
	filename = None
	with RemoteZip(url) as zip:
		filenames = zip.namelist()
		for fname in filenames:
			zinfo = zip.getinfo(fname)
			if filename in zinfo.filename and not ".plist" in zinfo.filename:
				filename = zinfo.filename.split("/")[-1]
				print("[i] downloading %s" % filename)
				extract_and_clean(zip, zinfo.filename, filename)
				return filename
		return filename

def extract_and_clean(zipper, zip_path, filename):
	zipper.extract(zip_path)
	if "/" in zip_path :
		os.rename(zip_path, filename)
		shutil.rmtree(zip_path.split('/')[0])

image_types = [
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

def get_image_type_name(image):
	image = image.decode("utf-8")
	for i in range(0, len(image_types)):
		if image == image_types[i][0] or image == image_types[i][1]:
			img_type = image_types[i][2]
			return img_type
	return None

parser = OptionParser()
def parse_arguments():
	parser.add_option("-f", "--file", dest="img_file", help="img file you want to decrypt")
	parser.add_option("-d","--device", dest="device", help="device ID  (eg : iPhone8,1)")
	parser.add_option("-i","--ios", dest="ios_version", help="iOS version for the said file")
	parser.add_option("-b","--build", dest="build_id", help="build ID to set instead of iOS version")
	parser.add_option("-c","--codename", dest="codename", help="codename of iOS version")
	parser.add_option("-l","--local", action='store_true', help="don't download firmware image")
	parser.add_option("--beta", action='store_true', help="specify beta version")
	(options, args) = parser.parse_args()
	return options, args

if __name__ == '__main__':
	argv = sys.argv
	argc = len(argv)
	set_ios_version = False
	device = None
	build = None
	codename = None

	options, args = parse_arguments()
	if argc < 7:
		parser.print_help()
		sys.exit(1)

	file = options.img_file
	device = options.device

	if options.ios_version is not None:
		ios_version = options.ios_version

	if options.build_id is not None:
		build = options.build_id

	scrapkeys = KeyGrabber()

	if options.beta is not True:
		if options.ios_version is not None:
			build = scrapkeys.version_or_build(device, ios_version, build)
		else:
			ios_version = scrapkeys.version_or_build(device, ios_version, build)

	if options.codename is None:
		codename = scrapkeys.get_codename(device, ios_version, build)

	# sometimes you already have the file
	if options.local is not True:
		ipsw = IpswDownloader()
		ipsw_url = ipsw.parse_json(device, ios_version, build, options.beta)[0]

		file = grab_file(ipsw_url, file)

	url = "https://www.theiphonewiki.com/wiki/" + codename + "_" + build + "_" + "(" + device + ")"

	magic, image_type = decrypt_img.get_image_type(file)
	image_name = get_image_type_name(image_type)

	if image_name is None:
		print("[e] image type not found")

	print("[i] image : %s" % image_name)
	print("[i] grabbing keys from %s" % url)
	image_keys = scrapkeys.parse_iphonewiki(url, image_name)

	iv = image_keys[:32]
	key = image_keys[-64:]
	print("[x] iv  : %s" % iv)
	print("[x] key : %s" % key)
	decrypt_img.decrypt_img(file, file + ".dec", magic, key, iv, openssl='openssl')
	print("[x] done")
