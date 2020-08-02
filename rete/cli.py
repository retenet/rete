#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import subprocess
import argparse
import logging
import elevate
import docker
import yaml
import grp
import os

from rete import (
    BROWSERS,
    DOWNLOAD_DIR,
    USER_CONFIG_PATH,
    USER_DATA_PATH,
    VERSION,
)
from rete.utils import (
    parse_config,
    run_container,
    pull_image,
    get_containers,
    add_xhost,
)

logger = logging.getLogger(__name__)


def get_args():
    cfg = parse_config()

    parser = argparse.ArgumentParser(f"rete version {VERSION}")
    parser.add_argument(
        "browser",
        nargs="?",
        choices=BROWSERS,
        default=cfg["browser"]["name"],
        help="Supported Browsers",
    )

    parser.add_argument(
        "-p",
        "--profile",
        default=cfg["profile"]["default"],
        required=False,
        help="Profile Name",
    )
    parser.add_argument("-t", action="store_true", help="Temporary Profile")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--config", action="store_true", required=False, help="Open Config for Editing"
    )
    group.add_argument(
        "--rm", action="store_true", required=False, help="Stop and Remove ALL Browsers"
    )
    group.add_argument(
        "--update", action="store_true", required=False, help="Check for Upates"
    )

    args = parser.parse_args()

    if args.t:
        args.profile = "temp"

    return args, cfg


def main():

    args, cfg = get_args()

    # What action are we taking?
    if args.config:
        config_path = f"{USER_CONFIG_PATH}/rete.yml"
        if os.environ["EDITOR"]:
            subprocess.call([os.environ["EDITOR"], config_path])
        else:
            logger.error(f"$EDITOR is not defined. Edit {config_path} manually")
        return

    user_grps = [g.gr_name for g in grp.getgrall() if os.environ["USER"] in g.gr_mem]
    # Not in docker group and normal user, then elevate
    if "docker" not in user_grps and "SUDO_USER" not in os.environ:
        logger.warning("User not in Docker group, elevating...")
        elevate.elevate(graphical=False)

    client = docker.from_env()

    if args.rm:
        logger.info("Getting All Running Browsers...")
        for cntr in get_containers(client):
            logger.info(f"Stopping {cntr.name}...")
            cntr.stop()
        logger.info("Done.")
        return
    elif args.update:
        logger.info("Checking for Updates...")
        subprocess.call(["python3", "-m", "pip", "install", "-U", "rete"])
        return

    # Lets download the latest image
    pull_image(client, args.browser)

    add_xhost()

    # start browser
    if "vpn" in cfg:
        vpn = cfg["vpn"]
    else:
        vpn = None
    run_container(client, args.browser, args.profile, cfg["browser"], vpn)


if __name__ == "__main__":
    main()
