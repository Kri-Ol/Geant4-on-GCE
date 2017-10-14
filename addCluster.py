# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import subprocess
import time

def case2name(case):
    """
    """
    s = case.split(" ")
    s = [q for q in s if q] # remove empty strings
    return "_".join(s)

def case2pod(case):
    """
    """
    s = case.split(" ")
    s = [q for q in s if q] # remove empty strings
    return "-".join(s)

def case2args(case):
    """
    """
    s = case.split(" ")
    s = [q for q in s if q] # remove empty strings
    s[0] += ".json"
    return s

def read_template(template):
    """
    read and return template file as JSON
    """
    data = None
    with open(template) as data_file:
        data = json.load(data_file)

    return data

def make_pod_from_template(temjson, case, docker2run):
    """
    given JSON from template and case, make in-memory pod json
    """

    pod = case2pod( case )

    temjson["metadata"]["name"] = pod

    temjson["spec"]["containers"][0]["name"] = pod

    temjson["spec"]["containers"][0]["image"] = docker2run

    temjson["spec"]["containers"][0]["args"]  = case2args(case)

    return temjson


def make_json_pod(template, case, docker2run):
    """
    from template and case to calc, make appropriate
    """

    temjson = read_template(template)
    outjson = make_pod_from_template(temjson, case, docker2run)

    fname = "pod" + "_" + case2name(case) + ".json"
    with open(fname, "w+") as f:
        f.write(json.dumps(outjson, indent=4))

    return fname

def read_config(ccfg):
    """
    read cluster configuration file from JSON
    """
    with open(ccfg) as data_file:
        data = json.load(data_file)
    return data

def read_cases(fname):
    if fname is None:
        return None

    lines = None
    with open(fname, "r+") as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]

    return lines

def main(cases_fname):
    """
    This method use existing cluster, and then
    for a given cluster launches pods (one pod per case),
    which are read from input file
    """

    if cases_fname is None:
        return -1

    cfg = read_config("config_cluster.json")

    CID   = cfg["CID"]
    ZID   = cfg["ZID"]
    mtype = cfg["machine-type"]

    docker  = cfg["docker"]
    gcr     = cfg["gcr"]
    project = cfg["project"]

    print("From config_cluster.json:")
    print(CID, ZID, mtype, docker, gcr, project)

    print("Reading cases list from {0}".format(cases_fname))

    cases = read_cases(cases_fname)

    print("To compute Cases: {0}".format(len(cases)))

    docker2run = os.path.join(gcr, project, docker) # full path to docker

    for case in cases:
        pod_name = make_json_pod("colpod.json", case, docker2run)
        cmd = "kubectl create -f " + pod_name
        rc = 0
        for k in range(0, 2): # several attempts to make a pod
            rc = subprocess.call(cmd, shell=True)
            if rc == 0:
                time.sleep(0.5)
                break

        if rc != 0:
            print("Cannot make case {0}".format(case))

    return 0

if __name__ =='__main__':
    nof_args = len(sys.argv)

    if nof_args == 1:
        print("Use: addCluster list_of_pods")
        sys.exit(1)

    cases_fname = None
    if nof_args >= 2:
        cases_fname = sys.argv[1]

    rc = main(cases_fname)

    sys.exit(rc)
