#!/usr/bin/python
# code from https://github.com/kennytm/Miscellaneous/blob/master/ipsw_decrypt.py
# not licensed under MIT as I don't know the initial license
import os
import sys
from struct import Struct
import subprocess

tag_unpack = Struct('<4s2I').unpack
kbag_unpack = Struct('<2I16s').unpack

def get_image_type(filename):
	if not os.path.isfile(filename):
		print("[e] %s : file not found" % filename)
		sys.exit(-1)
	with open(filename, 'rb') as file:
		# set the pointer to 
		# the beginning of the file
		file.seek(0, 0)
		magic = file.read(4)
		if magic == b'3gmI':	
			magic = "img3"
			is_img3 = True

			file.seek(12, os.SEEK_CUR)
			while True:
				tag = file.read(12)
				if not tag:
					break
				(img_type, total_len, data_len) = tag_unpack(tag)
				data_len &= ~15
				return magic, img_type
		else:
			file.seek(7, 0)
			magic = file.read(4)
				
			if magic != b'IM4P':
				return None
			else:
				magic = "img4"
			
			file.seek(2, os.SEEK_CUR)
			img_type = file.read(4)
			return magic, img_type


def decrypt_img(input, output, magic, key, iv, openssl='openssl'):
	image_type = get_image_type(input)
	if image_type == None:
		print("[e] %s is not an IMG3 file" % input)
		sys.exit(1)
	if magic == "img3":
		with open(input, 'rb') as f:
			f.seek(20, os.SEEK_CUR)

			while True:
				tag = f.read(12)
				if not tag:
					break
				(tag_type, total_len, data_len) = tag_unpack(tag)
				data_len &= ~15

				if tag_type == b'ATAD':
					print("[x] decrypting %s to %s..." % (input, output))
					aes_len = str(len(key) * 4)
					# OUCH!
					# Perhaps we an OpenSSL wrapper for Python 3.1
					# (although it is actually quite fast now)
					p = subprocess.Popen([openssl, 'aes-' + aes_len + '-cbc', '-d', '-nopad', '-K', key, '-iv', iv, '-out', output], stdin=subprocess.PIPE)
					bufsize = 16384
					buf = bytearray(bufsize)

					while data_len:
						bytes_to_read = min(data_len, bufsize)
						data_len -= bytes_to_read
						if bytes_to_read < bufsize:
							del buf[bytes_to_read:]
						f.readinto(buf)
						p.stdin.write(buf)
					p.stdin.close()

					if p.wait() != 0 or not os.path.exists(output):
						print("[e] Decryption failed")
					return

				else:
					f.seek(total_len - 12, os.SEEK_CUR)

			print("[w] Nothing was decrypted from %s" % input)
	elif magic == "img4":
		print("[i] decrypting %s to %s..." % (input, output))
		FNULL = open(os.devnull, 'w')
		try:
			p = subprocess.Popen(['img4', '-i', input, output, iv + key], stdout=FNULL)
		except:
			print("[e] can't decrypt file, is img4 tool in $PATH ?")
			sys.exit(1)
	else:
		return
