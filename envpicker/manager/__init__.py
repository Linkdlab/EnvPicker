from __future__ import annotations
from typing import Optional
from .conda_mngr import CondaManager, MambaManager
from .base import BaseEnvManager
from ..logger import ENVPICKER_LOGGER

PREFERENCE_ORDER = [
    "mamba",
    "conda",
    #   "poetry",
    "venv",
]


_MANAGER_CLASSES = {
    "conda": CondaManager if CondaManager.is_available() else None,
    "mamba": MambaManager if MambaManager.is_available() else None,
    #    "poetry": PoetryManager,
    #    "venv": VenvManager,
}


def get_manager(
    path: Optional[str] = None, preferences: Optional[list[str]] = None
) -> BaseEnvManager:
    """Return the first available manager."""
    if preferences is None:
        preferences = PREFERENCE_ORDER

    ENVPICKER_LOGGER.debug("Getting manager from %s", preferences)
    for manager in preferences:
        if manager in _MANAGER_CLASSES and _MANAGER_CLASSES[manager] is not None:
            ENVPICKER_LOGGER.info(f"Using %s as environment manager.", manager)
            return _MANAGER_CLASSES[manager](path=path)
    raise RuntimeError("No available environment managers found.")
