# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess


def unpack_run(run_fname):
    """
    Given the run filename, unpack it

    Parameters
    ----------

    shot_name: string
        name of the archive with compressed shot data

    returns: integer
        0 is Ok, non-zero means error
    """

    cmd = "tar xJvf {0}".format(run_fname)

    rc = subprocess.call(cmd, shell=True)

    output = None
    if rc == 0:
        output = os.path.splitext(os.path.splitext(run_fname)[0])[0] # remote tar.xz

    return (rc, output)


def process_output(output):
    """
    Given the output file
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
    """
    os.remove(output)

def process_run(run_fname):
    """
    This method process one packed archive of simulation
    """

    if run_fname is None:
        return -1

    rc, output = unpack_run(run_fname)

    g = None
    e = None
    p = None
    if rc == 0:
        g, e, p = process_output(output)
        remove_leftovers(output)

    return g, e, p

if __name__ =='__main__':
    nof_args = len(sys.argv)

    if nof_args == 1:
        print("need file name")
        sys.exit(1)

    run_fname = None
    if nof_args >= 2:
        run_fname = sys.argv[1]

    g, e, p = process_run(run_fname)

    rc = 0 if g is None else 1

    sys.exit(rc)
