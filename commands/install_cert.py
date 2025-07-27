from utils.adb_utils import run_adb_command
from utils.run_command import run_command
from utils.color_utils import ANSI
from utils.decorator import header
import subprocess
import os
import shutil
import requests

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import hashlib
import struct

# ------------------------------------------------------------------
# Hàm tính subject_hash_old (tương đương câu lệnh OpenSSL cũ)
# ------------------------------------------------------------------
def subject_hash_old(cert_pem_bytes: bytes) -> str:
    """
    Tính subject_name_hash theo phiên bản OpenSSL 1.x (MD5, little-endian)
    """
    cert = x509.load_pem_x509_certificate(cert_pem_bytes, default_backend())

    # Lấy subject DN DER
    subject_der = cert.subject.public_bytes()

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
    install_cert_folder = "install_cert"
    if not os.path.exists(install_cert_folder):
        os.makedirs(install_cert_folder)
        print(f"{ANSI.GREEN}Created '{install_cert_folder}' folder{ANSI.RESET}")
    else:
        print(f"{ANSI.YELLOW}'{install_cert_folder}' folder already exists{ANSI.RESET}")

    # ----------------------------------------------------------
    # Download
    # ----------------------------------------------------------
    def download_certificate(host, port):
        try:
            url = f"http://{host}:{port}/cert"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(f"{install_cert_folder}/toancert.der", "wb") as f:
                    f.write(response.content)
                print(f"{ANSI.GREEN}Certificate downloaded successfully as toancert.der{ANSI.RESET}")
                return True
            else:
                print(f"{ANSI.RED}Failed to download certificate. Status code: {response.status_code}{ANSI.RESET}")
                return False
        except requests.RequestException as e:
            print(f"{ANSI.RED}Error downloading certificate: {e}{ANSI.RESET}")
            return False

    # ----------------------------------------------------------
    if args.host and args.port:
        print(f"{ANSI.YELLOW}[+] Download cert from {args.host}:{args.port}{ANSI.RESET}")
        if not download_certificate(args.host, args.port):
            print(f"{ANSI.RED}Problem while downloading cert! Check host and port.{ANSI.RESET}")
            return
    else:
        print(f"{ANSI.YELLOW}[+] Find cert in folder {install_cert_folder}{ANSI.RESET}")

    # ----------------------------------------------------------
    # Kiểm tra tệp DER
    # ----------------------------------------------------------
    der_path = os.path.join(install_cert_folder, "toancert.der")
    if not os.path.isfile(der_path):
        print(f"{ANSI.RED}Error: toancert.der not found in {install_cert_folder} folder{ANSI.RESET}")
        return

    print(f"{ANSI.GREEN}toancert.der found in {install_cert_folder} folder{ANSI.RESET}")

    # ----------------------------------------------------------
    # Đọc DER → PEM (không cần OpenSSL CLI)
    # ----------------------------------------------------------
    with open(der_path, "rb") as f:
        cert_der = f.read()

    cert = x509.load_der_x509_certificate(cert_der, default_backend())
    pem_bytes = cert.public_bytes(encoding=serialization.Encoding.PEM)

    # Tính hash
    hash_name = subject_hash_old(pem_bytes)
    target_filename = f"{hash_name}.0"
    target_path = os.path.join(install_cert_folder, target_filename)

    # Ghi tệp <hash>.0: PEM + newline + DER gốc
    with open(target_path, "wb") as f:
        f.write(pem_bytes)
        f.write(b"\n")                       # newline
        f.write(cert_der)                    # thêm DER gốc để tương thích AOSP

    print(f"{ANSI.GREEN}Created {target_filename} ({hash_name}.0){ANSI.RESET}")

    # ----------------------------------------------------------
    # Push & install qua ADB
    # ----------------------------------------------------------
    run_adb_command(f"push {target_path} /data/local/tmp/")
    run_adb_command(
        f"shell su -c \"cp /data/local/tmp/{target_filename} /data/misc/user/0/cacerts-added/{target_filename}\""
    )

    # Dọn dẹp
    try:
        os.remove(target_path)
    except OSError:
        pass

    inp = input(f"{ANSI.YELLOW}Please reboot the device to apply the changes. Type Y or N: {ANSI.RESET}")
    if inp.strip().upper() == "Y":
        run_adb_command("reboot")
        print(f"{ANSI.GREEN}Certificate installed successfully!{ANSI.RESET}")
    else:
        print(f"{ANSI.YELLOW}Reboot and check!{ANSI.RESET}")

    # ----------------------------------------------------------
    # Xoá thư mục tạm
    # ----------------------------------------------------------
    if os.path.exists(install_cert_folder):
        try:
            shutil.rmtree(install_cert_folder)
            print(f"{ANSI.GREEN}Deleted '{install_cert_folder}' folder{ANSI.RESET}")
        except OSError as e:
            print(f"{ANSI.RED}Error deleting '{install_cert_folder}' folder: {e}{ANSI.RESET}")