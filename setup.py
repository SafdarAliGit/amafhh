from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in amafhh/__init__.py
from amafhh import __version__ as version

setup(
	name="amafhh",
	version=version,
	description="this is amafhh app",
	author="Tech Ventures",
	author_email="safdar211@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
