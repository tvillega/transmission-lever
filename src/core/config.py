#!/usr/bin/env python

import os
import json


def get_config() -> dict:
    """
    Get a config dictionary from a json file
    :return: config dictionary
    """

    f = open(os.path.dirname(__file__) + "/../../transmission-lever.json")

    cfg = json.load(f)
    return cfg