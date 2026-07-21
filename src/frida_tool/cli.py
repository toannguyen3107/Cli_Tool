import argparse
import pkgutil
import os
import importlib
from frida_tool.utils.color_utils import ANSI
BANNER = f"""
    {ANSI.CYAN}==================================================================================

▄▄▄█████▓ ▒█████  ▄▄▄      ███▄    █     ███▄    █   ▄████  █    ██▓██   ██▓▓█████ ███▄    █ 
▓  ██▒ ▓▒▒██▒  ██▒████▄    ██ ▀█   █     ██ ▀█   █  ██▒ ▀█▒ ██  ▓██▒▒██  ██▒▓█   ▀ ██ ▀█   █ 
▒ ▓██░ ▒░▒██░  ██▒██  ▀█▄ ▓██  ▀█ ██▒   ▓██  ▀█ ██▒▒██░▄▄▄░▓██  ▒██░ ▒██ ██░▒███  ▓██  ▀█ ██▒
░ ▓██▓ ░ ▒██   ██░██▄▄▄▄██▓██▒  ▐▌██▒   ▓██▒  ▐▌██▒░▓█  ██▓▓▓█  ░██░ ░ ▐██▓░▒▓█  ▄▓██▒  ▐▌██▒
  ▒██▒ ░ ░ ████▓▒░▓█   ▓██▒██░   ▓██░   ▒██░   ▓██░░▒▓███▀▒▒▒█████▓  ░ ██▒▓░░▒████▒██░   ▓██░
  ▒ ░░   ░ ▒░▒░▒░ ▒▒   ▓▒█░ ▒░   ▒ ▒    ░ ▒░   ▒ ▒  ░▒   ▒ ░▒▓▒ ▒ ▒   ██▒▒▒ ░░ ▒░ ░ ▒░   ▒ ▒ 
    ░      ░ ▒ ▒░  ▒   ▒▒ ░ ░░   ░ ▒░   ░ ░░   ░ ▒░  ░   ░ ░░▒░ ░ ░ ▓██ ░▒░  ░ ░  ░ ░░   ░ ▒░
  ░      ░ ░ ░ ▒   ░   ▒     ░   ░ ░       ░   ░ ░ ░ ░   ░  ░░░ ░ ░ ▒ ▒ ░░     ░     ░   ░ ░ 
             ░ ░       ░  ░        ░             ░       ░    ░     ░ ░        ░  ░        ░ 
                                                                    ░ ░                      
            Welcome to my hacking tool - v.1.0 - @Copyright by {ANSI.RED}Toan Nguyen{ANSI.RESET}{ANSI.CYAN}
    ==================================================================================
{ANSI.RESET}\n\n"""
def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="CLI tool to run specific jobs.")
    subparsers = parser.add_subparsers(dest="command", help=f"{ANSI.RED}Available commands{ANSI.RESET}")

    # dynamically load all modules in the commands package
    command_dir = os.path.join(os.path.dirname(__file__), 'commands')
    for _, module_name,_ in pkgutil.iter_modules([command_dir]):
        module = importlib.import_module(f'frida_tool.commands.{module_name}')
        module.add_parser(subparsers)
    
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
    
