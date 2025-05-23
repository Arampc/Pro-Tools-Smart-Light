#!/bin/bash

# Pro Tools Recording Lights Setup Script
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check if running on macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "This script is designed for macOS only"
        exit 1
    fi
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3 first."
        log_info "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2)
    log_success "Python $python_version detected"
    
    # Check if we're in the right directory
    if [[ ! -f "config.json" ]]; then
        log_error "config.json not found. Are you in the right directory?"
        exit 1
    fi
    
    if [[ ! -f "recording_lights_controller.py" ]]; then
        log_error "recording_lights_controller.py not found. Are you in the right directory?"
        exit 1
    fi
}

setup_virtual_environment() {
    log_info "Setting up Python virtual environment..."
    
    # Remove existing venv if it exists
    if [[ -d "venv" ]]; then
        log_warning "Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create virtual environment
    python3 -m venv venv
    
    # Check if venv was created successfully
    if [[ ! -d "venv" ]]; then
        log_error "Failed to create virtual environment"
        exit 1
    fi
    
    log_success "Virtual environment created"
}

install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if ! pip install -r requirements.txt; then
        log_error "Failed to install dependencies"
        exit 1
    fi
    
    log_success "Dependencies installed"
}

setup_permissions() {
    log_info "Setting up file permissions..."
    
    # Make scripts executable
    chmod +x recording_lights_controller.py
    chmod +x manual_control.py
    chmod +x test_devices.py
    chmod +x test_midi.py
    
    log_success "File permissions set"
}

setup_launch_agent() {
    log_info "Setting up macOS launch agent..."
    
    # Update the plist file to use the virtual environment Python
    local project_dir=$(pwd)
    local python_path="$project_dir/venv/bin/python"
    
    # Create updated plist content
    cat > com.studio.recordinglights.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.studio.recordinglights</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$python_path</string>
        <string>$project_dir/recording_lights_controller.py</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$project_dir/stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>$project_dir/stderr.log</string>
    
    <key>WorkingDirectory</key>
    <string>$project_dir</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p ~/Library/LaunchAgents
    
    # Copy launch agent to user's LaunchAgents directory
    cp com.studio.recordinglights.plist ~/Library/LaunchAgents/
    
    log_success "Launch agent installed"
}

start_service() {
    log_info "Starting the recording light service..."
    
    # Unload existing service if running
    launchctl unload ~/Library/LaunchAgents/com.studio.recordinglights.plist 2>/dev/null || true
    
    # Load the launch agent
    if ! launchctl load ~/Library/LaunchAgents/com.studio.recordinglights.plist; then
        log_error "Failed to load launch agent"
        exit 1
    fi
    
    # Give it a moment to start
    sleep 2
    
    # Check if service is running
    if launchctl list | grep -q "com.studio.recordinglights"; then
        log_success "Service started successfully"
    else
        log_warning "Service may not have started properly"
        log_info "Check stderr.log for error messages"
    fi
}

print_completion_message() {
    echo ""
    log_success "Setup complete!"
    echo ""
    echo -e "${GREEN}The Recording Lights Controller is now installed and running.${NC}"
    echo "It will automatically start when you log in."
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Configure Pro Tools to send MIDI to 'Recording Light Controller'"
    echo "2. See PRO_TOOLS_SETUP.md for detailed Pro Tools configuration"
    echo ""
    echo -e "${BLUE}Service management:${NC}"
    echo "  Start:     launchctl start com.studio.recordinglights"
    echo "  Stop:      launchctl stop com.studio.recordinglights"
    echo "  Uninstall: launchctl unload ~/Library/LaunchAgents/com.studio.recordinglights.plist"
    echo ""
    echo -e "${BLUE}Logs:${NC}"
    echo "  Application: recording_lights.log"
    echo "  Output:      stdout.log"
    echo "  Errors:      stderr.log"
    echo ""
    echo -e "${BLUE}Testing:${NC}"
    echo "  Test devices: ./test_devices.py"
    echo "  Test MIDI:    ./test_midi.py"
    echo "  Manual:       ./manual_control.py"
}

# Main execution
main() {
    echo "Pro Tools Recording Lights Setup"
    echo "================================="
    
    check_requirements
    setup_virtual_environment
    install_dependencies
    setup_permissions
    setup_launch_agent
    start_service
    print_completion_message
}

# Run main function
main "$@" 