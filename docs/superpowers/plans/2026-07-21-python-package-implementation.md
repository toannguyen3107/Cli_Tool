# Frida Tool Python Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing CLI installable from PyPI or Git with `pipx`/`pip` while preserving every existing business-function body and every legacy source file.

**Architecture:** Add a `src/frida_tool` namespace package containing logic-preserving copies of the current CLI, command, and utility modules. Only import paths and command-module discovery change inside the packaged copies; the existing top-level files remain untouched as compatibility sources. Setuptools builds the namespace package and exposes `frida-tool = frida_tool.cli:main`.

**Tech Stack:** Python 3.12+, setuptools, argparse, unittest, `build`, pip/pipx

## Global Constraints

- Do not delete or modify `cli_tool.py`, any file under `commands/`, any file under `utils/`, `mcp_server.py`, or `config/my-release-key.keystore`.
- Preserve every class and function body from the legacy runtime modules in the packaged copies; only module import paths and package discovery expressions may change.
- Do not package or publish `config/my-release-key.keystore`; it may contain private signing material.
- Preserve all command names, parser arguments, defaults, output text, encryption/certificate behavior, ADB behavior, signing behavior, and MCP behavior.
- Keep the existing project version `1.0.0`, Python floor `>=3.12`, and runtime dependency declarations unchanged.
- The installed CLI must run from outside the repository without requiring `uv`, a batch file, or the repository as its current working directory.

---

### Task 1: Add regression guards and the namespace package

**Files:**
- Create: `tests/test_packaged_source.py`
- Create: `tests/__init__.py`
- Create: `src/frida_tool/__init__.py`
- Create: `src/frida_tool/cli.py`
- Create: `src/frida_tool/commands/__init__.py`
- Create: `src/frida_tool/commands/connect_wifi.py`
- Create: `src/frida_tool/commands/devices.py`
- Create: `src/frida_tool/commands/install_cert.py`
- Create: `src/frida_tool/commands/klfrida.py`
- Create: `src/frida_tool/commands/packages.py`
- Create: `src/frida_tool/commands/proxy.py`
- Create: `src/frida_tool/commands/reboot.py`
- Create: `src/frida_tool/commands/signapk.py`
- Create: `src/frida_tool/utils/__init__.py`
- Create: `src/frida_tool/utils/adb_utils.py`
- Create: `src/frida_tool/utils/color_utils.py`
- Create: `src/frida_tool/utils/decorator.py`
- Create: `src/frida_tool/utils/run_command.py`

**Interfaces:**
- Consumes: Existing public functions and classes from `cli_tool.py`, `commands/*.py`, and `utils/*.py`.
- Produces: `frida_tool.cli.main()`, `frida_tool.commands.*`, and `frida_tool.utils.*` with function bodies equivalent to the legacy modules.

- [ ] **Step 1: Write the failing source-preservation tests**

Create `tests/test_packaged_source.py` with AST-based comparisons. Function and class bodies must remain identical even though imports are namespaced:

```python
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
        node.name: ast.dump(ast.Module(body=node.body, type_ignores=[]), include_attributes=False)
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
            "connect", "devices", "install_cert", "klfrida", "packages",
            "proxy", "reboot", "signapk",
        ):
            self.assertIn(command, result.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `python -m unittest tests.test_packaged_source -v`

Expected: FAIL because `src/frida_tool/cli.py` and packaged modules do not exist.

- [ ] **Step 3: Add package markers and logic-preserving module copies**

Create empty `__init__.py` files in `tests/`, `src/frida_tool/`, `src/frida_tool/commands/`, and `src/frida_tool/utils/`.

Copy the complete content of each legacy module to its paired packaged path. Apply only these exact import transformations in packaged files:

```text
from utils.                 -> from frida_tool.utils.
import_module('commands.    -> import_module('frida_tool.commands.
```

In `src/frida_tool/cli.py`, replace the filesystem discovery expression only:

```python
command_dir = os.path.join(os.path.dirname(__file__), 'commands')
```

The rest of every function/class body remains byte-for-byte equivalent to its legacy counterpart, which the AST regression test enforces.

- [ ] **Step 4: Run the source-preservation tests and verify GREEN**

Run: `python -m unittest tests.test_packaged_source -v`

Expected: 2 tests PASS, including `frida_tool.cli --help` command discovery.

- [ ] **Step 5: Confirm protected legacy files were not modified**

Run:

```powershell
git diff --exit-code -- cli_tool.py mcp_server.py commands utils config/my-release-key.keystore
```

Expected: exit code 0 with no output.

- [ ] **Step 6: Commit the namespace package and regression guards**

```powershell
git add tests/__init__.py tests/test_packaged_source.py src/frida_tool
git commit -m "feat: add installable frida tool package"
```

### Task 2: Configure standards-based builds and test the installed command

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/test_distribution.py`

**Interfaces:**
- Consumes: `frida_tool.cli.main()` from Task 1.
- Produces: A setuptools wheel/sdist and the console entry point `frida-tool`.

- [ ] **Step 1: Write the failing distribution metadata tests**

Create `tests/test_distribution.py`:

```python
import sys
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DistributionMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

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
        self.assertEqual(self.data["tool"]["setuptools"]["package-dir"], {"": "src"})
        self.assertEqual(self.data["tool"]["setuptools"]["packages"]["find"]["where"], ["src"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run metadata tests and verify RED**

Run: `python -m unittest tests.test_distribution -v`

Expected: ERROR for missing `build-system`, and FAIL because the current entry point is `cli_tool:main`.

- [ ] **Step 3: Add minimal setuptools configuration**

Add the following without changing the existing project metadata, version, Python requirement, or dependency list:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = {"" = "src"}
include-package-data = false

[tool.setuptools.packages.find]
where = ["src"]
```

Change only the console target:

```toml
[project.scripts]
frida-tool = "frida_tool.cli:main"
```

- [ ] **Step 4: Run metadata and source tests and verify GREEN**

Run: `python -m unittest discover -s tests -v`

Expected: 5 tests PASS.

- [ ] **Step 5: Build wheel and source distribution**

Run: `python -m build`

Expected: exit code 0 and one `.whl` plus one `.tar.gz` under `dist/`.

- [ ] **Step 6: Verify the wheel excludes protected signing material**

Run:

```powershell
@'
import glob, zipfile
wheel = glob.glob('dist/*.whl')[0]
with zipfile.ZipFile(wheel) as archive:
    names = archive.namelist()
assert not any(name.endswith('.keystore') for name in names), names
assert 'frida_tool/commands/install_cert.py' in names
assert 'frida_tool/commands/signapk.py' in names
print(f'verified {wheel}: {len(names)} files, no keystore')
'@ | python -
```

Expected: assertion-free output ending in `no keystore`.

- [ ] **Step 7: Install the wheel in a clean temporary virtual environment**

Run:

```powershell
$packageTestDir = Join-Path ([IO.Path]::GetTempPath()) ("frida-tool-wheel-test-" + [guid]::NewGuid())
python -m venv $packageTestDir
& "$packageTestDir\Scripts\python.exe" -m pip install --disable-pip-version-check (Get-ChildItem dist\*.whl | Select-Object -First 1).FullName
& "$packageTestDir\Scripts\frida-tool.exe" --help
```

Expected: installation succeeds and help lists all eight commands. The temporary path is explicitly scoped under `$env:TEMP` before removal.

- [ ] **Step 8: Commit the build configuration**

```powershell
git add pyproject.toml tests/test_distribution.py
git commit -m "build: configure setuptools distribution"
```

### Task 3: Document PyPI and Git installation without changing runtime behavior

**Files:**
- Modify: `README.md`
- Create: `RELEASING.md`
- Create: `tests/test_documentation.py`

**Interfaces:**
- Consumes: Built distribution and `frida-tool` console script from Task 2.
- Produces: Copy-paste installation and credential-safe release instructions.

- [ ] **Step 1: Write the failing documentation test**

Create `tests/test_documentation.py`:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_readme_documents_both_installation_channels(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("pipx install frida-tool", readme)
        self.assertIn("pipx install \"git+https://github.com/", readme)

    def test_release_guide_uses_token_environment_variable(self):
        release = (ROOT / "RELEASING.md").read_text(encoding="utf-8")
        self.assertIn("TWINE_PASSWORD", release)
        self.assertNotIn("pypi-AgEI", release)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run documentation tests and verify RED**

Run: `python -m unittest tests.test_documentation -v`

Expected: FAIL because the two `pipx` commands are absent and `RELEASING.md` does not exist.

- [ ] **Step 3: Update installation documentation**

Document these exact user flows in `README.md`:

```powershell
# Published release from PyPI
pipx install frida-tool

# Direct installation from GitHub
pipx install "git+https://github.com/<owner>/<repository>.git"

# Verify
frida-tool --help
frida-tool devices
```

Retain the current command reference and MCP documentation. Explain that ADB,
Frida server binaries, `jarsigner`, Android root access, and a user-supplied
keystore remain external prerequisites for commands that use them.

- [ ] **Step 4: Add credential-safe release instructions**

Create `RELEASING.md` with these commands and no real token or credential:

```powershell
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "<your-pypi-api-token>"
python -m twine upload dist/*
```

Include a TestPyPI verification step before production PyPI and note that
`config/my-release-key.keystore` must never appear in build artifacts.

- [ ] **Step 5: Run documentation tests and verify GREEN**

Run: `python -m unittest discover -s tests -v`

Expected: 7 tests PASS.

- [ ] **Step 6: Commit the documentation**

```powershell
git add README.md RELEASING.md tests/test_documentation.py
git commit -m "docs: add pipx and PyPI release guide"
```

### Task 4: Final regression and artifact verification

**Files:**
- Verify only; no production source changes expected.

**Interfaces:**
- Consumes: All earlier tasks.
- Produces: Evidence that legacy logic is unchanged and installed artifacts work.

- [ ] **Step 1: Run the complete test suite**

Run: `python -m unittest discover -s tests -v`

Expected: 7 tests PASS, 0 failures, 0 errors.

- [ ] **Step 2: Rebuild artifacts from current source**

Run: `python -m build`

Expected: exit code 0 and current wheel/sdist artifacts.

- [ ] **Step 3: Re-run protected-file and artifact checks**

Run:

```powershell
git diff --exit-code 78dfb4f -- cli_tool.py mcp_server.py commands utils config/my-release-key.keystore
@'
import glob, zipfile
wheel = glob.glob('dist/*.whl')[0]
with zipfile.ZipFile(wheel) as archive:
    names = archive.namelist()
assert not any(name.endswith('.keystore') for name in names), names
assert 'frida_tool/cli.py' in names
print(wheel)
'@ | python -
```

Expected: no protected legacy source diff and no keystore in the wheel.

- [ ] **Step 4: Inspect final repository changes**

Run: `git status --short` and `git log --oneline -4`.

Expected: only planned source/package/test/documentation/build files are changed or committed; no unrelated user files are touched.
