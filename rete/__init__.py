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
    LOG_PATH = f"{os.environ['XDG_DATA_HOME']}/rete"
except KeyError:
    LOG_PATH = f"{os.environ['HOME']}/.local/share/rete"
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

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
                "filename": f"{LOG_PATH}/rete.log",
            },
        },
        "loggers": {
            "": {"handlers": ["screen", "file"], "level": "DEBUG", "propagate": True}
        },
    }
)
coloredlogs.install()
