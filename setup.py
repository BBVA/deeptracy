#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    readme = f.read()

requirements = [str(ir.req) for ir in parse_requirements('requirements.txt', session=PipSession())]

test_requirements = [str(ir.req) for ir in parse_requirements('requirements_test.txt', session=PipSession())]

setup(
    name='deeptracy',
    version='0.0.1',
    author='BBVA',
    description=readme,
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    keywords='deeptracy',
    classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.6',
            'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='tests',
    tests_require=test_requirements
)
