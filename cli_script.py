#!/usr/bin/env python3

import os
import argparse
import boto3
from subprocess import call
import botocore

def get_certificate(domain, email, s3_bucket):
    cert_dir = f"/etc/letsencrypt/live/{domain}"
    cert_path = os.path.join(cert_dir, "fullchain.pem")
    privkey_path = os.path.join(cert_dir, "privkey.pem")

    if os.path.exists(cert_path) and os.path.exists(privkey_path):
        print(f"Certificate for {domain} already exists locally.")
        return

    s3 = boto3.client('s3')
    try:
        # Ensure the certificate directory exists
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)

        s3.download_file(s3_bucket, f"{domain}/fullchain.pem", cert_path)
        s3.download_file(s3_bucket, f"{domain}/privkey.pem", privkey_path)
        print(f"Certificate for {domain} downloaded from S3.")
        return
    except s3.exceptions.NoSuchKey:
        print(f"Certificate for {domain} not found in S3. Generating new one...")
        call(["certbot", "--nginx", "-d", domain, "--agree-tos", "-m", email])


def backup_to_s3(domain, s3_bucket):
    s3 = boto3.client('s3')
    certs_path = f"/etc/letsencrypt/live/{domain}/"

    cert_file = os.path.join(certs_path, "fullchain.pem")
    privkey_file = os.path.join(certs_path, "privkey.pem")

    # Check if the certificate exists in S3
    try:
        s3.head_object(Bucket=s3_bucket, Key=f"{domain}/fullchain.pem")
        print(f"Certificate for {domain} already backed up in S3.")
    except botocore.exceptions.ClientError:
        # If the certificate doesn't exist in S3, back it up
        if os.path.exists(cert_file) and os.path.exists(privkey_file):
            s3.upload_file(cert_file, s3_bucket, f"{domain}/fullchain.pem")
            s3.upload_file(privkey_file, s3_bucket, f"{domain}/privkey.pem")
            print(f"Certificate for {domain} backed up to S3.")


def setup_nginx(domain, port):
    config = f"""
server {{
    listen 80;
    server_name {domain};
    return 301 https://{domain}$request_uri;
}}

server {{
    listen 443 ssl;
    server_name {domain};

    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;

    location / {{
        proxy_pass http://localhost:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
    """
    with open(f"/etc/nginx/sites-available/{domain}", "w") as file:
        file.write(config)

    if os.path.exists(f"/etc/nginx/sites-enabled/{domain}"):
        os.remove(f"/etc/nginx/sites-enabled/{domain}")
    os.symlink(f"/etc/nginx/sites-available/{domain}", f"/etc/nginx/sites-enabled/{domain}")
    call(["nginx", "-s", "reload"])


def setup_apache(domain, port):
    config = f"""
<VirtualHost *:80>
    ServerName {domain}
    Redirect permanent / https://{domain}/
</VirtualHost>

<VirtualHost *:443>
    ServerName {domain}

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/{domain}/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/{domain}/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://localhost:{port}/
    ProxyPassReverse / http://localhost:{port}/
</VirtualHost>
    """
    with open(f"/etc/apache2/sites-available/{domain}.conf", "w") as file:
        file.write(config)

    if os.path.exists(f"/etc/apache2/sites-enabled/{domain}.conf"):
        os.remove(f"/etc/apache2/sites-enabled/{domain}.conf")
    os.symlink(f"/etc/apache2/sites-available/{domain}.conf", f"/etc/apache2/sites-enabled/{domain}.conf")
    call(["apache2ctl", "configtest"])
    call(["systemctl", "restart", "apache2"])


def main():
    parser = argparse.ArgumentParser(description="CLI tool to manage SSL certificates and web server config.")
    parser.add_argument("--domains", required=True, nargs='+', help="List of domains or subdomains.")
    parser.add_argument("--ports", required=True, nargs='+', help="List of ports corresponding to domains.")
    parser.add_argument("--email", required=True, help="Email for Let's Encrypt.")
    parser.add_argument("--s3-bucket", required=True, help="S3 bucket for certificate backup.")
    parser.add_argument("--server", required=True, choices=['nginx', 'apache'], help="Web server (nginx or apache).")

    args = parser.parse_args()

    if len(args.domains) != len(args.ports):
        print("Error: The number of domains must match the number of ports.")
        sys.exit(1)

    for domain, port in zip(args.domains, args.ports):
        get_certificate(domain, args.email, args.s3_bucket)
        backup_to_s3(domain, args.s3_bucket)
        if args.server == "nginx":
            setup_nginx(domain, port)
        else:
            setup_apache(domain, port)


if __name__ == "__main__":
    main()
