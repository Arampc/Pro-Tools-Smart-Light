#!/usr/bin/env python3
"""
Test script to verify TP-Link device connectivity
"""

import asyncio
import sys
from kasa import Discover, SmartDevice

async def test_devices():
    """Discover and test all TP-Link devices on the network"""
    print("Discovering TP-Link devices on the network...")
    print("-" * 60)
    
    try:
        devices = await Discover.discover()
        
        if not devices:
            print("No TP-Link devices found on the network.")
            print("\nTroubleshooting tips:")
            print("1. Ensure devices are powered on")
            print("2. Check that devices are connected to Wi-Fi network '624'")
            print("3. Ensure your Mac is on the same network")
            print("4. Try power cycling the devices")
            return
        
        print(f"Found {len(devices)} device(s):\n")
        
        # Expected device IDs
        expected_devices = {
            "8006760185751EF6BC07278FBBFDBFE118D0045A": "Recording Light 1 (Green Room)",
            "8006AF4E0F1D4E8B792E8FE90811A3AA173D9829": "Recording Light 2 (Lounge)",
            "8006675E37F7EBCB85C54FA0FC664D3817413EF6": "Recording Light 3 (Jim's Office)",
            "800644F8993DD132DC7A7416750BB39A18B1A134": "Recording Light 4 (Vestibule)",
            "80122FDBDF3FD96AE2E179F581E7171C1E8C9A2A": "Recording Light 5 (Drum Room)",
            "8012D9D1E1961AFD70E7FB42B105DF051E89BD5F": "Recording Light 6 (Vocal Booth)"
        }
        
        found_expected = []
        unexpected = []
        
        for ip, device in devices.items():
            await device.update()
            
            device_info = {
                'ip': ip,
                'alias': device.alias,
                'model': device.model,
                'device_id': device.device_id,
                'is_on': device.is_on,
                'device_type': device.device_type.name
            }
            
            if device.device_id in expected_devices:
                device_info['expected_name'] = expected_devices[device.device_id]
                found_expected.append(device_info)
            else:
                unexpected.append(device_info)
            
            # Print device info
            print(f"Device: {device.alias}")
            print(f"  IP Address: {ip}")
            print(f"  Model: {device.model}")
            print(f"  Type: {device.device_type.name}")
            print(f"  Device ID: {device.device_id}")
            print(f"  Status: {'ON' if device.is_on else 'OFF'}")
            
            if device.device_id in expected_devices:
                print(f"  ✓ Expected: {expected_devices[device.device_id]}")
            else:
                print(f"  ! Unexpected device")
            
            print()
        
        # Summary
        print("-" * 60)
        print("SUMMARY:")
        print(f"Expected devices found: {len(found_expected)}/{len(expected_devices)}")
        
        # List missing devices
        missing_ids = set(expected_devices.keys()) - {d['device_id'] for d in found_expected}
        if missing_ids:
            print("\nMissing devices:")
            for device_id in missing_ids:
                print(f"  ✗ {expected_devices[device_id]}")
        
        if unexpected:
            print(f"\nUnexpected devices found: {len(unexpected)}")
            for device in unexpected:
                print(f"  - {device['alias']} ({device['ip']})")
        
        # Test turning devices on/off
        if found_expected and input("\nTest turning all found devices ON and OFF? (y/n): ").lower() == 'y':
            print("\nTurning all devices ON...")
            for device_info in found_expected:
                device = await Discover.discover_single(device_info['ip'])
                await device.turn_on()
                print(f"  ✓ {device_info['alias']} turned ON")
            
            await asyncio.sleep(2)
            
            print("\nTurning all devices OFF...")
            for device_info in found_expected:
                device = await Discover.discover_single(device_info['ip'])
                await device.turn_off()
                print(f"  ✓ {device_info['alias']} turned OFF")
            
            print("\nTest complete!")
        
    except Exception as e:
        print(f"Error during device discovery: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your network connection")
        print("2. Ensure Python has network access")
        print("3. Try disabling firewall temporarily")
        print("4. Check if devices respond to the Kasa app")

if __name__ == "__main__":
    print("TP-Link Device Connectivity Test")
    print("=" * 60)
    asyncio.run(test_devices()) 