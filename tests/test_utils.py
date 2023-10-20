import unittest
from envpicker.utils import split_version, matches_version
import packaging


class TestVersionUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.expectations = [
            {
                "entry": "python=3.7.1",
                "cond": {
                    "pkg": "python",
                    "min": "3.7.1",
                    "max": "3.7.1",
                    "wmin": True,
                    "wmax": True,
                    "vstring": "=3.7.1",
                },
            },
            {
                "entry": "numpy>=2",
                "cond": {
                    "pkg": "numpy",
                    "min": "2",
                    "max": None,
                    "wmin": True,
                    "wmax": False,
                    "vstring": ">=2",
                },
            },
            {
                "entry": "numpy2>2",
                "cond": {
                    "pkg": "numpy2",
                    "min": "2",
                    "max": None,
                    "wmin": False,
                    "wmax": False,
                    "vstring": ">2",
                },
            },
            {
                "entry": "numpy<=2,>1.5",
                "cond": {
                    "pkg": "numpy",
                    "min": "1.5",
                    "max": "2",
                    "wmin": False,
                    "wmax": True,
                    "vstring": "<=2,>1.5",
                },
            },
            {
                "entry": "numpy==1.15",
                "cond": {
                    "pkg": "numpy",
                    "min": "1.15",
                    "max": "1.15",
                    "wmin": True,
                    "wmax": True,
                    "vstring": "==1.15",
                },
            },
            {
                "entry": "django<3",
                "cond": {
                    "pkg": "django",
                    "min": None,
                    "max": "3",
                    "wmin": False,
                    "wmax": False,
                    "vstring": "<3",
                },
            },
            {
                "entry": "flask>=1,<2",
                "cond": {
                    "pkg": "flask",
                    "min": "1",
                    "max": "2",
                    "wmin": True,
                    "wmax": False,
                    "vstring": ">=1,<2",
                },
            },
            {
                "entry": "scipy>1.5,<=2.1",
                "cond": {
                    "pkg": "scipy",
                    "min": "1.5",
                    "max": "2.1",
                    "wmin": False,
                    "wmax": True,
                    "vstring": ">1.5,<=2.1",
                },
            },
            {
                "entry": "tensorflow==2.4",
                "cond": {
                    "pkg": "tensorflow",
                    "min": "2.4",
                    "max": "2.4",
                    "wmin": True,
                    "wmax": True,
                    "vstring": "==2.4",
                },
            },
        ]
        return super().setUp()

    def test_version_splitter(self):
        for exp in self.expectations:
            self.assertEqual(exp["cond"], split_version(exp["entry"]))

    def test_matches_version(self):
        assert matches_version(">=1.1", "1.1")
        assert not matches_version(">=1.1", "1.0")

        # Test basic matching with multiple criteria
        assert matches_version(">=1.1,<2.0", "1.5")
        assert not matches_version(">=1.1,<2.0", "2.0")

        # Edge cases where the version is exactly on the boundary
        assert matches_version(">=1.1", "1.1")
        assert not matches_version("<1.1", "1.1")
        assert not matches_version("<1.1,>1.2", "1.3")

        # Check against invalid version strings (shouldn't raise exceptions)
        with self.assertRaises(packaging.version.InvalidVersion):
            matches_version(">=1.1", "invalid_version")
        with self.assertRaises(ValueError):
            assert not matches_version("", "1.5")

        with self.assertRaises(packaging.specifiers.InvalidSpecifier):
            assert not matches_version("malformed", "1.5")
