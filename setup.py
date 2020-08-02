#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.install import install
import shutil
import grp
import pwd
import sys
import os


class PermissionDenied(Exception):
    pass


class InstallWrapper(install):
    def run(self):
        self._startup_check()
        self._install_config()
        self._install_data()
        install.run(self)

    def _fix_folder_perms(self, path):

        if "SUDO_USER" in os.environ:
            user = os.environ["SUDO_USER"]
        else:
            user = os.environ["USER"]

        uid = pwd.getpwnam(user).pw_uid
        gid = pwd.getpwnam(user).pw_gid

        for root, dirs, files in os.walk(path):
            os.chown(root, uid, gid)
            for d in dirs:
                dname = os.path.join(root, d)
                os.chown(dname, uid, gid)
            for f in files:
                fname = os.path.join(root, f)
                os.chown(fname, uid, gid)

    def _get_user(self):
        if "SUDO_USER" in os.environ:
            user = os.environ["SUDO_USER"]
        else:
            user = os.environ["USER"]
        return user

    def _startup_check(self):

        # Are you root ?
        if os.geteuid() == 0:
            return

        # Are you in docker group ?
        user_grps = [
            g.gr_name for g in grp.getgrall() if os.environ["USER"] in g.gr_mem
        ]
        if "docker" in user_grps:
            return

        # Now we might have a problem...
        raise PermissionDenied(
            "Current user will not have permisson to execute commands. Either install as root, or join docker group."
        )

    def _install_config(self):
        user = self._get_user()

        config_dir = f"/home/{user}/.config/rete"
        if os.path.exists(f"{config_dir}/rete.yml"):
            return

        if not os.path.exists(config_dir):
            shutil.copytree("config", config_dir)
        self._fix_folder_perms(config_dir)

    def _install_data(self):
        user = self._get_user()

        data_dir = f"/home/{user}/.local/share/rete"
        if os.path.exists(f"{data_dir}/chrome.json"):
            return

        if not os.path.exists(data_dir):
            shutil.copytree("data", data_dir)
        self._fix_folder_perms(data_dir)


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
    extras_require={"dev": ["black==19.10b0", "ipython==7.13.0", "pytest==4.6.7"],},
    entry_points={"console_scripts": ["rete = rete.cli:main",],},
    include_package_data=True,
    cmdclass={"install": InstallWrapper},
)
