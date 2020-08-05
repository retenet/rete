#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import subprocess
import jsonschema
import logging
import docker
import shutil
import yaml
import pwd
import os

from rete import (
    DOWNLOAD_DIR,
    USER_CONFIG_PATH,
    USER_DATA_PATH,
    pulse_socket,
    REPO_NAME,
)

logger = logging.getLogger(__name__)


def fix_folder_perms(path):

    if "SUDO_USER" in os.environ:
        user = os.environ["SUDO_USER"]
    else:
        user = os.environ["USER"]

    uid = pwd.getpwnam(user).pw_uid
    gid = pwd.getpwnam(user).pw_gid

    for root, dirs, files in os.walk(path):
        logger.debug(f"chown {uid}:{gid} {root}")
        os.chown(root, uid, gid)
        for d in dirs:
            dname = os.path.join(root, d)
            logger.debug(f"chown {uid}:{gid} {dname}")
            os.chown(dname, uid, gid)


def setup_vpn(client, vpn):
    volumes = list()
    environment = dict()

    if not vpn:
        return "bridge"

    pull_image(client, "tunle")

    # User must set provider with user/pass or a config
    if "provider" in vpn:
        environment["PROVIDER"] = vpn["provider"]
        if vpn["provider"] not in ["tor", "generic"]:
            if "user" in vpn and "pass" in vpn:
                environment["UNAME"] = vpn["user"]
                environment["PASSWD"] = vpn["pass"]
            else:
                logger.error("Cannot Start VPN without Login Creds or a Config")
                exit(1)
        elif vpn["provider"] == "generic":
            # These may be set in tunle
            environment["UNAME"] = "generic"
            environment["PASSWD"] = "generic"

            if "config" in vpn and vpn["config"]:
                volumes.append(f'{vpn["config"]:/tmp/vpn}')
            else:
                logger.error("Cannot Start VPN without Login Creds or a Config")
                exit(1)
    elif "config" in vpn and vpn["config"]:
        volumes.append(f'{vpn["config"]:/tmp/vpn}')
    else:
        logger.error("Cannot Start VPN without Login Creds or a Config")
        exit(1)

    cntr_name = create_cntr_name(client, vpn["provider"], True)
    logger.info(f"Starting {cntr_name}...")
    cntr = client.containers.run(
        f"{REPO_NAME}/tunle",
        cap_drop=["all"],
        cap_add=["MKNOD", "SETUID", "SETGID", "NET_ADMIN", "NET_RAW"],
        detach=True,
        devices=["/dev/net/tun"],
        environment=environment,
        hostname=vpn["provider"],
        name=cntr_name,
        remove=True,
        shm_size="3G",
        volumes=volumes,
    )

    return f"container:{cntr_name}"


def create_cntr_name(client, browser, vpn=False):
    if vpn:
        name = f"tunle_{browser}"
    else:
        name = f"rete_{browser}"
    cntrs = list()
    for cntr in client.containers.list():
        if cntr.name.find(name) != -1:
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
        f"{USER_CONFIG_PATH}/rete_schema.yml"
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
        f"{USER_DATA_PATH}/pulseaudio.client.conf:/etc/pulse/client.conf",
        f"{DOWNLOAD_DIR}:/home/user/Downloads",
        "/tmp/.X11-unix/:/tmp/.X11-unix/",
    ]

    if profile != "temp":
        profile_dir = f"{USER_DATA_PATH}/profiles/{browser}/{profile}"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        volumes.append(f"{profile_dir}:/home/user/profile")

    if browser in ["brave", "chromium", "opera"]:
        with open(f"{USER_DATA_PATH}/chrome.json") as fr:
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
    if vpn_name == "bridge":
        hostname = profile
    else:
        hostname = None
        dns_list = list()

    fix_folder_perms(f"{USER_DATA_PATH}")
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
        hostname=hostname,
        name=create_cntr_name(client, browser),
        dns=dns_list,
        network_mode=vpn_name,
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
