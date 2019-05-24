#!/usr/bin/python3
import sys
import os
import zipfile
import shutil
from remotezip import RemoteZip

sys.path.insert(0, ".")
import decrypt_img
from scrapkeys import KeyGrabber
from ipsw_dl import IpswDownloader

def grab_file(url, filename):
	with RemoteZip(url) as zip:
		filenames = zip.namelist()
		for fname in filenames:
			zinfo = zip.getinfo(fname)
			if filename in zinfo.filename and not ".plist" in zinfo.filename:
				filename = zinfo.filename.split("/")[-1]
				print("[i] downloading %s" % filename)
				extract_and_clean(zip, zinfo.filename, filename)
				return filename

def extract_and_clean(zipper, zip_path, filename):
	zipper.extract(zip_path)
	if "/" in zip_path :
		os.rename(zip_path, filename)
		shutil.rmtree(zip_path.split('/')[0])

# boring part of the code.
# TODO : find a better way
def get_image_type_name(image):
	image = image.decode("utf-8")
	if image == "ogol" or image == "logo":
		img_type = "applelogo"
	elif image == "0ghc" or image == "chg0":
		img_type = "batterycharging0"
	elif image == "1ghc" or image ==  "chg1":
		img_type = "batterycharging1"
	elif image == "Ftab" or image == "batF":
		img_type = "batteryfull"
	elif image == "0tab" or image == "bat0":
		img_type = "batterylow0"
	elif image == "1tab" or image == "bat1":
		img_type = "batterylow1"
	elif image == "ertd" or image == "dtre":
		img_type = "devicetree"
	elif image == "Cylg" or image == "glyC":
		img_type = "glyphcharging"
	elif image == "Pylg" or image == "glyP":
		img_type = "glyphplugin"
	elif image == "tobi" or image == "ibot":
		img_type = "iboot"
	elif image == "blli" or image == "illb":
		img_type = "llb"
	elif image == "ssbi" or image == "ibss":
		img_type = "ibss"
	elif image == "cebi" or image == "ibec":
		img_type = "ibec"
	elif image == "lnrk" or image == "krnl" :
		img_type = "kernelcache"
	elif image == "sepi" :
		img_type = "sepfirmware"
	else :
		print("image type not supported : %s" % image)
		img_type = None
	return img_type

def usage(tool):
	if '/' in tool :
		name = tool.split('/')
		name = name[len(name) - 1]

	print("usage : %s -f <img file> -i [iOS version] -d [device]" % name)
	print("options : ")
	print(" -f [IMG file]\t\t set img file you want to decrypt")
	print(" -i |iOS version]\t iOS version for the said file")
	print(" -b [build version]\t build ID for the said file (optional)")
	print(" -d [device]\t\t set device ID (eg : iPhone8,1)")
	print(" -l \t\t\t local mode, it does not download firmware image")
	print(" -beta\t\t\t specify beta version")

if __name__ == '__main__':
	argv = sys.argv
	argc = len(argv)
	set_ios_version = False
	ios_version = None
	device = None
	build = None
	codename = None
	local = False
	beta = False

	if argc < 7:
		usage(argv[0])
		sys.exit(1)

	for i in range(0, argc):
		if argv[i] == "-f" :
			file = argv[i + 1]
		elif argv[i] == "-i":
			ios_version = argv[i + 1]
			set_ios_version = True
		elif argv[i] == "-b":
			build = argv[i + 1]
		elif argv[i] == "-d":
			device = argv[i + 1]
		elif argv[i] == "-c":
			codename = argv[i + 1]
		elif argv[i] == "-l":
			local = True
		elif argv[i] == "-beta":
			beta = True
		elif argv[i] == "-h":
			usage(argv[0])

	scrapkeys = KeyGrabber()

	if beta is not True:
		if set_ios_version is True:
			build = scrapkeys.version_or_build(device, ios_version, build)
		else:
			ios_version = scrapkeys.version_or_build(device, ios_version, build)

	if codename is None:
		codename = scrapkeys.get_codename(device, ios_version, build)

	# sometimes you already have the file
	if local is not True:
		ipsw = IpswDownloader()
		ipsw_url = ipsw.parse_json(device, ios_version, build, beta)[0]

		file = grab_file(ipsw_url, file)

	url = "https://www.theiphonewiki.com/wiki/" + codename + "_" + build + "_" + "(" + device + ")"

	magic, image_type = decrypt_img.get_image_type(file)
	image_name = get_image_type_name(image_type)

	print("[i] image : %s" % image_name)
	print("[i] grabbing keys from %s" % url)
	image_keys = scrapkeys.parse_iphonewiki(url, image_name)

	iv = image_keys[:32]
	key = image_keys[-64:]
	print("[x] iv  : %s" % iv)
	print("[x] key : %s" % key)
	decrypt_img.decrypt_img(file, file + ".dec", magic, key, iv, openssl='openssl')
	print("[x] done")
