#!/usr/bin/python3
# -*- coding:utf-8 -*-

import coloredlogs
import logging
import logging.config
import elevate
import os

REPO_NAME = "retenet"

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    VERSION = fr.read().strip()

try:
    USER_CONFIG_PATH = f"{os.environ['XDG_CONFIG_HOME']}/rete"
except KeyError:
    USER_CONFIG_PATH = f"{os.environ['HOME']}/.config/rete"
if not os.path.exists(USER_CONFIG_PATH):
    os.makedirs(USER_CONFIG_PATH)

try:
    USER_DATA_PATH = f"{os.environ['XDG_DATA_HOME']}/rete"
except KeyError:
    USER_DATA_PATH = f"{os.environ['HOME']}/.local/share/rete"
if not os.path.exists(USER_DATA_PATH):
    os.makedirs(USER_DATA_PATH)

DOWNLOAD_DIR = f"{os.environ['HOME']}/Downloads"

BROWSERS = ["brave", "chromium", "firefox", "opera", "tbb"]

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"standard": {"format": "%(message)s"},},
        "handlers": {
            "screen": {"level": "INFO", "class": "logging.StreamHandler",},
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": f"{USER_DATA_PATH}/rete.log",
            },
        },
        "loggers": {
            "": {"handlers": ["screen", "file"], "level": "DEBUG", "propagate": True}
        },
    }
)
coloredlogs.install()
