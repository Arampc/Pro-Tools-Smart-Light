# Pro Tools Smart Light Controller 🎙️💡

**Automatically turn your studio lights ON when recording in Pro Tools, and OFF when you stop!**

This is a simple system that connects your TP-Link smart lights to Pro Tools. When you press Record and Play in Pro Tools, all your lights turn on. When you stop recording, they turn off automatically.

**Perfect for:** 
- Recording studios
- Podcast setups  
- Home studios
- Any situation where you need "ON AIR" lighting

## What You Need

- **A Mac computer** (this won't work on Windows)
- **Pro Tools** (any recent version)
- **TP-Link smart lights or smart plugs** (connected to your Wi-Fi)
- **Basic computer skills** (following step-by-step instructions)

You do **NOT** need to know programming or be technical - this guide will walk you through everything!

## 📋 Step-by-Step Installation

**Don't worry - all the technical stuff happens automatically!**

### Step 1: Download This Project

**Option A: Easy Download**
1. Click the green **"Code"** button at the top of this page
2. Click **"Download ZIP"**  
3. Double-click the downloaded file to unzip it
4. Drag the folder to your **Documents** folder
5. Rename the folder to: `Pro-Tools-Smart-Light`

**Option B: If You're Comfortable with Terminal**
```bash
cd ~/Documents
git clone https://github.com/Arampc/Pro-Tools-Smart-Light.git
cd Pro-Tools-Smart-Light
```

### Step 2: Open Terminal and Run the Magic Setup Command

**Don't be scared of Terminal - you're just typing one command!**

1. **Open Terminal:**
   - Press `Cmd + Space` (opens Spotlight search)
   - Type: `Terminal`
   - Press Enter

2. **Navigate to your project:**
   ```bash
   cd ~/Documents/Pro-Tools-Smart-Light
   ```

3. **Run the automatic setup:**
   ```bash
   ./setup.sh
   ```

**What happens now?** The setup will automatically:
- ✅ Install all the technical Python stuff (you don't need to worry about this!)
- ✅ Test your smart lights
- ✅ Set everything up to start automatically when you turn on your Mac
- ✅ Start the system running in the background

**Just follow the prompts** - press Enter when it asks you to continue.

### Step 3: Run the Setup (This Installs Everything!)

**The setup script will automatically install all dependencies and test your devices:**

```bash
./setup.sh
```

**What this does:**
- ✅ Installs all Python libraries (kasa, rtmidi, etc.)
- ✅ Tests all your smart lights automatically
- ✅ Sets up the background service
- ✅ Shows you which devices were found

### Step 4: Configure Device IDs (If Needed)

**Good news! The system already knows about your lights!** The current configuration has your Device IDs pre-configured. But if you need to check or modify them:

1. **Test your devices manually** (after setup):
   ```bash
   # First activate the virtual environment
   source venv/bin/activate
   
   # Then run the test
   ./test_devices.py
   ```

2. **Edit the configuration file** (if needed):
   ```bash
   open config.json
   ```

3. **Device configuration format:**
   ```json
   {
     "devices": [
       {
         "name": "Studio Light 1",
         "location": "Control Room",
         "type": "Socket",
         "device_id": "<mac_address>"
       },
       {
         "name": "Studio Light 2", 
         "location": "Vocal Booth",
         "type": "Bulb",
         "device_id": "<mac_address>"
       }
     ]
   }
   ```

**Why Device IDs instead of IP addresses?**
- ✅ Device IDs never change (like serial numbers)
- ✅ Works even when your router assigns new IP addresses
- ✅ No need to set static IPs on your router
- ✅ Automatically finds devices wherever they are on your network

### Step 5: Connect Pro Tools to the Light System

**This is the final step to make Pro Tools talk to your lights!**

1. **Open Pro Tools**

2. **Set up MIDI Output (Method 1 - Easiest):**
   - Go to **Setup** → **Peripherals**
   - Click the **MIDI Controllers** tab
   - Find an empty controller slot
   - Set **Type:** to **HUI**
   - Set **Send To:** to **Recording Light Controller**
   - Check **Enable** and click **OK**

3. **Alternative Method - MIDI Track:**
   - Create a new **MIDI Track**
   - Set the track output to **"Recording Light Controller"**
   - The system will automatically detect Pro Tools play/record state

4. **Test it out:**
   - Click **Record Enable** on any track (red R button)
   - Click **Play** - **Your lights should turn ON!** 🎉
   - Click **Stop** - **Your lights should turn OFF!** ✨

**That's it!** Your lights will automatically turn on when you're recording and off when you stop.

**Need more detailed setup?** See `PRO_TOOLS_SETUP.md` for advanced configuration options.

## 🎉 You're Done! How to Use

**Normal Operation:**
- Just use Pro Tools like normal
- When you press **Record + Play**: Lights turn **ON**
- When you press **Stop**: Lights turn **OFF**  
- The system runs automatically in the background

**The system will:**
- ✅ Start automatically when you turn on your Mac
- ✅ Work with any Pro Tools project
- ✅ Turn lights on ONLY when you're actually recording
- ✅ Turn lights off immediately when you stop

## 🔧 Testing Your Setup

**Test your lights manually:**
```bash
cd ~/Documents/Pro-Tools-Smart-Light
source venv/bin/activate           # Activate virtual environment first
./manual_control.py --action on    # Turn all lights ON
./manual_control.py --action off   # Turn all lights OFF
```

**Test individual components:**
```bash
source venv/bin/activate  # Activate virtual environment first
./test_devices.py         # Test if your lights respond
./test_midi.py           # Test if MIDI is working
```

## ❓ Troubleshooting

**"Permission denied" when running setup:**
```bash
chmod +x setup.sh
./setup.sh
```

**Lights don't respond:**
- Make sure your lights are connected to Wi-Fi and working in the Kasa app
- Check that your Mac and lights are on the same Wi-Fi network  
- Try turning lights on/off manually: `./manual_control.py --action on`

**Pro Tools doesn't see "Recording Light Controller":**
- Restart Pro Tools after running the setup
- Check if the system is running: `launchctl list | grep recordinglights`

**Need help?** Check the log files in your project folder:
- Look at `recording_lights.log` for error messages
- Run `./test_devices.py` to check if your lights work

## 🔧 Advanced Options

**Add more lights:** Edit `config.json` and add more devices to the list.

**Control lights manually:**
```bash
./manual_control.py --action on --device "Studio Light 1"   # Turn on one light
./manual_control.py --list                                   # See all your lights
```

**Restart the system:**
```bash
launchctl stop com.studio.recordinglights
launchctl start com.studio.recordinglights
```

**Remove everything completely:**
```bash
launchctl unload ~/Library/LaunchAgents/com.studio.recordinglights.plist
rm ~/Library/LaunchAgents/com.studio.recordinglights.plist
rm -rf ~/Documents/Pro-Tools-Smart-Light
```

## 💡 About This System

**What does the setup install?**
- Python libraries: `python-kasa` (to talk to TP-Link devices) and `python-rtmidi` (to talk to Pro Tools)
- A background service that starts automatically when you boot your Mac
- A virtual MIDI port that Pro Tools can send messages to

**Is it safe?** 
- Yes! Everything runs locally on your Mac
- No internet required after setup
- Only communicates with your local Wi-Fi devices

**Will it slow down my Mac?**
- No! It uses virtually no CPU or memory when running
- Only activates when Pro Tools sends MIDI messages

---

🎵 **Enjoy your automated recording studio lights!** 🎵

*Having issues? Check the troubleshooting section above or create an issue on GitHub.* 
