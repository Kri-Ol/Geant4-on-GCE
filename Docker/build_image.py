#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
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
    return path to the G4 setup
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

def make_runtime(top, path_to_g4):
    """
    Checkout the runtime code and build it 
    """

    # get the source code
    repo =  "https://github.com/Oleg-Krivosheev/G4DCM"
    rc = subprocess.call(["git", "clone", repo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    head, tail = os.path.split(repo)
    print(tail)

    if rc != 0:
        return False

    runplace = "run"    
    rundir = os.path.join(top, runplace)
    
    if os.path.isdir(rundir):
        shutil.rmtree(rundir)

    os.mkdir(rundir)
    with temp_chdir(rundir):
        rc = subprocess.call(["cmake", "-DGeant4_DIR=" + path_to_g4,  os.path.join("..", tail)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if rc != 0:
            return False
        
        rc = subprocess.call(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if rc != 0:
            return False

    return tail

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

    # step 2 - build application
    tail = make_runtime(top, path_to_g4)
    
    shutil.rmtree("G4DCM")    

    # step last - builddocker image
    rc = subprocess.call(["docker", "build", "-t", "ubuntu:col",  "."], stderr=subprocess.PIPE)
    if rc != 0:
        raise RuntimeError("Unable to build docker image")

if __name__ == '__main__':
    main()
