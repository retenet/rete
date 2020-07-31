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

from rete import BROWSERS, USER_CONFIG_PATH, VERSION
from rete.utils import parse_config, run_container, pull_image, get_containers

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
    parser.add_argument("--vpn", required=False, help="Use a VPN")
    parser.add_argument("--proxy", required=False, help="PROTO://IP:PORT")

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

    logger.debug(args)
    return args


def main():

    args = get_args()

    # What action are we taking?
    if args.config:
        config_path = f"{USER_CONFIG_PATH}/rete.yml"
        if os.environ["EDITOR"]:
            subprocess.call([os.environ["EDITOR"], config_path])
        else:
            logger.error(f"$EDITOR is not defined. Edit {config_path} manually")
        return
    elif args.update:
        logger.info("Checking for Updates...")
        subprocess.call(["python3", "-m", "pip", "install", "-U", "rete"])
        return

    user_grps = [g.gr_name for g in grp.getgrall() if os.environ["USER"] in g.gr_mem]
    if "docker" not in user_grps:
        logger.debug("User not in Docker group, elevating...")
        elevate.elevate(graphical=False)

    client = docker.from_env()

    if args.rm:
        logger.info("Getting All Running Browsers...")
        for cntr in get_containers(client):
            logger.info(f"Stopping {cntr.name}...")
            cntr.stop()
        logger.info("Done.")
        return

    # Lets download the latest image
    logger.info(f"Download latest {args.browser} image...")
    pull_image(client, args.browser)


if __name__ == "__main__":
    main()
