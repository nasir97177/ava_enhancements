# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ava_enhancements/__init__.py
from ava_enhancements import __version__ as version

setup(
	name="ava_enhancements",
	version=version,
	description="Custom App for Ava Water customizations",
	author="Furqan Asghar",
	author_email="furqan.79000@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
