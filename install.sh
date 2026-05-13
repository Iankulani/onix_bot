#!/bin/bash
# ONIX-BOT Installation Script for Linux/macOS
# Author: Ian Carter Kulani
# Version: 2.0.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${RED}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║                      ONIX-BOT INSTALLER                          ║
║                         Version 2.0.0                            ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check Python version
check_python() {
    echo -e "${CYAN}[*] Checking Python installation...${NC}"
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}[!] Python 3 not found. Please install Python 3.7+${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if (( $(echo "$PYTHON_VERSION < 3.7" | bc -l) )); then
        echo -e "${RED}[!] Python 3.7+ required. Found $PYTHON_VERSION${NC}"
        exit 1
    fi
    echo -e "${GREEN}[✓] Python $PYTHON_VERSION found${NC}"
}

# Install system dependencies
install_system_deps() {
    echo -e "${CYAN}[*] Installing system dependencies...${NC}"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3-pip python3-dev nmap whois net-tools iputils-ping dnsutils tcpdump libpcap-dev chromium-browser chromium-chromedriver git curl wget
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip python3-devel nmap whois net-tools iputils dnsutils tcpdump libpcap-devel chromium git curl wget
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-pip python3-devel nmap whois net-tools iputils dnsutils tcpdump libpcap-devel chromium git curl wget
        else
            echo -e "${YELLOW}[!] Unknown package manager. Please install dependencies manually.${NC}"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            echo -e "${YELLOW}[!] Homebrew not found. Installing...${NC}"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python3 nmap net-tools tcpdump libpcap chromedriver git wget
    else
        echo -e "${YELLOW}[!] Unsupported OS. Please install dependencies manually.${NC}"
    fi
    echo -e "${GREEN}[✓] System dependencies installed${NC}"
}

# Create virtual environment
setup_venv() {
    echo -e "${CYAN}[*] Setting up virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}[✓] Virtual environment created${NC}"
}

# Install Python dependencies
install_python_deps() {
    echo -e "${CYAN}[*] Installing Python dependencies...${NC}"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install core requirements
    pip install -r requirements.txt
    
    # Install optional dependencies if requested
    read -p "Install full dependencies (including dev tools)? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install -r requirements-full.txt
    fi
    
    echo -e "${GREEN}[✓] Python dependencies installed${NC}"
}

# Setup configuration directories
setup_directories() {
    echo -e "${CYAN}[*] Creating configuration directories...${NC}"
    mkdir -p .onix/phishing
    mkdir -p .onix/captured
    mkdir -p reports
    mkdir -p logs
    echo -e "${GREEN}[✓] Directories created${NC}"
}

# Create configuration file
create_config() {
    echo -e "${CYAN}[*] Creating configuration file...${NC}"
    
    cat > config.json << EOF
{
    "version": "2.0.0",
    "database": ".onix/onix.db",
    "log_file": "logs/onix.log",
    "phishing_dir": ".onix/phishing",
    "captured_dir": ".onix/captured",
    "web_port": 5000,
    "phish_port": 8080,
    "auto_start_web": true,
    "encryption_enabled": true,
    "max_log_size_mb": 100,
    "retention_days": 30
}
EOF
    echo -e "${GREEN}[✓] Configuration created${NC}"
}

# Create systemd service (Linux only)
create_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo -e "${CYAN}[*] Creating systemd service...${NC}"
        read -p "Create systemd service for auto-start? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            CURRENT_DIR=$(pwd)
            CURRENT_USER=$(whoami)
            
            sudo tee /etc/systemd/system/onix-bot.service > /dev/null << EOF
[Unit]
Description=ONIX-BOT Service
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/python3 onix_bot.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
            sudo systemctl daemon-reload
            echo -e "${GREEN}[✓] Systemd service created${NC}"
            echo -e "${YELLOW}To enable auto-start: sudo systemctl enable onix-bot${NC}"
            echo -e "${YELLOW}To start now: sudo systemctl start onix-bot${NC}"
        fi
    fi
}

# Create desktop entry (Linux only)
create_desktop_entry() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo -e "${CYAN}[*] Creating desktop entry...${NC}"
        read -p "Create desktop entry? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            CURRENT_DIR=$(pwd)
            
            cat > ~/.local/share/applications/onix-bot.desktop << EOF
[Desktop Entry]
Name=ONIX-BOT
Comment=Security Testing Framework
Exec=$CURRENT_DIR/run.sh
Icon=$CURRENT_DIR/icon.png
Terminal=true
Type=Application
Categories=Network;Security;
EOF
            chmod +x ~/.local/share/applications/onix-bot.desktop
            echo -e "${GREEN}[✓] Desktop entry created${NC}"
        fi
    fi
}

# Create run script
create_run_script() {
    echo -e "${CYAN}[*] Creating run script...${NC}"
    
    cat > run.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 onix_bot.py
EOF
    chmod +x run.sh
    echo -e "${GREEN}[✓] Run script created (./run.sh)${NC}"
}

# Main installation
main() {
    echo -e "${YELLOW}Starting ONIX-BOT installation...${NC}"
    echo
    
    check_python
    install_system_deps
    setup_venv
    install_python_deps
    setup_directories
    create_config
    create_run_script
    create_service
    create_desktop_entry
    
    echo
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ ONIX-BOT installation completed successfully!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo
    echo -e "${CYAN}To start ONIX-BOT:${NC}"
    echo -e "  ./run.sh"
    echo
    echo -e "${CYAN}Or activate virtual environment:${NC}"
    echo -e "  source venv/bin/activate"
    echo -e "  python3 onix_bot.py"
    echo
    echo -e "${YELLOW}For help: type 'help' in the bot terminal${NC}"
}

# Handle interrupt
trap 'echo -e "\n${RED}Installation cancelled${NC}"; exit 1' INT

# Run main
main