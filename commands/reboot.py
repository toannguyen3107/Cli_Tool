from utils.adb_utils import run_adb_command, select_device
def add_parser(subparsers):
    parser = subparsers.add_parser("reboot", help="Reboot the device")
    parser.set_defaults(func=reboot_device)

def reboot_device(args):
    device = select_device()
    device.shell("reboot")
