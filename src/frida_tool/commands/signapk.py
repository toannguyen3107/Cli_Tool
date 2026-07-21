import os
from frida_tool.utils.color_utils import ANSI
from frida_tool.utils.run_command import run_command
from frida_tool.utils.decorator import header

def add_parser(subparsers):
    parser = subparsers.add_parser('signapk', help='Sign an APK file')
    parser.set_defaults(func=signapk)
    parser.add_argument("-af",'--apkfile', help='APK file to sign')
    parser.add_argument('--keystore', default="C:\\share\\tools\\MyHackingTools\\Frida-tool\\config\\my-release-key.keystore", help='Keystore file')
    parser.add_argument('--keypass', default="toannguyen", help='Key password')


@header
def signapk(args):
    """Sign an APK file."""
    if not args.apkfile:
        print(f"{ANSI.YELLOW}[!]{ANSI.RESET}Please provide an APK file to sign.")
        return
    if not os.path.exists(args.apkfile):
        print(f"{ANSI.YELLOW}[!]{ANSI.RESET}APK file not found.")
        return
    if not os.path.exists(args.keystore):
        print(f"{args.keystore}")
        print(f"{ANSI.YELLOW}[!]{ANSI.RESET}Keystore file not found.")
        return
    run_command(f"jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore {args.keystore} -storepass {args.keypass} {args.apkfile} alias_name")
