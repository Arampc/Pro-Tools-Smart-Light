# Pro Tools Recording Light Controller

Automatically control TP-Link smart lights based on Pro Tools recording state using MIDI communication. When you press Record in Pro Tools, all configured lights turn on. When you stop recording, they turn off.

## Features

- 🎙️ Direct MIDI communication with Pro Tools for instant response
- 💡 Controls TP-Link HS110 smart sockets and KL125 smart bulbs
- 🚀 Runs automatically when you log in to macOS
- ⚡ Ultra-low latency with debouncing for reliable operation
- 📝 Comprehensive logging for troubleshooting

## Supported Devices

This controller is configured for the following devices:

| Device | Location | Type | Device ID |
|--------|----------|------|-----------|
| Recording Light 1 | Green Room | Socket | 8006760185751EF6BC07278FBBFDBFE118D0045A |
| Recording Light 2 | Lounge | Socket | 8006AF4E0F1D4E8B792E8FE90811A3AA173D9829 |
| Recording Light 3 | Jim's Office | Socket | 8006675E37F7EBCB85C54FA0FC664D3817413EF6 |
| Recording Light 4 | Vestibule | Socket | 800644F8993DD132DC7A7416750BB39A18B1A134 |
| Recording Light 5 | Drum Room | Bulb | 80122FDBDF3FD96AE2E179F581E7171C1E8C9A2A |
| Recording Light 6 | Vocal Booth | Bulb | 8012D9D1E1961AFD70E7FB42B105DF051E89BD5F |

## Requirements

- macOS (tested on macOS 13+)
- Python 3.8 or higher
- Pro Tools with MIDI capability
- TP-Link smart devices connected to Wi-Fi network "624"
- Network access to control the devices

## Quick Setup

1. Clone or download this repository to your Documents folder
2. Open Terminal and navigate to the project directory:
   ```bash
   cd ~/Documents/pro-tools-recording-lights
   ```

3. Make the setup script executable and run it:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

The setup script will:
- Create a Python virtual environment
- Install all required dependencies
- Configure the launch agent for automatic startup
- Start the service immediately

## Pro Tools Configuration

After installation, you need to configure Pro Tools to send MIDI to the controller:

1. **Open Pro Tools** and go to **Setup > Peripherals > MIDI Controllers**

2. **Add a new MIDI Controller:**
   - Type: **HUI** (or Generic MIDI)
   - Receive From: *[Your MIDI Interface]*
   - Send To: **Recording Light Controller**
   - Click **OK**

3. **Configure MIDI Mapping:**
   - The controller expects:
     - **CC 117** for Play/Stop events
     - **CC 118** for Record Enable/Disable events

4. **Alternative: Use Pro Tools MIDI Track:**
   - Create a MIDI track
   - Route output to "Recording Light Controller"
   - Use MIDI events or automation to control lights

## How It Works

The controller creates a virtual MIDI port called "Recording Light Controller" that Pro Tools can send messages to. It monitors for specific Control Change (CC) messages:

- When **Record is enabled AND Play is pressed**: Lights turn **ON**
- When **Recording stops**: Lights turn **OFF**
- Events are debounced (250ms) to handle out-of-order MIDI messages

This direct MIDI approach provides:
- Instant response time
- 100% reliability
- No UI monitoring or accessibility permissions needed
- Works with any Pro Tools version that supports MIDI

## Manual Installation

If you prefer to install manually:

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Test the script:
   ```bash
   python recording_lights_controller.py
   ```

4. Install the launch agent:
   ```bash
   cp com.studio.recordinglights.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.studio.recordinglights.plist
   ```

## Usage

Once installed and configured:

1. The controller runs automatically in the background
2. Configure Pro Tools to send MIDI to "Recording Light Controller"
3. Use Pro Tools normally:
   - **Press Record + Play**: All lights turn ON
   - **Stop Recording**: All lights turn OFF

## Service Management

Control the background service:

```bash
# Start the service
launchctl start com.studio.recordinglights

# Stop the service
launchctl stop com.studio.recordinglights

# Restart the service
launchctl stop com.studio.recordinglights && launchctl start com.studio.recordinglights

# Uninstall the service
launchctl unload ~/Library/LaunchAgents/com.studio.recordinglights.plist
rm ~/Library/LaunchAgents/com.studio.recordinglights.plist
```

## Logs and Troubleshooting

The controller creates several log files for debugging:

- `recording_lights.log`: Main application log with device discovery and MIDI events
- `stdout.log`: Standard output from the service
- `stderr.log`: Error output from the service

### Common Issues

1. **Devices not found**: 
   - Ensure all devices are powered on and connected to Wi-Fi network "624"
   - Check that your Mac is on the same network
   - Try power cycling the devices

2. **MIDI port not showing in Pro Tools**:
   - Restart the controller service
   - Check if the virtual MIDI port was created: Look for "Recording Light Controller" in Audio MIDI Setup
   - Restart Pro Tools after starting the controller

3. **Lights not responding to Pro Tools**:
   - Verify Pro Tools is sending MIDI to "Recording Light Controller"
   - Check the logs for incoming MIDI messages
   - Ensure CC 117 and CC 118 are being sent

4. **Service not starting**:
   - Check stderr.log for Python errors
   - Ensure Python 3 is installed: `python3 --version`
   - Verify the virtual environment was created correctly

## Testing

Use the included test scripts:

- `test_devices.py`: Test TP-Link device connectivity
- `manual_control.py`: Manually control lights without Pro Tools

## Configuration

To add or modify devices, edit the `device_configs` list in `recording_lights_controller.py`:

```python
self.device_configs = [
    DeviceConfig("Device Name", "Location", "Socket|Bulb", "DEVICE_ID"),
    # Add more devices here
]
```

## License

This project is provided as-is for personal use in recording studios.

## Support

For issues or questions:
1. Check the log files for error messages
2. Ensure Pro Tools MIDI is configured correctly
3. Test device connectivity with `test_devices.py`
4. Verify MIDI messages are being received in the logs 