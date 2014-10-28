#!/usr/bin/env python

import os
import platform
from pip.index import PackageFinder
from pip.req import parse_requirements
from setuptools import setup, find_packages

root_dir = os.path.abspath(os.path.dirname(__file__))

requirements_file = 'base.txt'
requirements_path = os.path.join(root_dir, 'requirements', requirements_file)

finder = PackageFinder([], [])
requirements = parse_requirements(requirements_path, finder)
install_requires = [str(r.req) for r in requirements]

version = '0.1'

setup(
    name="seraph",
    version=version,
    packages=find_packages(),
    zip_safe=False,
    description="",
    long_description="""\
""",
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Liza Daly',
    author_email='lizadaly@gmail.com',
    url='',
    license='',
    include_package_data=True,
    install_requires=install_requires,
    entry_points="""
    # -*- Entry points: -*-
    """,
)
