#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import logging
import json
import paramiko
import hashlib

def fix_macro(mac, nof_tracks):
    """
    Set number of tracks in macro to user-defined value

    Parameters
    ------------

    mac: string
        macro to pass to the application as first argument

    nof_tracks: integer
        number of tracks to set

    returns: integer
        return code
    """
    logging.info("Fixing the macro {0} {1}".format(mac, nof_tracks) )

    if nof_tracks < 0:
        return 0

    lines = []
    with open(mac, "rt") as f:
        lines = f.readlines()

    b = -1
    k = 0
    for line in lines:
        if "/run/beamOn" in line:
            b = k
            break
        k += 1

    if b < 0:
        return 0

    s = lines[b].split(' ')
    lines[b] = s[0] + " " + str(nof_tracks)

    with open(mac, "wt") as f:
        f.writelines(lines)

    return 0

def run(app, mac, nof_tracks):
    """
    Run application with macro as its first argument

    Parameters
    ------------

    app: string
        application to run

    mac: string
        macro to pass to the application as first argument

    nof_tracks: integer
        number of tracks to run

    returns: string
        file name of the stdout output
    """

    logging.info("Running app {0} wih the macro {1}: {2}".format(app, mac, nof_tracks) )

    rc = fix_macro(mac, nof_tracks)
    if rc != 0:
        return None

    cmd = [os.path.join(".",app) + " " + mac]

    p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    std_out, std_err = p.communicate()

    fname = app + "_" + mac + ".output"
    with open(fname, "w") as the_file:
        the_file.write(std_out)

    logging.info("Done with run")
    return fname

def read_credentials(creds):
    """
    Given the JSON credentials, return tuple with relevant info

    creds: string
        JSON file with credentials

    returns: tuple
        host, port, user, pswd, dest
    """

    data = None
    with open(creds) as json_file:
        data = json.load(json_file)

    host = data["host"]
    port = data["port"]
    user = data["user"]
    pswd = data["pswd"]
    dest = data["dest"]

    return (host, port, user, pswd, dest)

def upload_sftp(creds, tarname):
    """
    Upload data to the server using SFTP

    Parameters
    ------------

    creds: string
        JSON file with credentials

    tarname: string
        TAR archive to create

    returns: string
        file name of the stdout output
    """

    rc = 0

    try:

        host, port, user, pswd, dest = read_credentials(creds)

        transport = paramiko.Transport((host, port))

        transport.connect(username=user, password=pswd)

        sftp = paramiko.SFTPClient.from_transport(transport)

        dest_dir   = dest
        remote_dir = dest_dir

        try:
            sftp.chdir(remote_dir)  # test if remote_dir exists
        except IOError:
            sftp.mkdir(remote_dir)

        sftp.chdir(remote_dir)

        destination_path = os.path.join(remote_dir, tarname)
        sftp.put(tarname, destination_path)

        sftp.close()
        transport.close()

        rc = 0

    except OSError:
        logging.debug("upload_sftp: OS failure ")
        rc = -1
        return rc

    return rc

def sign(*fnames):
    """
    Compute hash functions of the downloaded cups, to be
    used as a signature

    Parameters
    ------------

    fnames: list
        file names to sign

    returns: string
        file name of file with signatures
    """

    logging.info("Start data signing")

    algo = "sha1"

    if not (algo in hashlib.algorithms):
        raise Exception("data_uploader", "No SHA1 hash available")

    hashl = []

    # everything in work.dir: input, phantom, cups, etc
    for fname in fnames:

        hasher = hashlib.sha1()

        ctx = fname
        with open(ctx, "rb") as afile:
            buf = afile.read()
            hasher.update(buf)

            hashl.append((ctx, hasher.hexdigest()))

    with open(algo, "wt") as f:
        for l in hashl:
            f.write(l[0])
            f.write(": ")
            f.write(l[1])
            f.write("\n")

    logging.info("Done data signing")

    return algo

def compress_data(tarname, *fnames):
    """
    Pack and compress everything outgoing

    :param arcname: name of the archive to make
    :type arcname: str
    :param fnames: files to compress
    :type fnames: list of str
    """

    signs = sign(*fnames)

    dst = tarname + ".tar.xz"

    cmd = ["tar", "-cvJSf", dst]
    for fname in fnames:
        cmd.append(fname)
    cmd.append(signs)

    rc = subprocess.call(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    if rc != 0:
        return (rc, None)

    return (rc, dst)

def read_config(cfname):
    """
    Read cluster configuration file as JSON

    Parameters
    ------------

    cfname: string
        cluster config name

    returns: dictionary
        JSON parsed as dictionary
    """

    data = None
    with open(cfname) as data_file:
        data = json.load(data_file)
    return data

def main(cfg_json, nof_tracks):
    """
    Run app using configuration from JSON and # of tracks

    Parameters
    ------------

    cfg_json: string
        JSON file name with configuration

    nof_tracks: int
        # of tracks to compute

    returns: int
        return code, 0 on success, non-zero on failure
    """

    wrk_dir = os.getcwd()
    data    = read_config(cfg_json)

    app = data["application"]
    mac = data["macro"]

    log = app + ".rlog"

    # configuring logging
    logging.basicConfig(filename=os.path.join(wrk_dir, log), level=logging.DEBUG)
    logging.info("Started")

    logging.info("Running JSON {0} with # of tracks {1}".format(cfg_json, nof_tracks))

    output = run(app, mac, nof_tracks)
    if output == None:
        return 1

    rc, tarname = compress_data(output, output, log)
    if tarname == None:
        return rc

    rc = upload_sftp(tarname)

    return rc

if __name__ == '__main__':
    argc = len(sys.argv)

    if argc == 1:
        print("Usage: main.py config.json <optional number of tracks>")
        sys.exit(0)

    nof_tracks = -1
    if argc > 2:
        nof_tracks = int(sys.argv[2])

    cfg_json = sys.argv[1]

    sys.exit(main(cfg_json, nof_tracks))
