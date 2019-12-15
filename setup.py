import sys
from setuptools import setup

if sys.version_info < (3, 6, 0):
    sys.stderr.write("ERROR: You need Python 3.6 or later to use awhtools.\n")
    exit(1)

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="autodecrypt",
    version="2.0.0",
    description="A tool to grab keys and decrypt iOS firmware images",
    license="MIT",
    packages=['autodecrypt'],
    install_requires=requirements,
    entry_points={"console_scripts": ["autodecrypt=autodecrypt.autodecrypt:main"]},
)
   
