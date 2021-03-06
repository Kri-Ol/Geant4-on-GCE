# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import subprocess
import time

import helpers

def make_cluster(CID, mach_type, nof_machs, ZID, disk_size, preempt = True):
    """
    Given machine type and # of machines, creates cluster

    Parameters
    ------------

    CID: string
        cluster id

    mach_type: string
        machine type

    nof_machs: integer
        number of machines

    ZID: string
        zone id

    disk_size: integer
        disk size in Gb

    preempt: boolean
        if True (default) make preemptible cluster, if False make standard one

    returns: integer
        return code from gcloud call
    """

    cmd = "gcloud container clusters create {0} --machine-type {1} --zone {3} --num-nodes {2} --disk-size={4} --no-enable-ip-alias".format(CID, mach_type, nof_machs, ZID, disk_size)
    if preempt:
        cmd = cmd + " --preemptible"

    rc = subprocess.call(cmd, shell=True)
    return rc


def auth_cluster(CID, ZID):
    """
    Given zone id and cluser id, make authentication

    Parameters
    ------------

    CID: string
        cluster ID

    ZID: string
        zone ID

    returns: integer
        return code from gcloud call
    """

    cmd = "gcloud container clusters get-credentials {0} --zone {1}".format(CID, ZID)
    rc = subprocess.call(cmd, shell=True)
    return rc


def read_template(template):
    """
    Read and return template file as JSON

    Parameters
    ------------

    template: string
        template name

    returns: dictionary
        JSON parsed as dictionary
    """
    data = None
    with open(template) as data_file:
        data = json.load(data_file)

    return data


def make_pod_from_template(temjson, case, docker2run):
    """
    Given JSON from template and case, make in-memory pod json

    Parameters
    ------------

    temjson: dictionary
        In-memory pod JSON

    case: string
        Case to compute name

    docker2run: string
        docker image to run

    returns: dictionary
        modified JSON suitable for computation
    """

    pod = helpers.case2pod( case )

    temjson["metadata"]["name"] = pod

    temjson["spec"]["containers"][0]["name"] = pod

    temjson["spec"]["containers"][0]["image"] = docker2run

    temjson["spec"]["containers"][0]["args"]  = helpers.case2args(case)

    return temjson


def make_json_pod(template, case, docker2run):
    """
    From template and case to calc, make appropriate pod JSON

    Parameters
    ------------

    template: string
        file name of the JSON template

    case: string
        Case to compute name

    docker2run: string
        docker image to run

    returns: dictionary
        modified JSON suitable for computation
    """
    temjson = read_template(template)
    outjson = make_pod_from_template(temjson, case, docker2run)

    fname = "pod" + "_" + helpers.case2name(case) + ".json"
    with open(fname, "w+") as f:
        f.write(json.dumps(outjson, indent=4))

    return fname


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
    with open(cfname) as data_file:
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


def main(cases_fname, nof_nodes, preempt = True):
    """
    This method creates a cluster, and then
    for a given cluster launches pods (one pod per case),
    which are read from input file

    Parameters
    ------------

    cases_fname: string
        file name which contains list of Cases to compute

    nof_nodes: integer
        number of the nodes in the cluster

    preempt: boolean
        If True make preemptable cluster
    """

    cfg = read_config("config_cluster.json")

    CID   = cfg["CID"]
    ZID   = cfg["ZID"]
    mtype = cfg["machine-type"]

    docker  = cfg["docker"]
    gcr     = cfg["gcr"]
    project = cfg["project"]

    print("From config_cluster.json:")
    print(CID, ZID, mtype, docker, gcr, project)

    print("Reading Cases list from {0}".format(cases_fname))

    cases = read_cases(cases_fname)

    print("To compute Cases: {0}".format(len(cases)))

    print("Making cluster with nodes: {0}".format(nof_nodes))

    rc = make_cluster(CID, mtype, nof_nodes, ZID, disk_size=30, preempt = preempt)
    if rc != 0:
        print("Cannot make cluster")
        sys.exit(1)

    rc = auth_cluster(CID, ZID)
    if rc != 0:
        print("Cannot make auth")
        sys.exit(1)

    docker2run = os.path.join(gcr, project, docker) # full path to docker

    for case in cases:
        pod_name = make_json_pod("colpod.json", case, docker2run)
        cmd = "kubectl create -f " + pod_name
        rc = 0
        for k in range(0, 3): # several attempts to make a pod
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
        print("Use: startCluster list_of_pods <# of nodes> <any value to make non-preemptable cluster>")
        print("Default machine is usually n1-highcpu-2 with 2CPUs, see config_cluster.json")
        sys.exit(1)

    cases_fname = None
    if nof_args >= 2:
        cases_fname = sys.argv[1]

    nof_nodes = -1 # default number of nodes
    if nof_args > 2:
        nof_nodes = int(sys.argv[2])

    preempt = True
    if nof_args > 3:
        preempt = False

    if nof_nodes < 1:
        print("Negative number of nodes")
        sys.exit(1)

    rc = main(cases_fname, nof_nodes, preempt)

    sys.exit(rc)
