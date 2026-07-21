from utils.adb_utils import run_adb_command, select_device
from utils.decorator import header
from OpenSSL import crypto
def add_parser(subparsers):
    parser = subparsers.add_parser("check_cert", help="Check device certificates with md5sum")
    parser.set_defaults(func=check_cert)
    parser.add_argument("-H", "--host", type=str, help="Host address for certificate download")
    parser.add_argument("-P", "--port", type=int, help="Port number for certificate download")
    parser.add_argument("-F", "--file", type=str, help="Path to local certificate file", default="9a5ba575.0")
@header
def check_cert(args):
    device = select_device()
    print(f"Checking certificates on device {device.serial}...")
    cert_paths = {
        "user": "/data/misc/keychain/cacerts-added",
        "system": "/system/etc/security/cacerts"
    }
    def download_certificate(host, port):
        import requests
        try:
            url = f"http://{host}:{port}/cert"
            response = requests.get(url, timeout=10)
            return response.content
        except Exception as e:
            print(f"Error downloading certificate: {e}")
            return None
    
    cert = crypto.load_certificate(crypto.FILETYPE_ASN1, download_certificate(args.host, args.port))
    pem_bytes = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
    import hashlib
    md5_hash = hashlib.md5(pem_bytes).hexdigest()

    print(f"MD5 of the provided certificate: {md5_hash}") 
    for cert_type, path in cert_paths.items():
        print(f"\nChecking {cert_type} store...")
        output = device.shell(f"su -c 'ls {path}/{args.file}'")
        if args.file not in output:
            print(f"Certificate file {args.file} not found in {cert_type} store.")
            continue
        output = device.shell(f"su -c 'md5sum {path}/{args.file}'")
        if output:
            device_md5 = output.split()[0]
            if device_md5 == md5_hash:
                print(f"MD5 match found in {cert_type} store: {device_md5}")
                print(f"MD5sum from burp: {md5_hash}")
            else:
                print(f"Certificate not found in {cert_type} store.")
        else:
            print(f"Could not access {cert_type} store or file does not exist.")
