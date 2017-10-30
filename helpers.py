# -*- coding: utf-8 -*-

def case2name(case):
    """
    Convert case into name
    """
    s = case.split(" ")
    s = [q for q in s if q] # remove empty strings
    return "_".join(s)


def case2pod(case):
    """
    Convert case into pod-compatible string
    """
    s = case.split(" ")
    s = [q for q in s if q] # remove empty strings
    return "-".join(s)


def case2args(case):
    """
    Parse case and Convert case into pod-compatible string
    """
    s = case.split(" ")
    s = [q for q in s if q] # remove empty strings
    s[0] += ".json"
    return s
