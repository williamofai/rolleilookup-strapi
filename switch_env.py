#!/usr/bin/env python3

import os
import subprocess
import argparse
import re
import time

# File paths
ENV_FILE = "/opt/strapi/.env"
SERVER_FILE = "/opt/strapi/config/server.js"
NGINX_SRC = "/opt/strapi/deploy/rolleilookup.com.conf"
NGINX_DEST = "/etc/nginx/sites-enabled/rolleilookup.com"
STRAPI_DIR = "/opt/strapi"
LOG_FILE = "/opt/strapi/strapi.log"

# Environment configurations
DEV_CONFIG = {
    "URL": "http://localhost:1337",
    "ADMIN_URL": "http://localhost:1337/admin",
    "NODE_ENV": "development",
}
PROD_CONFIG = {
    "URL": "https://rolleilookup.com",
    "ADMIN_URL": "https://rolleilookup.com/admin",
    "NODE_ENV": "production",
}

def update_env_file(config):
    """Update .env file with the specified configuration."""
    with open(ENV_FILE, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    keys_to_update = set(config.keys())
    for line in lines:
        if line.strip().startswith('#'):
            updated_lines.append(line)
            continue
        key = line.split('=')[0].strip() if '=' in line else None
        if key in keys_to_update:
            updated_lines.append(f"{key}={config[key]}\n")
            keys_to_update.remove(key)
        else:
            updated_lines.append(line)

    for key in keys_to_update:
        updated_lines.append(f"{key}={config[key]}\n")

    with open(ENV_FILE, 'w') as f:
        f.writelines(updated_lines)

    print(f"Updated {ENV_FILE} with {config}")

def update_server_file(config):
    """Update config/server.js with the specified URL."""
    with open(SERVER_FILE, 'r') as f:
        content = f.read()

    new_url = config["URL"]
    content = re.sub(r'url: env\(\'URL\', \'[^\']*\'\)', f"url: env('URL', '{new_url}')", content)

    with open(SERVER_FILE, 'w') as f:
        f.write(content)

    print(f"Updated {SERVER_FILE} with URL={new_url}")

def update_nginx_config():
    """Copy Nginx configuration to the system directory and reload Nginx."""
    try:
        subprocess.run(["sudo", "cp", NGINX_SRC, NGINX_DEST], check=True)
        print(f"Copied {NGINX_SRC} to {NGINX_DEST}")
        subprocess.run(["sudo", "nginx", "-t"], check=True)
        print("Nginx configuration test passed")
        subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True)
        print("Reloaded Nginx")
    except subprocess.CalledProcessError as e:
        print(f"Error updating Nginx configuration: {e}")
        exit(1)

def clear_caches():
    """Clear Strapi and Vite caches."""
    cache_dirs = [
        "/opt/strapi/.cache",
        "/opt/strapi/build",
        "/opt/strapi/node_modules/.vite"
    ]
    for cache_dir in cache_dirs:
        subprocess.run(["rm", "-
