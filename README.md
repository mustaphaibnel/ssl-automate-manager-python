
# SSL Automate Manager (Python)

This tool is designed to automate the management of SSL certificates for your domains. It streamlines the process of setting up domain certificates with Let's Encrypt, automatically configures them for web servers (Nginx or Apache), and also provides backup functionality to Amazon S3.

## Prerequisites

1. **Python**: The script is written in Python and requires Python 3.x.
2. **AWS CLI**(https://github.com/mustaphaibnel/ssl-automate-manager-python/tree/main): The script interacts with Amazon S3 for backup purposes. Ensure you have AWS CLI installed and configured with the necessary credentials.
3. **Nginx or Apache**: The script can set up configurations for either of these web servers. Ensure you have the web server of your choice installed.
4. **Certbot**: The script uses Certbot to obtain certificates from Let's Encrypt.
5. **Boto3**: The Python SDK for AWS. It's used to interact with the Amazon S3 service.

## Configuration

Before running the script, ensure that:

1. AWS CLI is set up with the required profiles and permissions to access the S3 bucket.
2. The server (Nginx or Apache) is installed and running.
3. Certbot is installed.

## Usage

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mustaphaibnel/ssl-automate-manager-python.git
   cd ssl-automate-manager-python
   ```

2. **Run the Script**:

   ```bash
   ./cli_script.py --domains your_domain1.com your_domain2.com --email your_email@example.com --ports 9000 9001 --s3-bucket your_s3_bucket_name --server nginx
   ```

Replace the placeholders (`your_domain1.com`, `your_email@example.com`, etc.) with your actual domain names, email, and other details.

3. **Configurations**:

   - `--domains`: List of domains or subdomains you wish to manage.
   - `--email`: Email address for Let's Encrypt.
   - `--ports`: List of ports corresponding to the domains.
   - `--s3-bucket`: Name of the S3 bucket for certificate backup.
   - `--server`: Specify the web server. Choose either `nginx` or `apache`.

## Backup & Recovery

The script has an automated mechanism to back up SSL certificates to the provided S3 bucket. If you ever find the local certificate missing or corrupted, the script will attempt to fetch it from the S3 bucket before attempting to generate a new one.

## Contributing & Issues

For any issues, suggestions, or contributions, please head over to the [GitHub repository](https://github.com/mustaphaibnel/ssl-automate-manager-python) and open an issue or pull request.
