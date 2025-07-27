from utils.adb_utils import run_adb_command
from utils.decorator import header
from utils.color_utils import ANSI

def add_parser(subparsers):
    parser = subparsers.add_parser("connect", help="Connect to device via ADB WiFi")
    parser.add_argument("-H", "--host", required=True, help="Host/IP address of the device")
    parser.add_argument("-P", "--port", default="5555", help="Port number (default: 5555)")
    parser.set_defaults(func=connect_wifi)

@header
def connect_wifi(args):
    """Connect to device via ADB WiFi."""
    if not args.host:
        print(f"{ANSI.YELLOW}[!]{ANSI.RESET}Please provide a host/IP address.")
        return
    
    # Create the connection string
    connection_string = f"{args.host}:{args.port}"
    
    print(f"{ANSI.YELLOW}[+] Attempting to connect to {connection_string}...{ANSI.RESET}")
    
    # Run the adb connect command
    run_adb_command(f"connect {connection_string}")
    
    print(f"{ANSI.GREEN}[+] Connection attempt completed.{ANSI.RESET}")
    print(f"{ANSI.CYAN}[INFO] Use 'python cli_tool.py devices' to verify the connection.{ANSI.RESET}")
