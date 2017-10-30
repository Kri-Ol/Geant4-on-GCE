# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import fnmatch
import subprocess

import process_run

PATTERN = "*.tar.xz"


def get_lsof(dir_name, pattern):
    """
    """

    lsof = list()

    if not os.path.isdir(dir_name):
        return None

    for output_name in os.listdir(dir_name):
        if fnmatch.fnmatch(output_name, "*.xz"):
            fname = os.path.join(dir_name, output_name)
            lsof.append(fname)

    return lsof


def process_all(dir_name, pattern):
    """
    """

    lsof = get_lsof(dir_name, pattern)
    if lsof is None:
        return None

    photons = list()
    electrons = list()
    positrons = list()



if __name__ =='__main__':
    nof_args = len(sys.argv)

    if nof_args == 1:
        print("need dir name")
        sys.exit(1)

    dir_name = None
    if nof_args >= 2:
        dir_name = sys.argv[1]

    rc = process_all(dir_name)

    sys.exit(rc)
