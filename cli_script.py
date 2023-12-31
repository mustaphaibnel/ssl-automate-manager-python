#!/usr/bin/env python3

import os
import argparse
import boto3
from subprocess import call
import botocore
import sys
import argparse

def check_certificate_locally(domain):
    cert_dir = f"/etc/letsencrypt/live/{domain}"
    cert_path = os.path.join(cert_dir, "fullchain.pem")
    privkey_path = os.path.join(cert_dir, "privkey.pem")

    if os.path.exists(cert_path) and os.path.exists(privkey_path):
        print(f"Certificate for {domain} already exists locally.")
        return True
    
    if os.path.exists(cert_dir):
        print(f"Incomplete certificate found locally for {domain}. Deleting...")
        os.system(f"rm -rf {cert_dir}")

    print(f"Certificate for {domain} not found locally.")
    return False

def check_certificate_on_s3(domain, ip_address, s3_bucket):
    s3 = boto3.client('s3')
    s3_path = f"certificate/{ip_address}/{domain}/"

    try:
        s3.head_object(Bucket=s3_bucket, Key=f"{s3_path}fullchain.pem")
        s3.head_object(Bucket=s3_bucket, Key=f"{s3_path}privkey.pem")
        print(f"Certificate for {domain} found on S3.")
        return True
    except botocore.exceptions.ClientError:
        print(f"Certificate for {domain} not found on S3.")
        return False

def download_certificate_from_s3(domain, ip_address, s3_bucket):
    s3 = boto3.client('s3')
    cert_dir = f"/etc/letsencrypt/live/{domain}"
    s3_path = f"certificate/{ip_address}/{domain}/"
    cert_path = os.path.join(cert_dir, "fullchain.pem")
    privkey_path = os.path.join(cert_dir, "privkey.pem")
    
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    
    try:
        s3.download_file(s3_bucket, f"{s3_path}fullchain.pem", cert_path)
        s3.download_file(s3_bucket, f"{s3_path}privkey.pem", privkey_path)
        print(f"Certificate for {domain} downloaded from S3.")
    except Exception as e:
        print(f"Error downloading certificate from S3: {e}")
        os.system(f"rm -rf {cert_dir}")
        sys.exit(1)

def get_certificate(domain, ip_address, email, s3_bucket):
    if not check_certificate_locally(domain):
        if check_certificate_on_s3(domain, ip_address, s3_bucket):
            download_certificate_from_s3(domain, ip_address, s3_bucket)
            return True  # Since the cert is now locally available
        else:
            print(f"Generating a new certificate for {domain}...")
            result = call(["certbot", "--nginx", "-d", domain, "--agree-tos", "-m", email,"--non-interactive", "--redirect"])
            return result == 0  # True if certbot command was successful
    return True  # Certificate was found locally

def backup_to_s3(domain, ip_address, s3_bucket):
    s3 = boto3.client('s3')
    s3_path = f"certificate/{ip_address}/{domain}/"
    certs_path = f"/etc/letsencrypt/live/{domain}/"
    cert_file = os.path.join(certs_path, "fullchain.pem")
    privkey_file = os.path.join(certs_path, "privkey.pem")

    try:
        s3.head_object(Bucket=s3_bucket, Key=f"{s3_path}fullchain.pem")
        print(f"Certificate for {domain} already backed up in S3.")
    except botocore.exceptions.ClientError:
        if os.path.exists(cert_file) and os.path.exists(privkey_file):
            s3.upload_file(cert_file, s3_bucket, f"{s3_path}fullchain.pem")
            s3.upload_file(privkey_file, s3_bucket, f"{s3_path}privkey.pem")
            print(f"Certificate for {domain} backed up to S3.")

def setup_nginx(domain, port):
    config = f"""
server {{
    listen 80;
    server_name {domain};
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl;
    server_name {domain};

    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {{
        proxy_pass http://localhost:{port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_cache_bypass $http_upgrade;
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
    #parser.add_argument("--ip-address", required=True, help="IP address for certificate organization.")
    parser.add_argument("--ip-address", help="IP address for certificate organization.", default=os.getenv('MY_IP_ENV_VAR'))
    args = parser.parse_args()
    if not args.ip_address:
        print("Error: IP address is required.")
        sys.exit(1)
    if len(args.domains) != len(args.ports):
        print("Error: The number of domains must match the number of ports.")
        sys.exit(1)

    for domain, port in zip(args.domains, args.ports):
        cert_success = get_certificate(domain, args.ip_address, args.email, args.s3_bucket)
        if cert_success:
            backup_to_s3(domain, args.ip_address, args.s3_bucket)
            if args.server == "nginx":
                setup_nginx(domain, port)
            else:
                setup_apache(domain, port)
        else:
            print(f"Failed to obtain certificate for {domain}. Skipping server setup.")

if __name__ == "__main__":
    main()
