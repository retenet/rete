#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join("rete", "VERSION"), "r", encoding="utf-8") as f:
    version = f.read()

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rete",
    version=version,
    description="",
    license="GPLv3",
    long_description=long_description,
    author="retenet",
    author_email="dev@exploit.design",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    keywords="browser",
    packages=find_packages(exclude=["browsers", "contrib", "docs", "tests"]),
    install_requires=[
        "colorama==0.4.3",
        "coloredlogs==14.0",
        "docker==4.2.2",
        "elevate==0.1.3",
        "jsonschema==3.2.0",
        "PyYAML==5.3.1",
    ],
    use_scm_version=True,
    setup_required=["setuptools_scm"],
    extras_require={"dev": ["black==19.10b0", "ipython==7.13.0", "pytest==4.6.7"],},
    entry_points={"console_scripts": ["rete = rete.cli:main",],},
    include_package_data=True,
)
