#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess

def run(app, script):
    """
    """
    
    p = subprocess.Popen([app, script], stdin  = subprocess.PIPE,
                                        stdout = subprocess.PIPE, 
                                        stderr = subprocess.PIPE)
    out, err = p.communicate()
    
    fname = "LOG"
    with open(fname, "w") as the_file:
        the_file.write(out)
        
    return fname
    
def send(pack_name):
    """
    """
    
    rc = 1
    return rc
    
        
def main():
    """
    Run app
    """
    
    log = run("DICOM", "run.mac")

    rc = subprocess.Popen(["xz", log], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    
    fname = log + ".xz"
    
    rc = send(fname)
    
    return rc
    
if __name__ == '__main__':
    return main()
