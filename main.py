#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
import logging
import json

def run(app, mac):
    """
    Run application with macro as its first argument

    Parameters
    ------------

    app: string
        application to run

    mac: string
        macro to pass to the application as first argument

    returns: string
        file name of the stdout output
    """
    logging.info("Running app {0} wih the macro {1}: {0} {1}".format(app, mac) )

    p = subprocess.Popen([app, mac], stdin  = subprocess.PIPE,
                                     stdout = subprocess.PIPE,
                                     stderr = subprocess.PIPE)
    std_out, std_err = p.communicate()

    fname = app + "_" + mac + ".output"
    with open(fname, "w") as the_file:
        the_file.write(std_out)

    logging.info("Done with run")
    return fname

def upload_sftp(tarname):
    """
    Upload data to the server using SFTP

    Parameters
    ------------

    tarname: string
        TAR archive to create

    returns: string
        file name of the stdout output
    """

    try:
        host = "75.148.23.250"
        port = 22
        transport = paramiko.Transport((host, port))

        password = "twobob2015@xc"
        username = "sphinx"
        transport.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        dest_dir = "."
        remote_dir = os.path.join("/home/sphinx/gcloud", dest_dir)

        try:
            sftp.chdir(remote_dir)  # test if remote_dir exists
        except IOError:
            sftp.mkdir(remote_dir)
            sftp.chdir(remote_dir)

            destination_path = os.path.join(remote_dir, aname)
            sftp.put(aname, destination_path)

            sftp.close()
            transport.close()

            rc = 0

    except OSError:
        logging.debug("upload_sftp: OS failure ")
        rc = -1
        return rc

    return rc

def compress_data(tarname, *fnames):
    """
    Pack and compress everything outgoing

    :param arcname: name of the archive to make
    :type arcname: str
    :param fnames: files to compress
    :type fnames: list of str
    """

    dst = tarname + ".tar.xz"

    cmd = ["tar", "-cvJSf", dst]
    for
    rc = subprocess.call(["tar", "-cvJSf", dst, fname],
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

    output = run(app, "run.mac")
    if output == None:
        return 1

    tarname = compress_data(output, output, log)
    if tarname == None:
        return 2

    rc = upload_sftp(tarname)

    return rc

if __name__ == '__main__':
    argc = len(sys.argv)

    if argc == 1:
        print("Usage: main.py config.json <optional number of tracks>")

    nof_tracks = -1
    if argc > 2:
        nof_tracks = int(sys.argv[2])

    cfg_json = sys.argv[1]

    sys.exit(main(cfg_json, nof_tracks))
