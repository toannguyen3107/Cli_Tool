from utils.adb_utils import run_adb_command, select_device
from utils.color_utils import ANSI
from utils.decorator import header
def add_parser(subparsers):
    parser = subparsers.add_parser("packages", help="List all installed packages")
    parser.set_defaults(func=list_installed_packages)
@header
def list_installed_packages(args):
    device = select_device()
    output = device.shell("pm list packages")
    for i, package in enumerate(output.split('\n')):
        package = package.strip()
        i += 1
        if package != "":
            package = package.split(':')
            package = package[1]
            print(f"{ANSI.GREEN}[{i}] {package}{ANSI.RESET}")
