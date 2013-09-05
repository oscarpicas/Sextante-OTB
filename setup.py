# -*- coding: utf-8 -*-

from setuptools import setup
import sys

# Stallion requirements
install_requirements = [
        'setuptools>=0.6c11',
        'docutils>=0.8.1',
        'nose',
        'nose-regression',
]


def long_description():
    if sys.version_info >= (3, 0, 0):
        f = open("README.md", mode="r", encoding="utf-8")
    else:
        f = open("README.md", mode="r")

    return f.read()


setup(
    name='Sextante-OTB',
    version=sextante-otb.__version__,
    url='https://github.com/oscarpicas/Sextante-OTB/',
    license='GNU General Public License v2 (GPLv2)',
    author=sextante-otb.__author__,
    author_email='oscar.picas-puig@c-s.fr',
    description='OTB interface to sextante library.',
    long_description=long_description(),
    keywords='sextante, otb',
    platforms='Any',
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
