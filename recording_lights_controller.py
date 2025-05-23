#!/usr/bin/env python3
"""
Pro Tools Recording Light Controller
Monitors Pro Tools recording state via MIDI and controls TP-Link smart lights
"""

import asyncio
import sys
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import rtmidi
from kasa import SmartDevice, SmartBulb, SmartPlug, Discover

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recording_lights.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# MIDI Constants
CC_CODE = 176  # Control Change message
CC_RECORD = 118  # CC for record enable/disable
CC_PLAY = 117   # CC for play/pause
DEBOUNCE_TIME_SECONDS = 0.25  # Debounce time for MIDI events

@dataclass
class DeviceConfig:
    """Configuration for a smart device"""
    name: str
    location: str
    device_type: str
    device_id: str
    ip_address: Optional[str] = None

class RecordingLightController:
    """Controls TP-Link smart lights based on Pro Tools recording state via MIDI"""
    
    def __init__(self):
        self.devices: Dict[str, SmartDevice] = {}
        self.device_configs = [
            DeviceConfig("Recording Light 1", "Green Room", "Socket", "8006760185751EF6BC07278FBBFDBFE118D0045A"),
            DeviceConfig("Recording Light 2", "Lounge", "Socket", "8006AF4E0F1D4E8B792E8FE90811A3AA173D9829"),
            DeviceConfig("Recording Light 3", "Jim's Office", "Socket", "8006675E37F7EBCB85C54FA0FC664D3817413EF6"),
            DeviceConfig("Recording Light 4", "Vestibule", "Socket", "800644F8993DD132DC7A7416750BB39A18B1A134"),
            DeviceConfig("Recording Light 5", "Drum Room", "Bulb", "80122FDBDF3FD96AE2E179F581E7171C1E8C9A2A"),
            DeviceConfig("Recording Light 6", "Vocal Booth", "Bulb", "8012D9D1E1961AFD70E7FB42B105DF051E89BD5F"),
        ]
        
        # MIDI state
        self.midi_in = None
        self.record_enabled = False
        self.playing = False
        self.scheduled_task = None
        
        # CC action mapping
        self.cc_action_map = {
            CC_RECORD: self.on_record_changed,
            CC_PLAY: self.on_play_changed
        }
        
    async def discover_devices(self):
        """Discover TP-Link devices on the network"""
        logger.info("Discovering TP-Link devices on the network...")
        try:
            devices = await Discover.discover()
            logger.info(f"Found {len(devices)} devices")
            
            # Match discovered devices with our configuration
            for ip, device in devices.items():
                await device.update()
                device_id = device.device_id
                
                for config in self.device_configs:
                    if config.device_id == device_id:
                        config.ip_address = ip
                        if config.device_type == "Socket":
                            self.devices[config.name] = SmartPlug(ip)
                        else:  # Bulb
                            self.devices[config.name] = SmartBulb(ip)
                        logger.info(f"Matched {config.name} ({config.location}) at {ip}")
                        break
            
            # Check if all devices were found
            missing_devices = [c for c in self.device_configs if c.ip_address is None]
            if missing_devices:
                logger.warning(f"Could not find {len(missing_devices)} devices:")
                for device in missing_devices:
                    logger.warning(f"  - {device.name} ({device.location})")
                    
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            
    async def turn_all_lights_on(self):
        """Turn on all configured lights"""
        logger.info("Turning on all recording lights...")
        tasks = []
        for name, device in self.devices.items():
            tasks.append(self._turn_device_on(name, device))
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def turn_all_lights_off(self):
        """Turn off all configured lights"""
        logger.info("Turning off all recording lights...")
        tasks = []
        for name, device in self.devices.items():
            tasks.append(self._turn_device_off(name, device))
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def _turn_device_on(self, name: str, device: SmartDevice):
        """Turn on a single device"""
        try:
            await device.turn_on()
            logger.info(f"Turned on {name}")
        except Exception as e:
            logger.error(f"Failed to turn on {name}: {e}")
            
    async def _turn_device_off(self, name: str, device: SmartDevice):
        """Turn off a single device"""
        try:
            await device.turn_off()
            logger.info(f"Turned off {name}")
        except Exception as e:
            logger.error(f"Failed to turn off {name}: {e}")
            
    def setup_midi(self):
        """Setup MIDI virtual port for Pro Tools communication"""
        try:
            self.midi_in = rtmidi.MidiIn()
            port_name = "Recording Light Controller"
            self.midi_in.open_virtual_port(port_name)
            logger.info(f"MIDI virtual port '{port_name}' created successfully")
            logger.info("Configure Pro Tools to send MIDI CC to this port:")
            logger.info("  - CC 117 for Play/Stop")
            logger.info("  - CC 118 for Record Enable/Disable")
            return True
        except Exception as e:
            logger.error(f"Failed to create MIDI virtual port: {e}")
            return False
            
    async def schedule_debounced_light_change(self, lights_on: bool):
        """Schedule a debounced light change to handle out-of-order MIDI events"""
        # Cancel any existing scheduled task
        if self.scheduled_task:
            self.scheduled_task.cancel()
            
        # Schedule new task
        self.scheduled_task = asyncio.create_task(self._debounced_light_change(lights_on))
        
    async def _debounced_light_change(self, lights_on: bool):
        """Execute light change after debounce period"""
        await asyncio.sleep(DEBOUNCE_TIME_SECONDS)
        
        if lights_on:
            await self.turn_all_lights_on()
        else:
            await self.turn_all_lights_off()
            
    def on_play_changed(self, midi_value: int):
        """Handle play/pause state change"""
        self.playing = midi_value > 0
        logger.debug(f"Play state changed: {'Playing' if self.playing else 'Stopped'}")
        
        # Only change lights if we're in record mode
        if self.record_enabled:
            asyncio.create_task(self.schedule_debounced_light_change(self.playing))
            
    def on_record_changed(self, midi_value: int):
        """Handle record enable/disable state change"""
        self.record_enabled = midi_value > 0
        logger.debug(f"Record state changed: {'Enabled' if self.record_enabled else 'Disabled'}")
        
        # Only turn on lights if we're also playing
        if self.playing:
            asyncio.create_task(self.schedule_debounced_light_change(self.record_enabled))
        elif self.record_enabled:
            # If record is armed but not playing yet, prepare for recording
            logger.info("Record armed - lights will turn on when playback starts")
            
    def process_midi_message(self, message):
        """Process incoming MIDI message"""
        if len(message) < 3:
            return
            
        status, cc_number, value = message[0], message[1], message[2]
        
        # Only process CC messages
        if status != CC_CODE:
            return
            
        # Check if we have an action for this CC
        if cc_number in self.cc_action_map:
            logger.debug(f"MIDI CC {cc_number} received with value {value}")
            self.cc_action_map[cc_number](value)
            
    async def monitor_midi(self):
        """Main MIDI monitoring loop"""
        logger.info("Starting MIDI monitoring...")
        logger.info("Waiting for Pro Tools MIDI messages...")
        
        while True:
            try:
                # Get MIDI message (non-blocking)
                msg = self.midi_in.get_message()
                
                if msg:
                    message, delta_time = msg
                    self.process_midi_message(message)
                    
                # Small sleep to prevent CPU spinning
                await asyncio.sleep(0.005)
                
            except KeyboardInterrupt:
                logger.info("MIDI monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in MIDI monitoring: {e}")
                await asyncio.sleep(1)
                
    async def run(self):
        """Main entry point"""
        logger.info("Recording Light Controller starting...")
        
        # Discover devices
        await self.discover_devices()
        
        if not self.devices:
            logger.error("No devices found! Please check your network connection and device configuration.")
            return
            
        logger.info(f"Successfully connected to {len(self.devices)} devices")
        
        # Setup MIDI
        if not self.setup_midi():
            logger.error("Failed to setup MIDI. Exiting...")
            return
            
        # Start monitoring
        try:
            await self.monitor_midi()
        finally:
            # Cleanup
            if self.midi_in:
                self.midi_in.close_port()
                del self.midi_in
                logger.info("MIDI port closed")

async def main():
    """Main function"""
    controller = RecordingLightController()
    await controller.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
