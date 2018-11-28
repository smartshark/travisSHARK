#!/usr/bin/env python

import sys

from setuptools import setup, find_packages

if not sys.version_info[0] == 3:
    print('only python3 supported!')
    sys.exit(1)

setup(
    name='travisSHARK',
    version='2.0.1',
    description='Collects data from travis-ci and stores it into a mongo database.',
    install_requires=['mongoengine', 'pymongo', 'requests', 'pycoshark>=1.0.17'],
    dependency_links=['git+https://github.com/smartshark/pycoSHARK.git@1.0.17#egg=pycoshark-1.0.17'],
    author='ftrautsch',
    author_email='fabian.trautsch@uni-goettingen.de',
    url='https://github.com/smartshark/travisSHARK',
    download_url='https://github.com/smartshark/travisSHARK/zipball/master',
    test_suite ='tests',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache2.0 License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
