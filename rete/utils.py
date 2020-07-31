#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import jsonschema
import logging
import docker
import shutil
import yaml
import os

from rete import REPO_NAME, USER_CONFIG_PATH, DOWNLOAD_DIR

logger = logging.getLogger(__name__)


def create_cntr_name():
    return "rete"


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
            if "Failed validating 'pattern'" in str(e):
                logger.error(
                    f"Invalid Proxy in Config File: {USER_CONFIG_PATH}/rete.yml"
                )
            else:
                logger.error(
                    f"Invalid Option in Config File: {USER_CONFIG_PATH}/rete.yml"
                )
                logger.error(e)
            exit(1)

    return cfg


def run_container(client, browser, profile, dns):
    profile_dir = ""
    security_opt = list()
    dns_list = list()

    volumes = {
        f"{USER_DATA_PATH}/pulseaudio.socket": "/tmp/pulseaudio.socket",
        f"{USER_DATA_PATH}/pulseaudio.client.conf": "/etc/pulse/client.conf",
        "/tmp/.X11-unix/": "/tmp/.X11-unix/",
        DOWNLOAD_DIR: "/home/user/Downloads",
    }

    if profile != "temp":
        profile_dir = f"{USER_DATA_PATH}/profiles/browser/profile"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        volumes[profile_dir] = "/home/user/profile"

    if browser in ["brave", "chromium", "opera"]:
        security_opt.append(f"seccomp={os.path.dirname(__file__)}/chrome.json")

    if dns:
        dns_list.append(dns)

    cntr = client.containers.run(
        f"{REPO_NAME}/{browser}",
        detach=True,
        devices=["/dev/snd", "/dev/dri"],
        environment={
            "BROWSER": browser,
            "DISPLAY": os.environ["DISPLAY"],
            "PROFILE_NAME": profile,
            "PULSE_SERVER": "unix:/tmp/pulseaudio.socket",
            "PULSE_COOKIE": "/tmp/pulseaudio.cookie",
        },
        hostname=profile,
        name=create_cntr_name(),
        dns=dns_list,
        security_opt=security_opt,
        volumes=volumes,
    )
    logger.info(cntr)


def pull_image(client, browser):
    cntr = client.images.pull(f"{REPO_NAME}/{browser}")
    logger.info(cntr)


def get_containers(client):
    cntrs = list()
    for cntr in client.containers.list():
        if cntr.name.find("retenet") != -1:
            cntrs.append(cntr)
    return cntrs
