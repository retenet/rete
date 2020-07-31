#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import argparse
import logging
import elevate
import docker
import yaml
import grp
import os

from rete import BROWSERS, USER_CONFIG_PATH, VERSION
from rete.utils import parse_config, run_container, pull_image

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
        "-p", "--profile", default="", required=False, help="Profile Name"
    )
    parser.add_argument("-t", action="store_true", help="Temporary Profile")
    parser.add_argument("--vpn", required=False, help="Use a VPN")
    parser.add_argument("--proxy", required=False, help="PROTO://IP:PORT")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--config", required=False, help="Open Config for Editing")
    group.add_argument("--rm", required=False, help="Stop and Remove ALL Browsers")
    group.add_argument("--update", required=False, help="Check for Upates")

    args = parser.parse_args()

    if not args.browser:
        logger.error("No Browser Specified")
        exit(1)

    return args


def main():

    args = get_args()

    user_grps = [g.gr_name for g in grp.getgrall() if os.environ["USER"] in g.gr_mem]
    if "docker" not in user_grps:
        elevate.elevate(graphical=False)

    client = docker.from_env()
    # pull_image(client, args.browser)


if __name__ == "__main__":
    main()
