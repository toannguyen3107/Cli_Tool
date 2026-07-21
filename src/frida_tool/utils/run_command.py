import subprocess
from frida_tool.utils.color_utils import ANSI
import sys
from frida_tool.utils.decorator import splitstmt

@splitstmt
def run_command(command):
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True)
        print(f"{ANSI.MAGENTA}{result.stdout}{ANSI.RESET}")
        return result
    except FileNotFoundError:
        print("Command not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
