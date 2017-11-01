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
    Given directory and pattern, return list of files
    """

    lsof = list()

    if not os.path.isdir(dir_name):
        return None

    for output_name in os.listdir(dir_name):
        if fnmatch.fnmatch(output_name, "*.xz"):
            fname = (dir_name, output_name)
            lsof.append(fname)

    return lsof


def process_all(dir_name, pattern):
    """
    Given directory name and pattern, process all files in the directory which follows the pattern
    """

    lsof = get_lsof(dir_name, pattern)
    if lsof is None:
        return None

    photons = list()
    electrons = list()
    positrons = list()

    for dir_name, run_name in lsof:
        gg, ee, pp = process_run.process_run(dir_name, run_name)

        if gg is not None:
            for g in gg:
                photons.append(g)

        if ee is not None:
            for e in ee:
                electrons.append(e)

        if pp is not None:
            for p in pp:
                positrons.append(p)

    return (photons if len(photons)>0 else None, electrons if len(electrons)>0 else None, positrons if len(positrons)>0 else None)


if __name__ =='__main__':
    nof_args = len(sys.argv)

    if nof_args == 1:
        print("need dir_name")
        sys.exit(1)

    dir_name = None
    if nof_args >= 2:
        dir_name = sys.argv[1]

    g, e, p = process_all(dir_name, PATTERN)

    print(len(g))
    print(len(e))
    print(len(p))

    sys.exit(rc)
