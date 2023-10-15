#!/usr/bin/env python3

import argparse
import os
import boto3
import botocore

def restore_certificate(s3_bucket, local_directory):
    s3 = boto3.resource('s3')

    for object_summary in s3.Bucket(s3_bucket).objects.filter(Prefix="backup/certificates/"):
        file_name = object_summary.key.split('/')[-1]
        local_file_path = os.path.join(local_directory, file_name)

        # Skip if the certificate already exists locally
        if os.path.exists(local_file_path):
            print(f"Skipping {file_name} - already exists locally.")
            continue

        # Try to restore the certificate
        try:
            print(f"Restoring {file_name}...")
            s3.Bucket(s3_bucket).download_file(object_summary.key, local_file_path)
            print(f"Successfully restored {file_name} to {local_file_path}.")
        except botocore.exceptions.ClientError as e:
            print(f"Failed to restore {file_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Restore SSL Certificates from S3 Bucket")
    parser.add_argument("--s3-bucket", required=True, help="Name of the S3 bucket")
    parser.add_argument("--local-dir", default="/etc/letsencrypt", help="Local directory to restore certificates")
    args = parser.parse_args()

    restore_certificate(args.s3_bucket, args.local_dir)

if __name__ == "__main__":
    main()
