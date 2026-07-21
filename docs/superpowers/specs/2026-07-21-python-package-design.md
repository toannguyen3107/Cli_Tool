# Frida Tool Python Package Design

## Goal

Make Frida Tool installable and runnable as a standard Python command-line
application through both PyPI and a Git repository URL.

## Supported installation paths

After release to PyPI:

```powershell
pipx install frida-tool
frida-tool devices
```

Directly from a Git repository:

```powershell
pipx install "git+https://github.com/<owner>/<repository>.git"
frida-tool devices
```

`pip install frida-tool` will also install the package into an active Python
environment. Batch files and `uv` remain optional developer conveniences, not
runtime requirements for the installed CLI.

## Architecture

Move runtime source code to a `src/frida_tool/` package:

```text
src/frida_tool/
  __init__.py
  cli.py
  commands/
  utils/
```

The CLI discovers command modules from `frida_tool.commands` rather than from
paths relative to a top-level script. Imports use the `frida_tool` namespace so
the installed wheel works from any current working directory.

`pyproject.toml` will use the setuptools build backend and declare the console
script entry point:

```toml
[project.scripts]
frida-tool = "frida_tool.cli:main"
```

## Packaging and releases

The project metadata, dependencies, package discovery, and build configuration
live in `pyproject.toml`. `python -m build` produces a wheel and source archive
in `dist/`; both contain the namespace package and its command modules.

README installation and usage instructions will cover PyPI, Git installation,
and local development. A release guide will document the user-controlled PyPI
steps: create a PyPI account/token, build artifacts, upload to TestPyPI/PyPI,
then verify installation in a fresh `pipx` environment.

## Error handling and compatibility

The `frida-tool` command continues to display argparse help when invoked
without a subcommand and preserves existing command names and arguments. All
legacy source files and launch scripts remain untouched for compatibility. The
packaged source may change only import paths and module-discovery paths; all
existing function and class bodies must remain equivalent to their legacy
counterparts.

The existing keystore stays in the repository unchanged but is excluded from
distribution artifacts because publishing private signing material to PyPI
would be unsafe. Commands that require external tools, Android root access, or
a keystore retain their existing arguments and behavior.

## Verification

Tests will verify the console entry point is declared and that package build
artifacts are created. A clean temporary virtual environment will install the
built wheel and execute `frida-tool --help`, verifying that command discovery
works outside the checkout. Existing command behavior is exercised through the
CLI help path without requiring a connected Android device.

## Scope

This change prepares the repository for distribution. It does not create a PyPI
account, upload a release, create a GitHub repository, or publish artifacts;
those actions require credentials and explicit user authorization.
