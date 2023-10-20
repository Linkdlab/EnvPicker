import unittest
from unittest.mock import patch, Mock
import hashlib
import os
import tempfile


class TestUtilityFunctions(unittest.TestCase):
    def test_path_hash(self):
        from envpicker.manager.base import path_hash

        path = "test_path"

        expected_hash = hashlib.md5(path.encode()).hexdigest()
        self.assertEqual(path_hash(path), expected_hash)

    def test_is_package_entry(self):
        from envpicker.manager.base import is_package_entry

        self.assertTrue(is_package_entry("package==1.0"))
        self.assertTrue(is_package_entry("package>=1.0"))
        self.assertTrue(is_package_entry("package<1.0"))
        self.assertTrue(is_package_entry("package=*"))
        self.assertTrue(is_package_entry("packag>=3.1,<4"))
        self.assertTrue(is_package_entry("packag>=3.1,<=4"))
        self.assertFalse(is_package_entry("package="))
        self.assertFalse(is_package_entry("package"))
        self.assertFalse(is_package_entry("package 1.0"))
        self.assertFalse(is_package_entry("package\n==1.0"))
        self.assertFalse(is_package_entry("package ==1.0"))
        self.assertFalse(is_package_entry(12345))


class TestBaseEnvManager(unittest.TestCase):
    def setUp(self) -> None:
        from envpicker.manager.base import (
            BaseEnvManager,
        )
        from wrapconfig import InMemoryConfig
        import envpicker.manager.base as evm_base

        self.tempdir = tempfile.mkdtemp()

        mock_env = {
            "hash": "mock_hash",
            "path": os.path.normpath(
                os.path.abspath(os.path.join(self.tempdir, "mock", "path"))
            ),
            "name": "mock_env",
            "py_executable": os.path.normpath(
                os.path.abspath(os.path.join(self.tempdir, "mock", "path", "python"))
            ),
        }
        with patch.object(evm_base.os.path, "isdir", return_value=True), patch.object(
            evm_base, "YAMLWrapConfig", InMemoryConfig
        ):

            class MockBaseEnvManager(BaseEnvManager):
                @classmethod
                def is_available(cls):
                    return True

                @classmethod
                def register_all(cls):
                    pass

                def get_dependencies(self, env):
                    return []

            self.MockBaseEnvManager = MockBaseEnvManager
            self.manager = self.MockBaseEnvManager(
                path=os.path.join(self.tempdir, "mock", "path")
            )
            with patch.object(
                self.MockBaseEnvManager, "validate_env", return_value=True
            ):
                self.manager.environments = [mock_env]
            self.mock_env = mock_env
            return super().setUp()

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tempdir)
        return super().tearDown()

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isdir", return_value=False)
    def test_init_raises_error_for_non_directory(self, mock_isdir, mock_exists):
        with self.assertRaises(FileExistsError):
            self.MockBaseEnvManager()

    @patch("os.path.isfile", return_value=True)
    @patch(
        "builtins.open",
        new_callable=unittest.mock.mock_open,
        read_data="name: test\ndependencies:\n  - numpy",
    )
    def test_env_to_full_env(self, mock_open, mock_isfile):
        env = {
            "hash": "test_hash",
            "path": os.path.join(self.tempdir, "test", "path"),
            "name": "test_env",
            "py_executable": os.path.join(self.tempdir, "test", "path", "python"),
        }

        full_env = self.manager.env_to_full_env(env)
        self.assertIn("envdata", full_env)
        self.assertEqual(full_env["envdata"]["name"], "test")
        self.assertIn("numpy", full_env["envdata"]["dependencies"])

    @patch("os.path.isdir", return_value=False)
    def test_validate_env_invalid_path(self, mock_isdir):
        with self.assertRaises(FileNotFoundError):
            self.manager.validate_env(self.mock_env)

    @patch("os.path.isfile", return_value=False)
    def test_validate_env_invalid_py_executable(self, mock_isfile):
        with self.assertRaises(FileNotFoundError):
            self.manager.validate_env(self.mock_env)

    def test_validate_env_invalid_hash(self):
        with self.assertRaises(FileNotFoundError):
            self.manager.validate_env(self.mock_env)

    def test_get_env_by_path(self):
        with patch.object(self.manager, "env_to_full_env", lambda x: x):
            retrieved_env = self.manager.get_env_by_path(
                os.path.join(self.tempdir, "mock", "path")
            )
            self.assertEqual(retrieved_env["name"], "mock_env")

    @patch("os.path.isdir", return_value=True)
    @patch("subprocess.check_output", return_value=b"Python 3.9.1")
    def test_register_environment(self, mock_check_output, mock_isdir):
        with patch.object(
            self.MockBaseEnvManager, "validate_env", return_value=True
        ) as mock_validate_env:
            env = self.manager.register_environment(
                path=os.path.join(self.tempdir, "test", "path"), name="test_env"
            )
            self.assertEqual(env["name"], "test_env")
            self.assertEqual(
                env["path"],
                os.path.normpath(
                    os.path.abspath(os.path.join(self.tempdir, "test", "path"))
                ),
            )
            mock_validate_env.assert_called_with(
                {k: v for k, v in env.items() if k != "envdata"}
            )

    @patch("os.path.isdir", return_value=True)
    @patch("os.path.isfile", return_value=True)
    def test_environments_setter(self, mock_isfile, mock_isdir):
        with patch.object(
            self.manager, "registry", return_value=[self.mock_env]
        ) as mock_registry:
            new_env = {
                "hash": "new_hash",
                "path": os.path.join(self.tempdir, "new", "path"),
                "name": "new_env",
                "py_executable": os.path.join(self.tempdir, "new", "path", "python"),
            }

            self.manager.environments = [new_env]
            mock_registry.set.assert_called_once_with("environments", [new_env])

    @patch("os.path.isdir", return_value=True)
    @patch("os.path.isfile", return_value=True)
    def test_add_env(self, mock_isfile, mock_isdir):
        self.manager.environments = []
        env = self.manager.add_env(
            path=os.path.join(self.tempdir, "test", "path2"),
            py_executable=os.path.join(self.tempdir, "test", "path2", "python"),
            name="test_env2",
        )
        self.assertEqual(env["name"], "test_env2")
        self.assertEqual(
            env["path"],
            os.path.normpath(
                os.path.abspath(os.path.join(self.tempdir, "test", "path2"))
            ),
        )

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_create_env_yaml(self, mock_open):
        self.manager.create_env_yaml(self.mock_env)
        mock_open.assert_called_once_with(
            os.path.join(self.manager.path, "mock_hash.yaml"), "w"
        )


class TestFindEnvManager(unittest.TestCase):
    def test_basic_finder(self):
        from envpicker import get_manager

        mgr = get_manager()
        self.assertTrue(mgr.is_available())

    def test_preference_order(self):
        from envpicker import get_manager

        mgr = get_manager(preferences=["conda", "mamba", "venv"])
        self.assertTrue(mgr.is_available())

    def test_preference_order_not_available(self):
        from envpicker import get_manager

        with self.assertRaises(RuntimeError):
            mgr = get_manager(preferences=["dummy"])
