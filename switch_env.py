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
        subprocess.run(["rm", "-rf", cache_dir], check=True)
    print("Cleared caches")

def git_commit_and_push(mode):
    """Commit and push changes to Git repository."""
    os.chdir(STRAPI_DIR)
    try:
        subprocess.run(["git", "add", "config/server.js", "deploy/rolleilookup.com.conf", "switch_env.py"], check=True)
        commit_message = f"Switch to {mode} mode"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"Committed and pushed changes to Git: {commit_message}")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
        if "nothing to commit" in str(e):
            print("No changes to commit")

def manage_services(mode):
    """Stop all services and start the appropriate ones based on mode."""
    services = ["strapi-dev", "strapi-prod", "rolleiflex-frontend"]
    for service in services:
        try:
            subprocess.run(["sudo", "systemctl", "stop", service], check=True)
            print(f"Stopped {service}")
        except subprocess.CalledProcessError:
            print(f"Service {service} was not running")

    time.sleep(2)

    if mode == "dev":
        subprocess.run(["sudo", "systemctl", "start", "strapi-dev"], check=True)
        print("Started strapi-dev service")
    else:
        subprocess.run(["sudo", "systemctl", "start", "strapi-prod"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "rolleiflex-frontend"], check=True)
        print("Started strapi-prod and rolleiflex-frontend services")

def main():
    parser = argparse.ArgumentParser(description="Switch Strapi between dev and prod environments")
    parser.add_argument("mode", choices=["dev", "prod"], help="Environment mode (dev or prod)")
    args = parser.parse_args()

    config = DEV_CONFIG if args.mode == "dev" else PROD_CONFIG
    update_env_file(config)
    update_server_file(config)
    update_nginx_config()
    git_commit_and_push(args.mode)
    clear_caches()
    manage_services(args.mode)

if __name__ == "__main__":
    main()
