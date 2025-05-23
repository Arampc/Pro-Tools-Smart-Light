# Pro Tools MIDI Setup Guide

This guide will help you configure Pro Tools to send MIDI messages to the Recording Light Controller.

## Method 1: Using HUI Controller (Recommended)

### Step 1: Open MIDI Controllers Setup
1. In Pro Tools, go to **Setup** menu
2. Select **Peripherals**
3. Click on the **MIDI Controllers** tab

### Step 2: Configure HUI Controller
1. Find an empty controller slot (usually #1-#4)
2. Set the following:
   - **Type**: HUI
   - **Receive From**: [Your MIDI interface or "None"]
   - **Send To**: Recording Light Controller
   - **# Ch's**: 8

### Step 3: Enable Transport Controls
1. Make sure "Enable" checkbox is checked
2. Click **OK** to save

The HUI protocol automatically sends:
- CC 117 when Play/Stop is pressed
- CC 118 when Record is enabled/disabled

## Method 2: Using MIDI Track Automation

### Step 1: Create a MIDI Track
1. Go to **Track** > **New**
2. Create 1 **MIDI Track**
3. Name it "Recording Lights"

### Step 2: Set MIDI Output
1. Click on the track's output selector
2. Choose **Recording Light Controller** as the output
3. Set MIDI channel to 1

### Step 3: Create MIDI Events
You can manually create MIDI CC events:
- For Record ON: Insert CC 118 with value 127
- For Record OFF: Insert CC 118 with value 0
- For Play ON: Insert CC 117 with value 127
- For Play OFF: Insert CC 117 with value 0

## Method 3: Using Peripherals Synchronization

### Step 1: Open Synchronization Setup
1. Go to **Setup** > **Peripherals**
2. Click on **Synchronization** tab

### Step 2: Configure Machine Control
1. Enable **Enable MMC**
2. Set MMC Output to **Recording Light Controller**

## Verifying the Connection

1. Start the Recording Light Controller:
   ```bash
   cd ~/Documents/pro-tools-recording-lights
   source venv/bin/activate
   python test_midi.py
   ```

2. In Pro Tools:
   - Press Record Enable
   - Press Play
   - You should see MIDI messages in the terminal

3. Common MIDI Messages:
   - `CC 117: 127` - Play started
   - `CC 117: 0` - Play stopped
   - `CC 118: 127` - Record enabled
   - `CC 118: 0` - Record disabled

## Troubleshooting

### MIDI Port Not Visible
1. Make sure the Recording Light Controller is running
2. Restart Pro Tools after starting the controller
3. Check Audio MIDI Setup to verify the port exists

### No MIDI Messages Received
1. Verify the correct output is selected in Pro Tools
2. Check that the controller slot is enabled
3. Try sending test MIDI notes to verify routing

### Lights Not Responding
1. Check the recording_lights.log file
2. Verify devices are connected with test_devices.py
3. Ensure both Record AND Play are active for lights to turn on

## Advanced Configuration

### Custom MIDI Mapping
If you need different CC numbers, edit `recording_lights_controller.py`:

```python
# MIDI Constants
CC_CODE = 176  # Control Change message
CC_RECORD = 118  # Change this to your preferred CC
CC_PLAY = 117   # Change this to your preferred CC
```

### Using with Control Surfaces
Most control surfaces that support HUI protocol will work automatically. Popular compatible surfaces:
- Avid Artist Mix/Control
- Behringer X-Touch
- PreSonus FaderPort
- Mackie Control Universal

Simply route the surface through the Recording Light Controller or use a MIDI splitter/merger. 