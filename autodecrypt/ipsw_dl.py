#!/usr/bin/python3
import sys
import os
import shutil
import requests
import json
from urllib.request import urlopen
import zipfile
from clint.textui import progress

# download file
def dl(url, filename, sizeofile=0):
	# idk the size of the file
	if sizeofile == 0:
		dl_file = urlopen(url)
		with open(filename,'wb') as output:
			output.write(dl_file.read())
	else :
		dl_file = requests.get(url, stream=True)
		with open(filename,'wb') as output:
			for chunk in progress.bar(dl_file.iter_content(chunk_size=1024), expected_size=(sizeofile/1024) + 1):
				if chunk:
					output.write(chunk)
					output.flush()

# extract IPSW filename from URL
def get_filename(url):
	for i in range(len(url)):
		if url[i] == '/':
			position = i + 1
	return url[position:]

class IpswDownloader:
	# download and parse json file
	def parse_json(self, model, version, build=None, isbeta=False):
		json_file = model + ".json"
		i = 0
		size = 0
		# if it's a beta firmware use OTA json from api.ipsw.me
		if isbeta is True:
			dl("https://api.ipsw.me/v4/ota/" + version, json_file)
			data = json.load(open(json_file))

			with open(json_file):
				while True :
					i += 1
					buildid = data[i]["buildid"]
					device = data[i]["identifier"]
					if buildid == build and model == device:
						url = data[i]["url"]
						break
		else :
			dl("https://api.ipsw.me/v4/device/" + model, json_file)
			data = json.load(open(json_file))

			ios_version = data["firmwares"][i]["version"]
			with open(json_file):
				while ios_version != version :
					i += 1
					ios_version = data["firmwares"][i]["version"]
				buildid = data["firmwares"][i]["buildid"]
				url = data["firmwares"][i]["url"]
				size = data["firmwares"][i]["filesize"]


		ipswfile = get_filename(url)
		os.remove(json_file)
		return url, ipswfile, size

	def recursive_rm(folder="ipsw"):
		for files in os.listdir(folder):
			file_path = os.path.join(folder, files)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path): shutil.rmtree(file_path)
			except Exception as error:
				print(error)

