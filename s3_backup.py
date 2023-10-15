#!/usr/bin/env python3

import os
import argparse
import boto3
from datetime import datetime
import socket
import tarfile
from crontab import CronTab
import sys


def backup_to_s3_if_not_exists(s3_bucket_name):
    s3 = boto3.client('s3')

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

    try:
        s3.head_object(Bucket=s3_bucket_name, Key=f"backup/certificates/{backup_filename}")
        print(f"Backup already exists in S3. Skipping upload.")
    except Exception:
        with open(backup_path, 'rb') as backup_file:
            s3.upload_fileobj(backup_file, s3_bucket_name, f"backup/certificates/{backup_filename}")
            print(f"Backup uploaded to S3 bucket {s3_bucket_name} successfully.")


def set_cron_job(script_path, frequency):
    cron = CronTab(user='root')
    job = cron.new(command=f'python3 {script_path}')
    
    if frequency == 'daily':
        job.setall('0 0 * * *')
    elif frequency == 'weekly':
        job.setall('0 0 * * 0')
    
    cron.write()


def main():
    parser = argparse.ArgumentParser(description="SSL certificate backup to AWS S3.")
    parser.add_argument("--s3-bucket", required=True, help="S3 bucket for certificate backup.")
    parser.add_argument("--set-cron", choices=['daily', 'weekly'], help="Set a daily or weekly cron job to run this script.")

    args = parser.parse_args()
    
    if args.set_cron:
        set_cron_job(os.path.abspath(__file__), args.set_cron)
        print(f"A {args.set_cron} cron job has been set to run this script.")
        sys.exit(0)
    
    backup_to_s3_if_not_exists(args.s3_bucket)


if __name__ == "__main__":
    main()
