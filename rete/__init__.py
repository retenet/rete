#!/usr/bin/python3
# -*- coding:utf-8 -*-

from pathlib import Path
import coloredlogs
import logging
import logging.config
import subprocess
import os

REPO_NAME = "retenet"

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    VERSION = fr.read().strip()

# rete has been elevated
if "SUDO_USER" in os.environ:
    user = os.environ["SUDO_USER"]

    USER_CONFIG_PATH = f"/home/{user}/.config/rete"
    USER_DATA_PATH = f"/home/{user}/.local/share/rete"
    DOWNLOAD_DIR = f"/home/{user}/Downloads"
else:
    try:
        USER_CONFIG_PATH = f"{os.environ['XDG_CONFIG_HOME']}/rete"
    except KeyError:
        USER_CONFIG_PATH = f"{os.environ['HOME']}/.config/rete"

    try:
        USER_DATA_PATH = f"{os.environ['XDG_DATA_HOME']}/rete"
    except KeyError:
        USER_DATA_PATH = f"{os.environ['HOME']}/.local/share/rete"

    DOWNLOAD_DIR = f"{os.environ['HOME']}/Downloads"

if not os.path.exists(USER_CONFIG_PATH):
    os.makedirs(USER_CONFIG_PATH)

if not os.path.exists(USER_DATA_PATH):
    os.makedirs(USER_DATA_PATH)

# setup pulseaudio socket
pulse_socket = f"{USER_DATA_PATH}/pulseaudio.socket"
if os.path.exists(pulse_socket) and not os.path.exists("/tmp/rete_launched"):
    Path("/tmp/rete_launched").touch()
    os.remove(pulse_socket)
else:
    create_pulse_socket = (
        f"pactl load-module module-native-protocol-unix socket={pulse_socket}"
    )
    subprocess.call(
        create_pulse_socket.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )


BROWSERS = ["brave", "chromium", "firefox", "opera", "tbb"]

coloredlogs.install()
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "loggers": {"": {"level": "DEBUG", "handlers": ["console", "file"]}},
        "formatters": {
            "colored_console": {
                "()": "coloredlogs.ColoredFormatter",
                "format": "%(levelname)s %(message)s",
                "datefmt": "%H:%M:%S",
            },
            "file_format": {
                "format": "%(asctime)s :: %(funcName)s in %(filename)s (l:%(lineno)d) :: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "colored_console",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": "DEBUG",
                "formatter": "file_format",
                "class": "logging.FileHandler",
                "filename": f"{USER_DATA_PATH}/rete.log",
            },
        },
    }
)

logging.addLevelName(logging.DEBUG, "[+]")
logging.addLevelName(logging.INFO, "[i]")
logging.addLevelName(logging.WARNING, "[!]")
logging.addLevelName(logging.ERROR, "[-]")
