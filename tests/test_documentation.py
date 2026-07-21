import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_readme_documents_both_installation_channels(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("pipx install frida-tool", readme)
        self.assertIn(
            'pipx install "git+https://github.com/toannguyen3107/Cli_Tool.git"',
            readme,
        )

    def test_release_guide_uses_token_environment_variable(self):
        release = (ROOT / "RELEASING.md").read_text(encoding="utf-8")
        self.assertIn("TWINE_PASSWORD", release)
        self.assertNotIn("pypi-AgEI", release)


if __name__ == "__main__":
    unittest.main()
