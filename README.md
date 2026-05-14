# onix_bot

<img width="800" height="500" alt="onix" src="https://github.com/user-attachments/assets/0741c4d8-387a-47d7-82b4-c05b4a35a24f" />


[![GitHub stars](https://img.shields.io/github/stars/Iankulani/wren_bot?style=for-the-badge&logo=github)](https://github.com/Iankulani/wren_bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Iankulani/wren_bot?style=for-the-badge&logo=github)](https://github.com/Iankulani/wren_bot/network)
[![GitHub watchers](https://img.shields.io/github/watchers/Iankulani/wren_bot?style=for-the-badge&logo=github)](https://github.com/Iankulani/wren_bot/watchers)
[![GitHub contributors](https://img.shields.io/github/contributors/Iankulani/wren_bot?style=for-the-badge&logo=github)](https://github.com/Iankulani/wren_bot/graphs/contributors)
[![GitHub last commit](https://img.shields.io/github/last-commit/Iankulani/wren_bot?style=for-the-badge&logo=git)](https://github.com/Iankulani/wren_bot/commits/main)
[![Docker Pulls](https://img.shields.io/badge/docker-available-blue?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/iankulaniking_phisher)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-blue?style=for-the-badge&logo=linux&logoColor=white)](https://github.com/Iankulani/wren_bot)
[![Python](https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

Onix Bot is a multi-platform command execution tool that enables users to fire commands seamlessly via Telegram, Discord, Signal, WhatsApp, iMessage, and a web app. Designed for educational and research purposes only, Onix Bot serves as a controlled environment for understanding command-and-control mechanics across diverse messaging ecosystems. It supports white hat, black hat, and all hacker types—allowing defenders to simulate threats, researchers to analyze attack patterns, and ethical testers to harden systems. Users must operate within legal boundaries. Onix Bot bridges communication layers and remote execution, offering hands-on insight into modern security challenges. Always use responsibly and with explicit authorization.

**Advanced Security Testing Framework with Multi-Platform Integration**

## 🚀 Features

- **5000+ Security Commands** - Comprehensive toolkit for security testing
- **Multi-Platform Integration** - Discord, Telegram, Slack, WhatsApp, Signal, Google Chat
- **Advanced Phishing Suite** - 50+ customizable templates
- **SSH Remote Access** - Execute commands across platforms
- **Real Traffic Generation** - ICMP/TCP/UDP/HTTP/DNS/ARP
- **Nikto Scanner Integration** - Web vulnerability scanning
- **IP Management & Threat Detection** - Real-time monitoring
- **Web Dashboard** - Cyberpunk-themed management interface
- **API Management** - RESTful API with key authentication

## 📋 Requirements

- Python 3.7 or higher
- 1GB RAM minimum (2GB recommended)
- 500MB disk space
- Linux/macOS/Windows

## 🛠️ Quick Installation

### Linux/macOS
```bash
git clone https://github.com/iankarl/onix-bot.git
cd onix-bot
```
        
chmod +x install.sh
./install.sh



# Windows
```bash
git clone https://github.com/Iankulani/onix_bot.git
cd onix-bot
```
install.bat
Docker

# Ubuntu-based image
```bash
docker build -t onix-bot .
docker run -p 5000:5000 -p 8080:8080 onix-bot
```

# Alpine (lightweight)
```bash
docker build -f Dockerfile.alpine -t onix-bot-alpine .
docker run -p 5000:5000 -p 8080:8080 onix-bot-alpine
```

# Using docker-compose
```bash
docker-compose up -d
```
🎮 Usage
CLI Mode
bash
./run.sh
# or

```bash
python3 onix_bot.py
```

# Web Dashboard
```bash
http://localhost:5000
```    
# Bot Commands
```bash
help	Show all commands
status	System statistics
ping <target>	ICMP test
scan <target>	Port scan
phish <platform>	Generate phishing link
ssh_add <name> <host> <user>	Add SSH connection
traffic icmp <target> <count>	Traffic generation
````


Use only on authorized systems

Encrypt sensitive data with cryptography

Regular security updates recommended

Keep API keys secure

# 📊 API Documentation
Authentication

# Create API key
```bash
api_create my_key read,write
```
# Use API key
```bash      
curl -H "X-API-Key: your-key" http://localhost:5000/api/command
```

# Endpoints
```bash
POST /api/command - Execute command

GET /api/stats - Get statistics

GET /api/threats - List threats
```
# 🐛 Troubleshooting
Common Issues
Module not found:

```bash
pip install -r requirements.txt
```
Permission denied:

```bash
chmod +x *.sh
Port already in use:
```
# Change port in config.json or use:
```bash
python3 onix_bot.py --port 5001
```
# 📝 License
Proprietary License - All rights reserved

👤 Author
Ian Carter Kulani

GitHub: Iankulani

# ⚠️ Disclaimer
This tool is for educational and authorized testing purposes only. Users are responsible for complying with all applicable laws.


# Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Iankulani/onix_bot&type=Date)](https://star-history.com/#Iankulani/onix_bot&Date)
