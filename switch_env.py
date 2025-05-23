#!/usr/bin/env python3

import os
import subprocess
import argparse
import re
import time

# File paths
ENV_FILE = "/opt/strapi/.env"
SERVER_FILE = "/opt/strapi/config/server.js"
MIDDLEWARES_FILE = "/opt/strapi/config/middlewares.js"
VITE_FILE = "/opt/strapi/vite.config.js"
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

# Middleware configurations for dev and prod
DEV_MIDDLEWARES_CONFIG = """
module.exports = [
  'strapi::errors',
  {
    name: 'strapi::cors',
    config: {
      origin: ['http://localhost:1337', 'http://127.0.0.1:1337', 'http://localhost:3001'],
      headers: ['Content-Type', 'Authorization', 'X-Frame-Options', 'Origin', 'Accept'],
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    },
  },
  {
    name: 'strapi::security',
    config: {
      contentSecurityPolicy: {
        useDefaults: true,
        directives: {
          'connect-src': ["'self'", 'https:', 'http:'],
          'img-src': ["'self'", 'data:', 'blob:'],
          'media-src': ["'self'", 'data:', 'blob:'],
          'script-src': ["'self'", "'unsafe-inline'"],
          'style-src': ["'self'", "'unsafe-inline'"],
          upgradeInsecureRequests: null,
        },
      },
    },
  },
  'strapi::poweredBy',
  'strapi::logger',
  'strapi::query',
  'strapi::body',
  'strapi::session',
  'strapi::favicon',
  'strapi::public',
  'global::error-handler',
];
"""

PROD_MIDDLEWARES_CONFIG = """
module.exports = [
  'strapi::errors',
  {
    name: 'strapi::cors',
    config: {
      origin: ['https://rolleilookup.com', 'https://rolleilookup.com/admin'],
      headers: ['Content-Type', 'Authorization', 'X-Frame-Options', 'Origin', 'Accept'],
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    },
  },
  {
    name: 'strapi::security',
    config: {
      contentSecurityPolicy: {
        useDefaults: true,
        directives: {
          'connect-src': ["'self'", 'https:', 'http:'],
          'img-src': ["'self'", 'data:', 'blob:', 'https://*.digitaloceanspaces.com'],
          'media-src': ["'self'", 'data:', 'blob:', 'https://*.digitaloceanspaces.com'],
          'script-src': ["'self'", "'unsafe-inline'", 'https://rolleilookup.com'],
          'style-src': ["'self'", "'unsafe-inline'"],
          upgradeInsecureRequests: null,
        },
      },
    },
  },
  'strapi::poweredBy',
  'strapi::logger',
  'strapi::query',
  'strapi::body',
  'strapi::session',
  'strapi::favicon',
  'strapi::public',
  'global::error-handler',
];
"""

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
    """Update config/server.js with the specified URL and proxy setting."""
    server_config = f"""
module.exports = ({{ env }}) => ({{
  host: env('HOST', '0.0.0.0'),
  port: env.int('PORT', 1337),
  url: env('URL', '{config["URL"]}'),
  admin: {{
    url: env('ADMIN_URL', '/admin'),
  }},
  app: {{
    keys: env.array('APP_KEYS'),
  }},
  proxy: true, // Trust proxy headers from Nginx
  async bootstrap({{ strapi }}) {{
    const syncSerialNumbers = require('../scripts/sync-serial-numbers');
    await syncSerialNumbers({{ strapi }});
  }},
}});
"""
    with open(SERVER_FILE, 'w') as f:
        f.write(server_config)
    print(f"Updated {SERVER_FILE} with URL={config['URL']} and proxy=true")

def update_middlewares_file(mode):
    """Update config/middlewares.js with the appropriate CORS origins for the mode."""
    middlewares_config = DEV_MIDDLEWARES_CONFIG if mode == "dev" else PROD_MIDDLEWARES_CONFIG
    with open(MIDDLEWARES_FILE, 'w') as f:
        f.write(middlewares_config)
    print(f"Updated {MIDDLEWARES_FILE} with CORS origins for {mode}")

def remove_vite_config():
    """Remove vite.config.js if it exists."""
    if os.path.exists(VITE_FILE):
        os.remove(VITE_FILE)
        print(f"Removed {VITE_FILE}")
    else:
        print(f"{VITE_FILE} does not exist, skipping removal")

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
    """Clear Strapi and Vite caches, excluding admin panel build directory."""
    cache_dirs = [
        "/opt/strapi/.cache",
        "/opt/strapi/node_modules/.vite"
    ]
    for cache_dir in cache_dirs:
        try:
            subprocess.run(["rm", "-rf", cache_dir], check=True)
            print(f"Cleared cache directory: {cache_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Error clearing cache directory {cache_dir}: {e}")
    print("Cleared all caches (preserving /opt/strapi/build)")

def git_commit_and_push(mode):
    """Commit and push changes to Git repository without affecting untracked files."""
    os.chdir(STRAPI_DIR)
    try:
        # Stage only the specified files
        subprocess.run(["git", "add", "config/server.js", "config/middlewares.js", "deploy/rolleilookup.com.conf", "switch_env.py"], check=True)
        if os.path.exists(VITE_FILE):
            subprocess.run(["git", "rm", "-f", "vite.config.js"], check=True)
        else:
            subprocess.run(["git", "rm", "-f", "vite.config.js"], check=False)
        commit_message = f"Switch to {mode} mode"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"Committed and pushed changes to Git: {commit_message}")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
        if "nothing to commit" in str(e):
            print("No changes to commit")

def ensure_admin_panel_built():
    """Ensure the admin panel is built for prod mode."""
    if not os.path.exists("/opt/strapi/build"):
        print("Admin panel not built, building now...")
        try:
            subprocess.run(["NODE_OPTIONS=--max-old-space-size=2048 npm run build"], cwd=STRAPI_DIR, shell=True, check=True)
            print("Admin panel built successfully")
        except subprocess.CalledProcessError as e:
            print(f"Failed to build admin panel: {e}")
            exit(1)

def manage_services(mode):
    """Stop all services and start the appropriate ones based on mode."""
    # Step a: Stop the dev service (strapi-dev) and ensure port 1337 is free
    services = ["strapi-dev", "strapi-prod", "rolleiflex-frontend"]
    for service in services:
        try:
            subprocess.run(["sudo", "systemctl", "stop", service], check=True)
            print(f"Stopped {service}")
        except subprocess.CalledProcessError:
            print(f"Service {service} was not running")

    # Forcefully kill any lingering Strapi processes on port 1337
    try:
        result = subprocess.run(
            ["lsof", "-i", ":1337", "-t"],
            capture_output=True,
            text=True,
            check=False
        )
        pids = result.stdout.strip().split('\n')
        for pid in pids:
            if pid:
                subprocess.run(["sudo", "kill", "-9", pid], check=True)
                print(f"Killed lingering process on port 1337 with PID {pid}")
    except subprocess.CalledProcessError:
        print("No lingering processes found on port 1337")

    time.sleep(2)

    # Step b: Config files are already updated by previous steps
    # Step c: Start the prod service (strapi-prod) and frontend
    if mode == "dev":
        subprocess.run(["sudo", "systemctl", "start", "strapi-dev"], check=True)
        print("Started strapi-dev service")
    else:
        # Ensure admin panel is built before starting prod
        ensure_admin_panel_built()
        subprocess.run(["sudo", "systemctl", "start", "strapi-prod"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "rolleiflex-frontend"], check=True)
        print("Started strapi-prod and rolleiflex-frontend services")

def ensure_serial_number_controller():
    """Ensure the serial-number controller file exists and is not empty."""
    controller_file = "/opt/strapi/src/api/serial-number/controllers/serial-number.js"
    controller_dir = os.path.dirname(controller_file)
    default_controller_content = """'use strict';

const { createCoreController } = require('@strapi/strapi').factories;

module.exports = createCoreController('api::serial-number.serial-number');
"""

    # Create the controllers directory if it doesn't exist
    if not os.path.exists(controller_dir):
        os.makedirs(controller_dir)
        print(f"Created directory: {controller_dir}")

    # Check if the controller file exists and is not empty
    if not os.path.exists(controller_file) or os.path.getsize(controller_file) == 0:
        with open(controller_file, 'w') as f:
            f.write(default_controller_content)
        print(f"Created serial-number controller file: {controller_file}")
    else:
        print(f"Serial-number controller file already exists and is not empty: {controller_file}")

def ensure_serial_number_schema():
    """Ensure the serial-number schema file exists and is not empty."""
    schema_file = "/opt/strapi/src/api/serial-number/content-types/serial-number/schema.json"
    schema_dir = os.path.dirname(schema_file)
    default_schema_content = """{
  "kind": "collectionType",
  "collectionName": "serial_numbers",
  "info": {
    "singularName": "serial-number",
    "pluralName": "serial-numbers",
    "displayName": "Serial Number"
  },
  "options": {
    "draftAndPublish": false
  },
  "attributes": {
    "serial_start": {
      "type": "integer",
      "required": true
    },
    "serial_end": {
      "type": "integer",
      "required": true
    },
    "model_name": {
      "type": "string"
    },
    "year_produced": {
      "type": "string"
    },
    "taking_lens": {
      "type": "string"
    },
    "looking_lens": {
      "type": "string"
    },
    "description": {
      "type": "text"
    }
  }
}
"""

    # Create the content-types/serial-number directory if it doesn't exist
    if not os.path.exists(schema_dir):
        os.makedirs(schema_dir)
        print(f"Created directory: {schema_dir}")

    # Check if the schema file exists and is not empty
    if not os.path.exists(schema_file) or os.path.getsize(schema_file) == 0:
        with open(schema_file, 'w') as f:
            f.write(default_schema_content)
        print(f"Created serial-number schema file: {schema_file}")
    else:
        print(f"Serial-number schema file already exists and is not empty: {schema_file}")

def main():
    parser = argparse.ArgumentParser(description="Switch Strapi between dev and prod environments")
    parser.add_argument("mode", choices=["dev", "prod"], help="Environment mode (dev or prod)")
    args = parser.parse_args()

    config = DEV_CONFIG if args.mode == "dev" else PROD_CONFIG
    update_env_file(config)
    update_server_file(config)
    update_middlewares_file(args.mode)
    remove_vite_config()
    update_nginx_config()
    git_commit_and_push(args.mode)
    clear_caches()
    ensure_serial_number_controller()  # Ensure the controller file exists
    ensure_serial_number_schema()     # Ensure the schema file exists
    manage_services(args.mode)

if __name__ == "__main__":
    main()
