import unittest
from unittest.mock import patch, Mock
import hashlib
import os
import tempfile

from envpicker import CondaManager, MambaManager


# set os.environ["ENV_MANAGER_PATH"] = self.tempdir


class TestCondaManager(unittest.TestCase):
    def setUp(self):
        self.orig_env = os.environ.get("ENV_MANAGER_PATH")
        self.tempdir = tempfile.mkdtemp()
        os.environ["ENV_MANAGER_PATH"] = self.tempdir
        self.mock_env = {
            "hash": "mock_hash",
            "path": "/mock/path",
            "name": "mock_env",
            "py_executable": "/mock/path/python",
        }

    def tearDown(self):
        if self.orig_env:
            os.environ["ENV_MANAGER_PATH"] = self.orig_env
        else:
            del os.environ["ENV_MANAGER_PATH"]
        import shutil

        shutil.rmtree(self.tempdir)

    @patch("subprocess.check_output", return_value=b'{"key": "value"}')
    def test_init(self, mock_subprocess):
        manager = CondaManager()
        self.assertEqual(manager.condainfo, {"key": "value"})

    @patch("subprocess.check_output", side_effect=Exception("Error"))
    def test_is_available_false(self, mock_subprocess):
        self.assertFalse(CondaManager.is_available())

    @patch("subprocess.check_output", return_value=b"version info")
    def test_is_available_true(self, mock_subprocess):
        self.assertTrue(CondaManager.is_available())

    @patch("subprocess.check_output", return_value=b'{"envs": ["/path1"]}')
    @patch.object(CondaManager, "get_env_by_path", side_effect=[None, {}])
    @patch.object(CondaManager, "register_environment")
    def test_register_all(
        self, mock_register_env, mock_get_env_by_path, mock_subprocess
    ):
        manager = CondaManager()
        manager.register_all()
        mock_register_env.assert_called_once()

    def patched_out(x):
        if x[1] == "info":
            return b'{"envs": [] }'
        elif x[1] == "env" and x[2] == "export":
            return b"name: test\ndependencies:\n  - numpy==1.0\n  - pip:\n    - pandas==1.0"

    @patch(
        "subprocess.check_output",
        patched_out,
    )
    def test_get_dependencies(self):
        manager = CondaManager()
        deps = manager.get_dependencies(self.mock_env)

        self.assertIn("numpy==1.0", deps)
        self.assertIn("pandas==1.0", deps)


class TestMambaManager(TestCondaManager):
    def setUp(self):
        super().setUp()
        self.manager_cls = MambaManager
