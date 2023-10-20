from typing import List, Dict, Any, TypedDict
import re
from packaging.specifiers import SpecifierSet


class PackageVersionCondition(TypedDict):
    pkg: str
    min: str
    max: str
    wmin: bool
    wmax: bool
    vstring: str


def split_version(w) -> PackageVersionCondition:
    version_indicator = re.compile(r"([<>=]+)")
    # split before the version indicator
    sp = version_indicator.split(w, 1)
    if len(sp) == 1:
        sp.extend([">=", "0"])

    pkg, version_indicator, version = sp

    version = version_indicator + version
    conditions = version.split(",")
    min_version = None
    max_version = None
    wmin = False
    wmax = False

    for c in conditions:
        if c.startswith(">="):
            min_version = c[2:]
            wmin = True
        elif c.startswith("<="):
            max_version = c[2:]
            wmax = True
        elif c.startswith(">"):
            min_version = c[1:]
        elif c.startswith("<"):
            max_version = c[1:]
        elif c.startswith("=="):
            min_version = c[2:]
            max_version = c[2:]
            wmin = True
            wmax = True
        elif c.startswith("="):
            min_version = c[1:]
            max_version = c[1:]
            wmin = True
            wmax = True

        else:
            raise ValueError(f"Invalid version specifier {c}")

    return PackageVersionCondition(
        pkg=pkg, min=min_version, max=max_version, wmin=wmin, wmax=wmax, vstring=version
    )


def matches_version(lookup: str, current: str) -> bool:
    """
    Checks if the given current version matches the specified lookup version range.

    Args:
    - lookup (str): The version range to look up, e.g., ">=1.1,<2.0".
    - current (str): The current version to check, e.g., "1.5".

    Returns:
    - bool: True if the current version matches the lookup range, False otherwise.
    """
    lookup = lookup.strip()
    current = current.strip()

    while current.startswith("="):
        current = current[1:]
    if not lookup:
        raise ValueError("Lookup version cannot be empty")
    if not current:
        raise ValueError("Current version cannot be empty")

    specifier_req = SpecifierSet(lookup)

    return specifier_req.contains(current)
