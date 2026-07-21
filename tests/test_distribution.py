import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DistributionMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tomllib.loads(
            (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )

    def test_setuptools_build_backend_is_declared(self):
        self.assertEqual(
            self.data["build-system"]["build-backend"],
            "setuptools.build_meta",
        )

    def test_console_script_targets_namespaced_cli(self):
        self.assertEqual(
            self.data["project"]["scripts"]["frida-tool"],
            "frida_tool.cli:main",
        )

    def test_packages_are_discovered_under_src(self):
        self.assertEqual(
            self.data["tool"]["setuptools"]["package-dir"],
            {"": "src"},
        )
        self.assertEqual(
            self.data["tool"]["setuptools"]["packages"]["find"]["where"],
            ["src"],
        )


if __name__ == "__main__":
    unittest.main()
