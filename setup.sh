#!/bin/bash

# Pro Tools Recording Lights Setup Script

echo "Setting up Pro Tools Recording Lights Controller..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Make the main script executable
chmod +x recording_lights_controller.py

# Update the plist file to use the virtual environment Python
echo "Updating launch agent configuration..."
sed -i '' 's|/usr/bin/python3|/Users/arampeleschen/Documents/pro-tools-recording-lights/venv/bin/python|' com.studio.recordinglights.plist

# Copy launch agent to user's LaunchAgents directory
echo "Installing launch agent..."
mkdir -p ~/Library/LaunchAgents
cp com.studio.recordinglights.plist ~/Library/LaunchAgents/

# Load the launch agent
echo "Loading launch agent..."
launchctl load ~/Library/LaunchAgents/com.studio.recordinglights.plist

echo "Setup complete!"
echo ""
echo "The Recording Lights Controller is now installed and running."
echo "It will automatically start when you log in."
echo ""
echo "To manually control the service:"
echo "  Start: launchctl start com.studio.recordinglights"
echo "  Stop:  launchctl stop com.studio.recordinglights"
echo "  Uninstall: launchctl unload ~/Library/LaunchAgents/com.studio.recordinglights.plist"
echo ""
echo "Logs can be found at:"
echo "  Application log: recording_lights.log"
echo "  Standard output: stdout.log"
echo "  Standard error: stderr.log" 