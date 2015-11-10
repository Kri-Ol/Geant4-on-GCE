#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import contextlib
import subprocess
import shutil

@contextlib.contextmanager
def temp_chdir(path):
    """
    Usage:
    >>> with temp_chdir(gitrepo_path):
    ...   subprocess.call('git status')

    On return from temp_chdir previous CWD will be restored

    :param path: path to go and do something here
    :type path: str
    """

    starting_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(starting_directory)

def get_geant_installation():
    """
    By checking low energy data ftom G4 installation,
    return path to the G4 setup, typically in /opt/Geant/vXXXX

    :returns: formatted string
    :rtype: str
    """

    try:
        g4ledata = os.environ["G4LEDATA"]
    except KeyError:

        raise RuntimeError("No G4LEDATA found, aborting")
    path = g4ledata
    while True:
        path, tail = os.path.split(path)

        if tail == "share":
            break

        if tail == "":
            break

    if path == "":
        raise RuntimeError("No proper G4 installation found")

    return path

def copy_GEANT4(top):
    """
    Copy Geant4 from installation place to docker

    :param top: path to top level directory
    :type top: str
    """

    src = get_geant_installation()

    if not os.path.exists(src):
        return None

    if not os.path.isdir(src):
        return None

    head, G4_version = os.path.split(src)

    dest = os.path.join(top, G4_version)
    if os.path.isdir(dest):
        shutil.rmtree(dest)

    try:
        shutil.copytree(src, dest, symlinks=True, ignore=None)
    except OSError:
        raise RuntimeError("Unable to copy Geant4, aboring")

    return src
    
def copy_creds(top, target_dir):
    """
    Copy credentials
    """

    fname = "config_credentials.json"
    
    src = os.path.join(top, "..", "..", fname)
    dst = os.path.join(top, target_dir, fname)
    
    shutil.copyfile(src, dst)
    
    return 0

def make_runtime(top, path_to_g4, target_dir):
    """
    Checkout the runtime code and build it
    """

    # get the source code

    #repo =  "https://192.168.1.230/svn/XCSW/MC_simulation/MC_phsp/Geant4"
    #rc   = subprocess.call(["svn", "checkout", repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       
    repo =  "https://github.com/Tatiana-Krivosheev/CollimationStudies"
    rc = subprocess.call(["git", "clone", repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    head, tail = os.path.split(repo)

    if rc != 0:
        return False

    rundir = os.path.join(top, target_dir)
    if not os.path.isdir(rundir):
        os.mkdir(target_dir)

    with temp_chdir(rundir):
        rc = subprocess.call(["cmake", "-DGeant4_DIR=" + path_to_g4,  os.path.join("..", tail)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if rc != 0:
            return False

        rc = subprocess.call(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if rc != 0:
            return False

    shutil.rmtree(tail)

    return True

def get_repo(target_dir):
    """
    Get python scripts from repository into the target dir
    """

    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)

    os.mkdir(target_dir)

    repo = "https://github.com/Kri-Ol/Geant4-on-GCE"
    rc = subprocess.call(["git", "clone", repo, target_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #repo = "https://192.168.1.230/svn/XCSW/MC_simulation/MC_phsp/Geant4onGCE"
    #rc = subprocess.call(["svn", "checkout", repo, target_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return rc

def main():
    """
    Building Docker image
    """

    # step 0 - pull ubuntu:15.04 from docker hub
    rc = subprocess.call(["docker", "pull", "ubuntu:15.04"], stderr=subprocess.PIPE)
    if rc != 0:
        raise RuntimeError("Unable to pull ubuntu:15.04 image")

    top = os.getcwd()
    print(top)

    # step 1 - copy Geant4
    path_to_g4 = copy_GEANT4(top)
    print(path_to_g4)

    # step 2 - get code from repository. NB! order is important
    rc = get_repo("run")
    if rc != 0:
        raise RuntimeError("Unable to clone repo")

    # step 3 - build application
    rc = make_runtime(top, path_to_g4, "run")
    if rc != True:
        raise RuntimeError("Unable to build run time")
        
    # step 4 - copy credentials
    rc = copy_creds(top, "run")

    # step last - builddocker image
    rc = subprocess.call(["docker", "build", "-t", "ubuntu:col",  "."], stderr=subprocess.PIPE)
    if rc != 0:
        raise RuntimeError("Unable to build docker image")

    return rc

if __name__ == '__main__':
    sys.exit(main())
