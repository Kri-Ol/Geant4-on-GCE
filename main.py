#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
import paramiko

def run(app, script):
    """
    Run application with script as its first argument

    :param app: application to run
    :type app: str
    :param app: application to run
    :type app: str
    :returns: file name of the stdout output
    :rtype: str
    """

    p = subprocess.Popen([app, script], stdin  = subprocess.PIPE,
                                        stdout = subprocess.PIPE,
                                        stderr = subprocess.PIPE)
    out, err = p.communicate()

    fname = "LOG"
    with open(fname, "w") as the_file:
        the_file.write(out)

    return fname

def upload_sftp(aname):
    """
    Upload data to the server using SFTP
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

def compress_data(fname):
    """
    Pack and compress everything outgoing

    :param fname: file to compress
    :type fname: str
    """

    dst = fname + ".tar.xz"
    rc = subprocess.call(["tar", "-cvJSf", dst, fname],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    if rc != 0:
        return (rc, None)

    return (rc, dst)

def main():
    """
    Run app using
    """

    log = run("DICOM", "run.mac")

    rc = subprocess.Popen(["xz", log], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    fname = log + ".xz"

    rc = send(fname)

    return rc

if __name__ == '__main__':
    return main()
