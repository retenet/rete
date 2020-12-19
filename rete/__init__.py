#!/usr/bin/python3
# -*- coding:utf-8 -*-

import logging
import logging.config
from rich.logging import RichHandler
from pathlib import Path
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
tmp_file = "/tmp/rete_setup"
if not os.path.exists(tmp_file) and os.path.exists(pulse_socket):
    Path(pulse_socket).unlink()

if not os.path.exists(pulse_socket):
    Path(tmp_file).touch()
    create_pulse_socket = (
        f"pactl load-module module-native-protocol-unix socket={pulse_socket}"
    )
    subprocess.call(
        create_pulse_socket.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )

BROWSERS = ["brave", "chromium", "firefox", "opera", "tbb"]

logging.basicConfig(
    level='INFO',
    format='%(message)s',
    datefmt='[%X]',
    handlers=[RichHandler(rich_tracebacks=True)]
)
