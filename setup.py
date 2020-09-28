# -*- coding: utf-8 -*-
"""
setup.py - Install solvecaptcha package on your
computer.
How to run this::
    for development::
    >>> python setup.py develop
    for complete installation on machine::
    >>> python setup.py install
"""
from setuptools import setup

__author__ = "Mack Waters"

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()


setup(
    name="solvecaptcha",
    author="Mack Waters",
    url='https://github.com/mackosmium/solvecaptcha',
    version="0.1",
    description="Async/Sync API wrapper for 2captcha.com",
    packages=["solvecaptcha"],
    install_requires=requirements,
)
