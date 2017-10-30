# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess


def unpack_run(dir_name, run_name):
    """
    Given the run directory and filename, unpack it

    Parameters
    ----------

    dir_name: string
        name of the directory of the cases

    run_name: string
        name of the archive with compressed run data

    returns: (integer, output
        0 is Ok, non-zero means error
    """
    cmd = "tar xJvf {0}".format(os.path.join(dir_name, run_name))

    rc = subprocess.call(cmd, shell=True)

    output = None
    if rc == 0:
        output = os.path.splitext(os.path.splitext(run_name)[0])[0] # remote tar.xz

    return (rc, output)


def process_output(output):
    """
    Given the output file, filter out photons, electrons and positrons
    """

    if output is None:
        return (None, None, None) # no photons, electrons or positrons

    photons   = list()
    electron  = list()
    positrons = list()

    with open(output, "r") as f:
        for cnt, line in enumerate(f):
            if "GGG" in line:
                photons.append(line)
            elif "EEE" in line:
                electrons.append(line)
            elif "PPP" in line:
                positrons.append(line)

    return (photons if len(photons)>0 else None, electrons if len(electrons)>0 else None, positrons if len(positrons)>0 else None)


def remove_leftovers(output):
    """
    Remove the output file
    """
    os.remove(output)

def process_run(dir_name, run_name):
    """
    Given the run directory and filename, process run

    Parameters
    ----------

    dir_name: string
        name of the directory of the cases

    run_name: string
        name of the archive with compressed run data
    """

    if run_name is None:
        return -1

    rc, output = unpack_run(dir_name, run_name)

    g = None
    e = None
    p = None
    if rc == 0:
        g, e, p = process_output(output)
        remove_leftovers(output)

    return g, e, p

if __name__ =='__main__':
    nof_args = len(sys.argv)

    if nof_args == 1 or  nof_args == 2:
        print("need directory and file name")
        sys.exit(1)

    dir_name = None
    if nof_args >= 2:
        dir_name = sys.argv[1]

    run_name = None
    if nof_args >= 3:
        run_name = sys.argv[2]

    g, e, p = process_run(dir_name, run_name)

    rc = 0 if g is None else 1

    sys.exit(rc)
