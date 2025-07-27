from utils.color_utils import ANSI
from utils.decorator import header
from utils.adb_utils import run_adb_command

def add_parser(subparsers):
    parser = subparsers.add_parser("proxy", help="Manage proxy settings")
    subparsers = parser.add_subparsers()

    # Subparser for getting proxy settings
    get_parser = subparsers.add_parser("get", help="Get current proxy settings")
    get_parser.set_defaults(func=get_proxy)

    # Subparser for setting proxy settings
    set_parser = subparsers.add_parser("set", help="Set proxy settings. Syntax: proxy set <IP> <PORT>")
    set_parser.add_argument("-P", "--port", default="8080", help="Port to set the proxy server")
    set_parser.add_argument("-H", "--host", required=True, help="IP address to set the proxy server")
    set_parser.set_defaults(func=set_proxy)
    # Subparser for unsetting proxy settings
    unset_parser = subparsers.add_parser("unset", help="Unset proxy settings")
    unset_parser.set_defaults(func=unset_proxy)

@header
def get_proxy(args):
    """Retrieve current proxy settings."""
    run_adb_command("shell su -c 'settings get global http_proxy'")

@header
def set_proxy(args):
    """Set the proxy server."""
    if not args.host:
        print(f"{ANSI.YELLOW}[!]{ANSI.RESET}Please provide an IP address.")
        return
    proxy_settings = f"{args.host}:{args.port}"
    run_adb_command(f"shell su -c 'settings put global http_proxy {proxy_settings}'")

@header
def unset_proxy(args):
    """Unset the proxy server."""
    run_adb_command("shell su -c 'settings put global http_proxy :0'")
