#!/usr/bin/env python3

import re
import os

# The directory where your nginx configurations are stored
conf_directory = '/etc/nginx/sites-enabled/'

# Navigate to Nginx's sites-enabled directory (or wherever your configuration files are stored)
os.chdir(conf_directory)

# Define a delimiter
delimiter = '-' * 30

# Create a regex pattern for extracting the server_name and proxy_pass directives
server_name_pattern = re.compile(r'server_name\s+(.+?);')
proxy_pass_pattern = re.compile(r'proxy_pass\s+(http://.+?)(/.*)?;')

# Prepare the data for tabulate
data = [("Filename", "Domain", "Proxy Pass", "Listen Port")]

# Grep for server_name and proxy_pass directives
for filename in os.listdir():
    with open(filename, 'r') as file:
        file_content = file.read()

        # Extract the server name (domain)
        server_name_match = server_name_pattern.search(file_content)
        if not server_name_match:
            continue
        
        server_name = server_name_match.group(1)

        # Extract the proxy pass destination
        proxy_pass_match = proxy_pass_pattern.search(file_content)
        if not proxy_pass_match:
            continue
        
        proxy_pass = proxy_pass_match.group(1)

        # Extract the listen port from proxy_pass
        listen_port = proxy_pass.split(':')[-1]

        # Append to the data
        data.append((filename, server_name, proxy_pass, listen_port))

# Print in a nice tabulated form
from tabulate import tabulate
print(tabulate(data, headers="firstrow", tablefmt="grid"))
