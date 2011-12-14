import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="geonode-documents",
    version="0.1",
    author="Simone Dalmasso, Ariel Nunez",
    author_email="simone.dalmasso@gmail.com",
    description="Documents extension for GeoNode",
    long_description=(read('README.rst')),
    classifiers=[
        'Development Status :: 2 - Pre-alpha',
        'Framework :: GeoNode',
        'License :: OSI Approved :: BSD',
    ],
    license="BSD",
    keywords="geonode django",
    url='https://github.com/simod/geonode-documents',
    scripts = [
              ],
    packages=find_packages('.'),
    include_package_data=True,
	package_data={
		'':['fixtures/*.*','templates/*.*'],
	},
    zip_safe=False,
)
