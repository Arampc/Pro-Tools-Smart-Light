#!/usr/bin/env python3
"""
Manual control script for recording lights
Useful for testing and manual override
"""

import asyncio
import sys
from recording_lights_controller import RecordingLightController

async def main():
    """Main function for manual control"""
    controller = RecordingLightController()
    
    print("Recording Lights Manual Control")
    print("=" * 40)
    print("Commands:")
    print("  on  - Turn all lights ON")
    print("  off - Turn all lights OFF")
    print("  exit - Exit the program")
    print("=" * 40)
    
    # Discover devices first
    await controller.discover_devices()
    
    if not controller.devices:
        print("No devices found! Please check your network connection.")
        return
    
    print(f"\nConnected to {len(controller.devices)} devices")
    
    while True:
        try:
            command = input("\nEnter command (on/off/exit): ").strip().lower()
            
            if command == "on":
                await controller.turn_all_lights_on()
            elif command == "off":
                await controller.turn_all_lights_off()
            elif command == "exit":
                print("Exiting...")
                break
            else:
                print("Invalid command. Please use 'on', 'off', or 'exit'.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 