from utils.adb_utils import run_adb_command, select_device, push_file_to_device
from utils.run_command import run_command
from utils.color_utils import ANSI
from utils.decorator import header
import subprocess
import os
import shutil
import requests

from OpenSSL import crypto
import hashlib
import struct

# ------------------------------------------------------------------
# Hàm tính subject_hash_old (tương đương câu lệnh OpenSSL cũ)
# ------------------------------------------------------------------
def subject_hash_old(cert_pem_bytes: bytes) -> str:
    """
    Tính subject_name_hash theo phiên bản OpenSSL 1.x (MD5, little-endian)
    """
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem_bytes)

    # Lấy subject DN DER
    subject_der = cert.get_subject().der()

    # Tính MD5
    digest = hashlib.md5(subject_der).digest()

    # Lấy 4 byte đầu, chuyển sang little-endian
    hash32, = struct.unpack("<I", digest[:4])
    return f"{hash32:08x}"


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
def add_parser(subparsers):
    parser = subparsers.add_parser(
        "install_cert",
        help=f"Install a certificate with {ANSI.CYAN}ip{ANSI.RESET} and {ANSI.CYAN}port{ANSI.RESET}."
    )
    parser.add_argument("-p", "--path", default="toancert.der",
                        help="Path to the certificate file")
    parser.set_defaults(func=install_certificate)
    parser.add_argument("-H", "--host", type=str,
                        help="Host address for certificate download")
    parser.add_argument("-P", "--port", type=int,
                        help="Port number for certificate download")


@header
def install_certificate(args):
    # ----------------------------------------------------------
    # Download
    # ----------------------------------------------------------
    def download_certificate(host, port):
        try:
            url = f"http://{host}:{port}/cert"
            response = requests.get(url, timeout=10)
            return response.content
        except Exception as e:
            print(f"{ANSI.RED}Error downloading certificate: {e}{ANSI.RESET}")
            raise e


    
    
    cert = crypto.load_certificate(crypto.FILETYPE_ASN1, download_certificate(args.host, args.port))
    pem_bytes = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
    
 

    # Tính hash (tương đương: openssl x509 -inform PEM -subject_hash_old -in cim-cacert.pem |head -1)
    hash_name = subject_hash_old(pem_bytes)
    target_filename = f"{hash_name}.0"
    remote_path = f"/data/local/tmp/{target_filename}"
    # create device
    device = select_device()
    # ppadb push cần file, nên phải ghi file tạm
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(pem_bytes)
        tmp_path = tmp.name

    try:
        push_file_to_device(device, tmp_path, remote_path)
    finally:
        os.remove(tmp_path)

    print(f"{ANSI.GREEN}Created {target_filename} ({hash_name}.0){ANSI.RESET}")
    # Create folder user cert if don't exit
    try:
        output = device.shell("su -c 'mkdir -p /data/misc/user/0/cacerts-added'")
        print(f"{ANSI.GREEN}[+] Create folder if not exist /data/misc/user/0/cacerts-added on {device.serial} - {output}{ANSI.RESET}")
    except Exception as e:
        print(f"{ANSI.RED}Error creating folder /data/misc/user/0/cacerts-added on {device.serial}: {e}{ANSI.RESET}")
        raise e
    # Copy file to folder /data/misc/user/0/cacerts-added
    try:
        output = device.shell(f"su -c 'cp /data/local/tmp/{target_filename} /data/misc/user/0/cacerts-added/{target_filename}'")
        print(f"{ANSI.GREEN}[+] Copy {target_filename} to /data/misc/user/0/cacerts-added/{target_filename} on {device.serial} - {output}{ANSI.RESET}")
    except Exception as e:
        print(f"{ANSI.RED}Error copying {target_filename} to /data/misc/user/0/cacerts-added/{target_filename} on {device.serial}: {e}{ANSI.RESET}")
        raise e
    
    # Reboot the device
    inp = input(f"{ANSI.YELLOW}Please reboot the device to apply the changes. Type Y or N: {ANSI.RESET}")
    if inp.strip().upper() == "Y":
        output = device.shell("reboot")
        print(f"{ANSI.GREEN}[+] Reboot the device on {device.serial} - {output}{ANSI.RESET}")
        print(f"{ANSI.GREEN}Certificate installed successfully!{ANSI.RESET}")
    else:
        print(f"{ANSI.YELLOW}Reboot and check!{ANSI.RESET}")

