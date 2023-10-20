from __future__ import annotations
from typing import Optional
from .base import BaseEnvManager, EnvExistsError, EnvironmentEntry, is_package_entry
import subprocess
import json
import os
import yaml
from ..logger import ENVPICKER_LOGGER


class CondaManager(BaseEnvManager):
    CONDACMD = "conda"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.condainfo = json.loads(
            subprocess.check_output([self.CONDACMD, "info", "--json"]).decode("utf-8")
        )

    @classmethod
    def is_available(cls) -> bool:
        try:
            _ = subprocess.check_output([cls.CONDACMD, "--version"])
            return True
        except Exception:
            return False

    def register_all(self) -> None:
        """Register all available environments."""

        env_list_output = subprocess.check_output(
            [self.CONDACMD, "env", "list", "--json"]
        )
        env_list_json = json.loads(env_list_output.decode("utf-8"))
        environments = env_list_json["envs"]
        r = 0
        for env_path in environments:
            env = self.get_env_by_path(env_path)
            if env:
                continue

            env_name = os.path.basename(
                env_path
            )  # by default, use the name of the directory as the environment name

            # Register the environment using add_env function
            try:
                self.register_environment(
                    path=env_path,
                    py_executable=None,
                    name=env_name,
                    force=False,
                )
                ENVPICKER_LOGGER.info(
                    "Successfully registered %s (%s)", env_name, env_path
                )
                r += 1
            except EnvExistsError:
                continue
        ENVPICKER_LOGGER.info("Successfully registered %s environments.", r)

    def get_dependencies(self, env: EnvironmentEntry):
        yaml_string = subprocess.check_output(
            [
                self.CONDACMD,
                "env",
                "export",
                "--no-builds",
                "-p",
                env["path"],
            ]
        )
        yaml_string = yaml_string.decode("utf-8")
        data = yaml.safe_load(yaml_string)
        deps = []
        for entry in data["dependencies"]:
            if is_package_entry(entry):
                deps.append(entry)
            elif isinstance(entry, dict):
                if "pip" in entry:
                    for pip_entry in entry["pip"]:
                        if is_package_entry(pip_entry):
                            deps.append(pip_entry)

        return deps


class MambaManager(CondaManager):
    CONDACMD = "mamba"
