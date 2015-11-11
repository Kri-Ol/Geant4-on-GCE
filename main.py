#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import logging
import json
import paramiko
import hashlib

def fix_macro_int(lines, key, value):
    """
    Fix lines to have new value for a given key
    
    lines: array of strings
        where key to be found
        
    key: string
        key
        
    value: int
        set to be for a given key
        
    returns: bool
        True on success, False otherwise
    """
    
    l = -1
    k =  0
    for line in lines:
        if key in line:
            l = k
            break
        k += 1

    if l >= 0:
        s = lines[l].split(' ')
        lines[l] = s[0] + " " + str(value) + "\n"
        return True
        
    return False


def fix_macro(mac, C, nof_tracks, nof_threads, seed):
    """
    Set number of tracks in macro to user-defined value

    Parameters
    ------------

    mac: string
        macro to pass to the application as first argument

    C: int
        collimator, in mm        

    nof_tracks: int
        number of tracks to set

    nof_threads: int
        number of threads to set

    seed: int
        RNG initial seed

    returns: int
        return code
    """
    logging.info("Fixing the macro {0} {1} {2} {3} {4}".format(mac, C, nof_tracks, nof_threads, seed) )

    lines = []
    with open(mac, "rt") as f:
        lines = f.readlines()

    # fixing up collimator
    l = -1
    k =  0
    for line in lines:
        if "C25.in" in line:
            l = k
            break
        k += 1

    if l >= 0:
        s = lines[l].split(' ')
        lines[l] = s[0] + " " + "C{0}.in".format(C)

    # fixing up nof tracks
    if nof_tracks > 0:
        rc = fix_macro_int(lines, "/run/beamOn", nof_tracks)
        if not rc:
            raise ValueError("No beamOn in macro")
    
            
    # fixing up nof threads
    if nof_threads > 0:
        rc = fix_macro_int(lines, "/run/numberOfThreads", nof_threads)
        if not rc:
            raise ValueError("No numberOfThreads in macro")

    # fixing up seed
    if seed > 0:
        rc = fix_macro_int(lines, "/random/setSeeds", seed)
        if not rc:
            raise ValueError("No setSeeds in macro")
            
    # save it all
    with open(mac, "wt") as f:
        f.writelines(lines)

    return 0

def run(app, mac, C, nof_tracks, nof_threads, seed):
    """
    Run application with macro as its first argument

    Parameters
    ------------

    app: string
        application to run

    mac: string
        macro to pass to the application as first argument
        
    C: int
        collimator, in mm        

    nof_tracks: int
        number of tracks to run

    nof_threads: int
        number of threads to run
        
    seed: int
        RNG seed
        
    returns: string
        file name of the stdout output
    """

    logging.info("Running app {0} wih the macro {1}: {2} {3} {4} {5}".format(app, mac, C, nof_tracks, nof_threads, seed) )

    rc = fix_macro(mac, C, nof_tracks, nof_threads, seed)
    if rc != 0:
        return None

    #cmd = [os.path.join(".",app) + " " + mac]
    #p = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    cmd = [os.path.join(".",app), mac]
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    
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

def main(cfg_json, C, nof_tracks, nof_threads, seed):
    """
    Run app using configuration from JSON and # of tracks

    Parameters
    ------------

    cfg_json: string
        JSON file name with configuration

    C: int
        collimator, in mm

    nof_tracks: int
        # of tracks to compute

    nof_threads: int
        # of threads to run
        
    returns: int
        return code, 0 on success, non-zero on failure
    """

    wrk_dir = os.getcwd()
    data    = read_config(cfg_json)

    app = data["application"]
    mac = data["macro"]
    crd = data["credentials"]

    log = app + ".rlog"

    # configuring logging
    logging.basicConfig(filename=os.path.join(wrk_dir, log), level=logging.DEBUG)
    logging.info("Started")

    logging.info("Running JSON {0} with C{1},  # of tracks {2} and # of threads {3} and Rseed {4}".format(cfg_json, C, nof_tracks, nof_threads, seed))

    output = run(app, mac, C, nof_tracks, nof_threads, seed)
    if output == None:
        return 1

    rc, tarname = compress_data(output, output, log)
    if tarname == None:
        return rc

    rc = upload_sftp(crd, tarname)

    return rc

if __name__ == '__main__':
    argc = len(sys.argv)

    if argc == 1:
        print("Usage: main.py config.json <collimator size in mm> <optional number of tracks> <optional number of threads> <optional RNG seed>")
        sys.exit(0)

    cfg_json = sys.argv[1]
    
    C = 25
    try:
        C = int(sys.argv[2])
    except:
        pass
        
    nof_tracks = -1
    try:
        nof_tracks = int(sys.argv[3])
    except:
        pass
    
    nof_threads = -1 
    try:
        nof_threads = int(sys.argv[4])
    except:
        pass

    seed = -1 
    try:
        seed = int(sys.argv[5])
    except:
        pass
        
    sys.exit(main(cfg_json, C, nof_tracks, nof_threads, seed))

