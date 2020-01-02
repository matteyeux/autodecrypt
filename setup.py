from setuptools import find_packages, setup

def get_description():
    """Prepare long descripion."""
    f = open('README.md')
    description = f.read()
    f.close()

    return description

setup(
    name = 'autodecrypt',
    packages = ['autodecrypt'],
    version = '2.0.2',
    long_description=get_description(),
    long_description_content_type='text/markdown',
    license='MIT',
    description = 'Tool to decrypt iOS firmware images',
    author = 'matteyeux',
    author_email = 'mathieu.hautebas@gmail.com',
    url = 'https://github.com/matteyeux/autodecrypt',
    download_url = 'https://github.com/matteyeux/autodecrypt/archive/2.0.2.tar.gz',
    keywords = ['autodecrypt', 'iOS', 'iBoot'],
    install_requires = ['certifi', 'chardet', 'cssselect',
                        'idna', 'lxml', 'pyquery', 'remotezip',
                        'requests', 'tabulate', 'urllib3',
    ],
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Developers',
      'Intended Audience :: Information Technology',
      'Topic :: Utilities',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Programming Language :: Python :: 3.8',
    ],
    entry_points = {
        "console_scripts": [
            "autodecrypt=autodecrypt.autodecrypt:main",
        ]
    }

)
