from __future__ import annotations

import xml.etree.ElementTree as ET

import numpy as np


def age_group_bounds(xml: str) -> np.ndarray:
    root = ET.fromstring(xml)
    age_group = root.find(".//monitoring/ageGroup")
    if age_group is None:
        raise ValueError("scenario has no monitoring/ageGroup element")
    upperbounds = [float(g.attrib["upperbound"]) for g in age_group.findall("group")]
    return np.array([float(age_group.attrib["lowerbound"]), *upperbounds])


def age_group_upperbounds(xml: str) -> np.ndarray:
    return age_group_bounds(xml)[1:]


def age_group_midpoints(xml: str) -> np.ndarray:
    bounds = age_group_bounds(xml)
    return (bounds[:-1] + bounds[1:]) / 2


def age_group_labels(upperbounds: np.ndarray, lowerbound: float = 0.0) -> list[str]:
    labels = []
    lb = lowerbound
    for ub in upperbounds:
        labels.append(f"{lb:g}-{ub:g}")
        lb = ub
    return labels
