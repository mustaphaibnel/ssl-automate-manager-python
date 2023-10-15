# SSL Automate Manager (Python)

This tool is designed to automate the management of SSL certificates for your domains. It facilitates the setup of domain certificates with Let's Encrypt, automatic configurations for Nginx or Apache web servers, backup functionalities to Amazon S3, and now includes enhanced features for improved backup management and easy restoration.

## Features

### Enhanced Backup Management

* **Automatic S3 Sync**: Automatically syncs SSL certificates with the specified S3 bucket, ensuring that the latest certificates are always backed up.

* **Customizable Backup Schedules**: Easily set up cron jobs to schedule backups at your preferred intervals - daily, weekly, or custom.

* **Host-specific Backups**: Each backup is tagged with the hostname and timestamp for easy identification and management.

### Easy Restoration

* **Conflict Handling**: The restoration script is equipped to handle conflicts, skipping over existing files to prevent unintentional overwrites.

* **Selective Restoration**: Restore specific certificates with ease, providing flexibility and control over the restoration process.

## Prerequisites

1. **Python**: Requires Python 3.x.
2. [**AWS CLI**](aws-cli.md): Ensure AWS CLI is installed and configured with necessary credentials.
3. **Nginx or Apache**: The script supports configurations for both web servers.
4. **Certbot**: Used for obtaining certificates from Let's Encrypt.
5. **Boto3**: Python SDK for AWS, used for S3 interactions.

## Configuration

Ensure AWS CLI is set up with required profiles and permissions, the web server is installed and running, and Certbot is installed.

## Usage

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/mustaphaibnel/ssl-automate-manager-python.git
    cd ssl-automate-manager-python
    ```

2. **Run the SSL Certificate Manager Script**:
    ```bash
    ./cli_script.py --domains your_domain1.com your_domain2.com --email your_email@example.com --ports 9000 9001 --s3-bucket your_s3_bucket_name --server nginx
    ```

3. **Run the Backup Script**:
    ```bash
    ./s3_backup.py --s3-bucket your_s3_bucket_name --set-cron weekly
    ```

4. **Run the Restoration Script**:
    ```bash
    ./s3_restore.py --s3-bucket your_s3_bucket_name --local-dir /your/local/directory
    ```

Replace placeholders with your actual values.

## Backup & Recovery

The enhanced backup and recovery feature ensures your SSL certificates are not only backed up to your provided S3 bucket but are easily restorable. The automated conflict resolution ensures existing files are skipped during the restoration process to preserve data integrity.


## Installing Packages
Below is the `requirements.txt` file that includes all the necessary Python packages with specific versions that your scripts require. You should modify the version numbers based on your current environment or the version that you want to freeze.

```plaintext
boto3==1.17.49
botocore==1.20.49
certbot==1.12.0
python-crontab==2.5.1
```

### How to Use `requirements.txt`

1. **Creating the `requirements.txt` File:**

   You can manually create a `requirements.txt` file and copy the above content into that file. Alternatively, if you want to automatically generate it based on the installed packages, use:
   ```bash
   pip freeze > requirements.txt
   ```

2. **Installing Packages from `requirements.txt`:**

   To install the packages listed in the `requirements.txt` file, use:
   ```bash
   pip install -r requirements.txt
   ```

### Note

- The `boto3` and `botocore` packages are for AWS S3 interactions.
- `certbot` is used for obtaining SSL certificates from Let’s Encrypt.
- `python-crontab` is used for managing the cron jobs for automatic backups.

Ensure to test the specific versions in your environment; you might need to adjust them based on compatibility and the features you need. Also, keep an eye on updates for security and feature enhancements.

## Contributing & Issues

We welcome contributions, enhancements, and bug reports. Feel free to open an issue or create a pull request on the [GitHub repository](https://github.com/mustaphaibnel/ssl-automate-manager-python).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
