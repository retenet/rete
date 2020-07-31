#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import jsonschema
import logging
import docker
import shutil
import yaml
import os

from rete import REPO_NAME, USER_CONFIG_PATH

logger = logging.getLogger(__name__)


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
                logger.error(f"Invalid Proxy in Config File: {USER_CONFIG_PATH}/rete.yml")
            else:
                logger.error(f"Invalid Option in Config File: {USER_CONFIG_PATH}/rete.yml")
                logger.error(e)
            exit(1)

    return cfg


def run_container(client, browser, detach=False):
    cntr = client.containers.run(f"{REPO_NAME}/{browser}", detach=detach)
    logger.info(cntr)


def pull_image(client, browser):
    cntr = client.images.pull(f"{REPO_NAME}/{browser}")
    logger.info(cntr)
