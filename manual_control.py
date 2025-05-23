#!/usr/bin/env python3
"""
Manual control script for recording lights
Useful for testing and manual override
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Optional
from kasa import SmartDevice, SmartBulb, SmartPlug, Discover

async def load_device_config() -> list:
    """Load device configuration from config.json"""
    try:
        config_path = Path("config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('devices', [])
    except FileNotFoundError:
        print("Error: config.json not found")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json")
        return []

async def discover_and_match_devices(device_configs: list) -> Dict[str, SmartDevice]:
    """Discover and match devices with configuration"""
    print("Discovering devices...")
    devices = {}
    
    try:
        discovered = await Discover.discover()
        print(f"Found {len(discovered)} devices on network")
        
        for ip, device in discovered.items():
            await device.update()
            device_id = device.device_id
            
            for config in device_configs:
                if config['device_id'] == device_id:
                    device_type = config['type'].lower()
                    if device_type == "socket":
                        devices[config['name']] = SmartPlug(ip)
                    elif device_type == "bulb":
                        devices[config['name']] = SmartBulb(ip)
                    print(f"✓ Found {config['name']} ({config['location']}) at {ip}")
                    break
                    
    except Exception as e:
        print(f"Error discovering devices: {e}")
        
    return devices

async def control_all_devices(devices: Dict[str, SmartDevice], turn_on: bool) -> None:
    """Turn all devices on or off"""
    if not devices:
        print("No devices to control")
        return
        
    action = "ON" if turn_on else "OFF"
    print(f"Turning all lights {action}...")
    
    tasks = []
    for name, device in devices.items():
        tasks.append(control_single_device(name, device, turn_on))
    
    await asyncio.gather(*tasks, return_exceptions=True)

async def control_single_device(name: str, device: SmartDevice, turn_on: bool) -> None:
    """Control a single device"""
    try:
        if turn_on:
            await device.turn_on()
            print(f"  ✓ {name} turned ON")
        else:
            await device.turn_off()
            print(f"  ✓ {name} turned OFF")
    except Exception as e:
        action = "turn on" if turn_on else "turn off"
        print(f"  ✗ Failed to {action} {name}: {e}")

async def main():
    """Main function for manual control"""
    print("Recording Lights Manual Control")
    print("=" * 40)
    
    # Load configuration
    device_configs = await load_device_config()
    if not device_configs:
        print("No device configuration found. Please check config.json")
        return
        
    # Discover devices
    devices = await discover_and_match_devices(device_configs)
    
    if not devices:
        print("No devices found! Please check your network connection.")
        print("\nTroubleshooting tips:")
        print("- Ensure devices are powered on")
        print("- Check devices are on the same network")
        print("- Try power cycling the devices")
        return
    
    print(f"\nConnected to {len(devices)} devices")
    print("\nCommands:")
    print("  on  - Turn all lights ON")
    print("  off - Turn all lights OFF")
    print("  list - List connected devices")
    print("  exit - Exit the program")
    print("=" * 40)
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command == "on":
                await control_all_devices(devices, True)
            elif command == "off":
                await control_all_devices(devices, False)
            elif command == "list":
                print("\nConnected devices:")
                for name in devices.keys():
                    print(f"  - {name}")
            elif command == "exit":
                print("Exiting...")
                break
            else:
                print("Invalid command. Use: on, off, list, or exit")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 