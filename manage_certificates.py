#!/usr/bin/env python3

import os
import argparse
import boto3
from subprocess import call
from datetime import datetime
import socket
import tarfile
import sys

def check_certificate_local(domain):
    cert_dir = f"/etc/letsencrypt/live/{domain}"
    cert_path = os.path.join(cert_dir, "fullchain.pem")
    privkey_path = os.path.join(cert_dir, "privkey.pem")
    return os.path.exists(cert_path) and os.path.exists(privkey_path)


def check_certificate_s3(domain, s3_bucket):
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=s3_bucket, Key=f"{domain}/fullchain.pem")
        s3.head_object(Bucket=s3_bucket, Key=f"{domain}/privkey.pem")
        return True
    except Exception:
        return False


def download_certificate_s3(domain, s3_bucket):
    cert_dir = f"/etc/letsencrypt/live/{domain}"
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)

    s3 = boto3.client('s3')
    s3.download_file(s3_bucket, f"{domain}/fullchain.pem", os.path.join(cert_dir, "fullchain.pem"))
    s3.download_file(s3_bucket, f"{domain}/privkey.pem", os.path.join(cert_dir, "privkey.pem"))


def generate_certificate(domain, email):
    call(["certbot", "--nginx", "-d", domain, "--agree-tos", "-m", email, "--non-interactive"])


def backup_letsencrypt(s3_bucket_name):
    hostname = socket.gethostname()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(os.getcwd(), 'backup')
    backup_filename = f"{hostname}_certificate_{timestamp}.tar.gz"
    backup_path = os.path.join(backup_dir, backup_filename)

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    with tarfile.open(backup_path, 'w:gz') as backup:
        backup.add('/etc/letsencrypt', arcname=os.path.basename('/etc/letsencrypt'))

    print(f"Backup stored at: {backup_path}")

    with open(backup_path, 'rb') as backup_file:
        s3 = boto3.client('s3')
        s3.upload_fileobj(backup_file, s3_bucket_name, f"backup/certificates/{backup_filename}")

    print(f"Backup uploaded to S3 bucket {s3_bucket_name} successfully.")


def main():
    parser = argparse.ArgumentParser(description="SSL certificate management with AWS S3 backup.")
    parser.add_argument("--domains", required=True, nargs='+', help="List of domains or subdomains.")
    parser.add_argument("--email", required=True, help="Email for Let's Encrypt.")
    parser.add_argument("--s3-bucket", required=True, help="S3 bucket for certificate backup.")

    args = parser.parse_args()
    s3_bucket_name = args.s3_bucket

    for domain in args.domains:
        if check_certificate_local(domain):
            print(f"Certificate for {domain} already exists locally.")
        elif check_certificate_s3(domain, s3_bucket_name):
            print(f"Certificate for {domain} found in S3. Downloading.")
            download_certificate_s3(domain, s3_bucket_name)
        else:
            print(f"Certificate for {domain} not found locally or in S3. Generating new one.")
            generate_certificate(domain, args.email)

        backup_letsencrypt(s3_bucket_name)

if __name__ == "__main__":
    main()
