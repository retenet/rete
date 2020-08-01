#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import subprocess
import jsonschema
import logging
import docker
import shutil
import yaml
import os

from rete import (
    DOWNLOAD_DIR,
    USER_CONFIG_PATH,
    USER_DATA_PATH,
    pulse_socket,
    REPO_NAME,
)

logger = logging.getLogger(__name__)


def setup_vpn(client, vpn):
    if not vpn:
        return None

    pull_image(client, f"{REPO_NAME/tunle}")


def create_cntr_name(client, browser):
    name = f"rete_{browser}"
    cntrs = list()
    for cntr in client.containers.list():
        if cntr.name.find(f"rete_{browser}") != -1:
            cntrs.append(cntr.name)

    if not cntrs:
        return name
    elif len(cntrs) == 1:
        return f"{name}_2"
    else:
        num = sorted(map(lambda x: x.split("_")[-1], sorted(cntrs)))[:-1][-1]
        return f"{name}_{num}"


def add_xhost():
    logger.debug("Adding user to xhost")
    if "SUDO_USER" in os.environ:
        xhost = f"xhost +SI:localuser:{os.environ['SUDO_USER']}"
    else:
        xhost = f"xhost +SI:localuser:{os.environ['USER']}"
    subprocess.call(xhost.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def parse_config():
    config_path = f"{USER_CONFIG_PATH}/rete.yml"
    if not os.path.exists(config_path):
        shutil.copy(f"{os.path.dirname(__file__)}/config/rete.yml", config_path)

    with open(f"{USER_CONFIG_PATH}/rete.yml") as fr, open(
        f"{os.path.dirname(__file__)}/config/rete_schema.yml"
    ) as fr2:
        try:
            cfg = yaml.safe_load(fr)
            jsonschema.validate(cfg, yaml.safe_load(fr2))
        except jsonschema.exceptions.ValidationError as e:
            if "['browser']['proxy']" in str(e):
                logger.error(
                    f"Invalid Proxy in Config File: {USER_CONFIG_PATH}/rete.yml"
                )
            elif "['browser']['dns']['ip']" in str(e):
                logger.error(
                    f"Invalid DNS IP in Config File: {USER_CONFIG_PATH}/rete.yml"
                )
            elif "['browser']['dns']['host']" in str(e):
                logger.error(
                    f"Invalid DNS HOST in Config File: {USER_CONFIG_PATH}/rete.yml"
                )
            else:
                logger.error(
                    f"Invalid Option in Config File: {USER_CONFIG_PATH}/rete.yml"
                )
                logger.error(e)
            exit(1)

    return cfg


def run_container(client, browser, profile, cfg, vpn):
    profile_dir = ""
    security_opt = list()
    dns_list = list()

    volumes = [
        f"{pulse_socket}:/tmp/pulseaudio.socket",
        f"{os.path.dirname(__file__)}/config/pulseaudio.client.conf:/etc/pulse/client.conf",
        f"{DOWNLOAD_DIR}:/home/user/Downloads",
        "/tmp/.X11-unix/:/tmp/.X11-unix/",
    ]

    if profile != "temp":
        profile_dir = f"{USER_DATA_PATH}/profiles/browser/profile"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        volumes.append(f"{profile_dir}:/home/user/profile")

    if browser in ["brave", "chromium", "opera"]:
        with open(f"{os.path.dirname(__file__)}/chrome.json") as fr:
            chrome_seccomp = fr.read()
        security_opt.append(f"seccomp={chrome_seccomp}")

    try:
        dns = cfg["dns"]["ip"]
        dns_list.append(dns)
    except KeyError:
        dns = None

    try:
        doh = cfg["dns"]["doh"]
        if doh:
            doh_domain = cfg["dns"]["host"]
        else:
            doh_domain = None
    except KeyError:
        doh_domain = None

    try:
        proxy = cfg["proxy"]
    except KeyError:
        proxy = None

    vpn_name = setup_vpn(client, vpn)

    logger.info(f"Starting {browser}...")
    cntr = client.containers.run(
        f"{REPO_NAME}/{browser}",
        detach=True,
        devices=["/dev/snd", "/dev/dri"],
        environment={
            "BROWSER": browser,
            "DISPLAY": os.environ["DISPLAY"],
            "DOH": doh_domain,
            "DNS": dns,
            "PROFILE_NAME": profile,
            "PROXY": proxy,
            "PULSE_SERVER": "unix:/tmp/pulseaudio.socket",
            "PULSE_COOKIE": "/tmp/pulseaudio.cookie",
        },
        hostname=profile,
        name=create_cntr_name(client, browser),
        dns=dns_list,
        network=vpn_name,
        remove=True,
        security_opt=security_opt,
        volumes=volumes,
    )


def pull_image(client, browser):
    logger.info(f"Downloading Latest {browser} Image...")
    cntr = client.images.pull(f"{REPO_NAME}/{browser}")


def get_containers(client):
    cntrs = list()

    logger.info(f"Retreiving Running Containers...")
    for cntr in client.containers.list():
        if cntr.name.find("retenet") != -1:
            cntrs.append(cntr)
    return cntrs
