import subprocess
import sys
from utils.color_utils import ANSI
from utils.decorator import splitstmtadb
@splitstmtadb
def run_adb_command(command):
    try:
        result = subprocess.run(['adb'] + command.split(), capture_output=True, text=True)
        print(f"{ANSI.CYAN}\t{result.stdout}{ANSI.RESET}")
        if result.stderr:
            print(f"{ANSI.RED}Error: {result.stderr}{ANSI.RESET}", file=sys.stderr)
    except FileNotFoundError:
        print(f"{ANSI.RED}ADB is not installed or not in your PATH.{ANSI.RESET}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{ANSI.RED}An error occurred: {e}{ANSI.RESET}", file=sys.stderr)
        sys.exit(1)
@splitstmtadb
def run_adb_command_retn(command):
    try:
        result = subprocess.run(['adb'] + command.split(), capture_output=True, text=True)
        return result.stdout
    except FileNotFoundError:
        print(f"{ANSI.RED}ADB is not installed or not in your PATH.{ANSI.RESET}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{ANSI.RED}An error occurred: {e}{ANSI.RESET}", file=sys.stderr)
        sys.exit(1)
        return None

def list_devices():
    from ppadb.client import Client as AdbClient
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()
    for i, d in enumerate(devices):
            model = d.shell("getprop ro.product.model").strip()
            brand = d.shell("getprop ro.product.brand").strip()
            sdk = d.shell("getprop ro.build.version.sdk").strip()
            release = d.shell("getprop ro.build.version.release").strip()
            print(f"{ANSI.RED}[{i}]{ANSI.RESET}. {d.serial} - {ANSI.GREEN}{brand} {model}{ANSI.RESET} - {ANSI.YELLOW}{sdk}{ANSI.RESET} - {ANSI.BLUE}{release}{ANSI.RESET}")

def select_device():
        from ppadb.client import Client as AdbClient
        ## Connect to device
        client = AdbClient(host="127.0.0.1", port=5037)
        devices = client.devices()

        if not devices:
            raise RuntimeError("No devices connected")

        # In danh sách device
        print("Connected devices:")
        print("--------------------------------\n")
        for i, d in enumerate(devices):
            model = d.shell("getprop ro.product.model").strip()
            brand = d.shell("getprop ro.product.brand").strip()
            sdk = d.shell("getprop ro.build.version.sdk").strip()
            release = d.shell("getprop ro.build.version.release").strip()
            print(f"{ANSI.RED}[{i}]{ANSI.RESET}. {d.serial} - {ANSI.GREEN}{brand} {model}{ANSI.RESET} - {ANSI.YELLOW}{sdk}{ANSI.RESET} - {ANSI.BLUE}{release}{ANSI.RESET}")
        print(f"{ANSI.RED}[{len(devices)}]{ANSI.RESET}. Exit\n")
        # Cho user chọn
        while True:
            try:
                choice = int(input("Chọn thiết bị (số): "))
                if 0 <= choice <= len(devices):
                    if choice == len(devices):
                        print(f"{ANSI.GREEN}[+] Exit{ANSI.RESET}")
                        exit()
                    print("\n")
                    return devices[choice]
                else:
                    print("Số không hợp lệ, thử lại.")
            except ValueError:
                print("Nhập số thôi bạn ơi.")
                
def push_file_to_device(device, local_path, remote_path):
    device.push(local_path, remote_path)
    print(f"{ANSI.GREEN}[+] Pushed file to {remote_path} on {device.serial}{ANSI.RESET}")