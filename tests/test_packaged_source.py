import ast
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAIRS = [
    (ROOT / "cli_tool.py", ROOT / "src/frida_tool/cli.py"),
    *[
        (path, ROOT / "src/frida_tool/commands" / path.name)
        for path in sorted((ROOT / "commands").glob("*.py"))
    ],
    *[
        (path, ROOT / "src/frida_tool/utils" / path.name)
        for path in sorted((ROOT / "utils").glob("*.py"))
    ],
]


class NormalizeAllowedPackagingChanges(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return ast.copy_location(
                ast.Constant(node.value.replace("frida_tool.commands.", "commands.")),
                node,
            )
        return node


def definitions(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tree = NormalizeAllowedPackagingChanges().visit(tree)
    return {
        node.name: ast.dump(
            ast.Module(body=node.body, type_ignores=[]),
            include_attributes=False,
        )
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


class PackagedSourceTests(unittest.TestCase):
    def test_packaged_modules_preserve_all_definition_bodies(self):
        for legacy, packaged in SOURCE_PAIRS:
            with self.subTest(module=legacy.name):
                self.assertTrue(packaged.is_file(), packaged)
                self.assertEqual(definitions(legacy), definitions(packaged))

    def test_packaged_cli_help_loads_all_commands(self):
        result = subprocess.run(
            [sys.executable, "-m", "frida_tool.cli", "--help"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in (
            "check_cert",
            "connect",
            "devices",
            "install_cert",
            "klfrida",
            "packages",
            "proxy",
            "reboot",
            "signapk",
        ):
            self.assertIn(command, result.stdout)


if __name__ == "__main__":
    unittest.main()
