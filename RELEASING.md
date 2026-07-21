# Releasing Frida Tool

Publishing is a credentialed action. Run these steps only from a clean checkout
after reviewing the release contents. Never commit or paste a real PyPI token
into this repository.

## 1. Prepare the release

Update the version in `pyproject.toml`, commit it, and confirm the protected
keystore has not entered a build artifact:

```powershell
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*

@'
import glob
import tarfile
import zipfile

wheel = glob.glob("dist/*.whl")[0]
sdist = glob.glob("dist/*.tar.gz")[0]

with zipfile.ZipFile(wheel) as archive:
    assert not any(name.endswith(".keystore") for name in archive.namelist())

with tarfile.open(sdist) as archive:
    assert not any(name.endswith(".keystore") for name in archive.getnames())

print("Release artifacts contain no keystore files")
'@ | python -
```

## 2. Upload to TestPyPI

Create a TestPyPI API token, then keep it only in the process environment:

```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "<your-testpypi-api-token>"
python -m twine upload --repository testpypi dist/*
```

Verify the TestPyPI artifact in a temporary environment. The extra index is
needed because runtime dependencies are obtained from production PyPI:

```powershell
python -m venv .release-test
& .\.release-test\Scripts\python.exe -m pip install `
  --index-url https://test.pypi.org/simple/ `
  --extra-index-url https://pypi.org/simple/ `
  frida-tool
$env:PYTHONUTF8 = "1"
& .\.release-test\Scripts\frida-tool.exe --help
```

## 3. Upload to PyPI

Create a production PyPI project-scoped API token and replace the environment
value. Do not reuse the TestPyPI token:

```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "<your-pypi-api-token>"
python -m twine upload dist/*
```

Verify the public release:

```powershell
pipx install frida-tool
frida-tool --help
```

Unset the token when finished:

```powershell
Remove-Item Env:TWINE_PASSWORD
```

PyPI does not allow replacing an artifact for an existing version. Increment
the version in `pyproject.toml` and rebuild if a release must be corrected.
