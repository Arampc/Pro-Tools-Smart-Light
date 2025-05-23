#!/usr/bin/env python3
"""
Pro Tools Recording Light Controller
Monitors Pro Tools recording state via MIDI and controls TP-Link smart lights
"""

import asyncio
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
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

@dataclass
class DeviceConfig:
    """Configuration for a smart device"""
    name: str
    location: str
    device_type: str
    device_id: str
    ip_address: Optional[str] = None

@dataclass 
class MidiConfig:
    """MIDI configuration settings"""
    port_name: str
    cc_play: int
    cc_record: int
    debounce_time: float

@dataclass
class NetworkConfig:
    """Network configuration settings"""
    wifi_network: str
    discovery_timeout: int

class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass

class MidiError(Exception):
    """Raised when MIDI operations fail"""
    pass

class Configuration:
    """Handles loading and validation of configuration"""
    
    def __init__(self, config_path: Union[str, Path] = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()
        
    def _load_config(self) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
            
    def _validate_config(self) -> None:
        """Validate configuration structure"""
        required_sections = ['midi', 'network', 'devices']
        for section in required_sections:
            if section not in self.config:
                raise ConfigurationError(f"Missing required section: {section}")
                
        # Validate devices
        if not self.config['devices']:
            raise ConfigurationError("No devices configured")
            
        for device in self.config['devices']:
            required_fields = ['name', 'location', 'type', 'device_id']
            for field in required_fields:
                if field not in device:
                    raise ConfigurationError(f"Device missing required field: {field}")
                    
    @property
    def midi(self) -> MidiConfig:
        """Get MIDI configuration"""
        midi_config = self.config['midi']
        return MidiConfig(
            port_name=midi_config['port_name'],
            cc_play=midi_config['cc_play'],
            cc_record=midi_config['cc_record'],
            debounce_time=midi_config['debounce_time']
        )
        
    @property
    def network(self) -> NetworkConfig:
        """Get network configuration"""
        network_config = self.config['network']
        return NetworkConfig(
            wifi_network=network_config['wifi_network'],
            discovery_timeout=network_config['discovery_timeout']
        )
        
    @property
    def devices(self) -> List[DeviceConfig]:
        """Get device configurations"""
        return [
            DeviceConfig(
                name=device['name'],
                location=device['location'],
                device_type=device['type'],
                device_id=device['device_id']
            )
            for device in self.config['devices']
        ]

class DeviceManager:
    """Manages smart device discovery and control"""
    
    def __init__(self, device_configs: List[DeviceConfig]):
        self.device_configs = device_configs
        self.devices: Dict[str, SmartDevice] = {}
        
    async def discover_devices(self) -> None:
        """Discover TP-Link devices on the network"""
        logger.info("Discovering TP-Link devices on the network...")
        try:
            devices = await Discover.discover()
            logger.info(f"Found {len(devices)} devices")
            
            await self._match_devices(devices)
            self._log_discovery_results()
                    
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            raise
            
    async def _match_devices(self, discovered_devices: Dict[str, SmartDevice]) -> None:
        """Match discovered devices with configuration"""
        for ip, device in discovered_devices.items():
            await device.update()
            device_id = device.device_id
            
            for config in self.device_configs:
                if config.device_id == device_id:
                    config.ip_address = ip
                    self.devices[config.name] = self._create_device_instance(config, ip)
                    logger.info(f"Matched {config.name} ({config.location}) at {ip}")
                    break
                    
    def _create_device_instance(self, config: DeviceConfig, ip: str) -> SmartDevice:
        """Create appropriate device instance based on type"""
        if config.device_type.lower() == "socket":
            return SmartPlug(ip)
        elif config.device_type.lower() == "bulb":
            return SmartBulb(ip)
        else:
            raise ConfigurationError(f"Unknown device type: {config.device_type}")
            
    def _log_discovery_results(self) -> None:
        """Log device discovery results"""
        missing_devices = [c for c in self.device_configs if c.ip_address is None]
        if missing_devices:
            logger.warning(f"Could not find {len(missing_devices)} devices:")
            for device in missing_devices:
                logger.warning(f"  - {device.name} ({device.location})")
                
    async def control_all_devices(self, turn_on: bool) -> None:
        """Turn all devices on or off"""
        action = "on" if turn_on else "off"
        logger.info(f"Turning {action} all recording lights...")
        
        tasks = [
            self._control_single_device(name, device, turn_on)
            for name, device in self.devices.items()
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def _control_single_device(self, name: str, device: SmartDevice, turn_on: bool) -> None:
        """Control a single device"""
        try:
            if turn_on:
                await device.turn_on()
                logger.info(f"Turned on {name}")
            else:
                await device.turn_off()
                logger.info(f"Turned off {name}")
        except Exception as e:
            action = "turn on" if turn_on else "turn off"
            logger.error(f"Failed to {action} {name}: {e}")

class MidiHandler:
    """Handles MIDI communication and events"""
    
    def __init__(self, midi_config: MidiConfig, device_manager: DeviceManager):
        self.config = midi_config
        self.device_manager = device_manager
        self.midi_in: Optional[rtmidi.MidiIn] = None
        self.record_enabled = False
        self.playing = False
        self.scheduled_task: Optional[asyncio.Task] = None
        
        # CC action mapping
        self.cc_action_map = {
            self.config.cc_record: self._on_record_changed,
            self.config.cc_play: self._on_play_changed
        }
        
    def setup_midi_port(self) -> None:
        """Setup MIDI virtual port for Pro Tools communication"""
        try:
            self.midi_in = rtmidi.MidiIn()
            self.midi_in.open_virtual_port(self.config.port_name)
            logger.info(f"MIDI virtual port '{self.config.port_name}' created successfully")
            logger.info("Configure Pro Tools to send MIDI CC to this port:")
            logger.info(f"  - CC {self.config.cc_play} for Play/Stop")
            logger.info(f"  - CC {self.config.cc_record} for Record Enable/Disable")
        except Exception as e:
            raise MidiError(f"Failed to create MIDI virtual port: {e}")
            
    async def monitor_midi(self) -> None:
        """Main MIDI monitoring loop"""
        logger.info("Starting MIDI monitoring...")
        logger.info("Waiting for Pro Tools MIDI messages...")
        
        try:
            while True:
                msg = self.midi_in.get_message()
                
                if msg:
                    message, delta_time = msg
                    await self._process_midi_message(message)
                    
                await asyncio.sleep(0.005)  # Small sleep to prevent CPU spinning
                
        except Exception as e:
            logger.error(f"Error in MIDI monitoring: {e}")
            raise
            
    async def _process_midi_message(self, message: List[int]) -> None:
        """Process incoming MIDI message"""
        if len(message) < 3:
            return
            
        status, cc_number, value = message[0], message[1], message[2]
        
        # Only process CC messages (176 = 0xB0)
        if status != 176:
            return
            
        # Check if we have an action for this CC
        if cc_number in self.cc_action_map:
            logger.debug(f"MIDI CC {cc_number} received with value {value}")
            await self.cc_action_map[cc_number](value)
            
    async def _on_play_changed(self, midi_value: int) -> None:
        """Handle play/pause state change"""
        self.playing = midi_value > 0
        logger.debug(f"Play state changed: {'Playing' if self.playing else 'Stopped'}")
        
        # Only change lights if we're in record mode
        if self.record_enabled:
            await self._schedule_debounced_light_change(self.playing)
            
    async def _on_record_changed(self, midi_value: int) -> None:
        """Handle record enable/disable state change"""
        self.record_enabled = midi_value > 0
        logger.debug(f"Record state changed: {'Enabled' if self.record_enabled else 'Disabled'}")
        
        # Only turn on lights if we're also playing
        if self.playing:
            await self._schedule_debounced_light_change(self.record_enabled)
        elif self.record_enabled:
            logger.info("Record armed - lights will turn on when playback starts")
            
    async def _schedule_debounced_light_change(self, lights_on: bool) -> None:
        """Schedule a debounced light change to handle out-of-order MIDI events"""
        # Cancel any existing scheduled task
        if self.scheduled_task:
            self.scheduled_task.cancel()
            
        # Schedule new task
        self.scheduled_task = asyncio.create_task(self._debounced_light_change(lights_on))
        
    async def _debounced_light_change(self, lights_on: bool) -> None:
        """Execute light change after debounce period"""
        await asyncio.sleep(self.config.debounce_time)
        await self.device_manager.control_all_devices(lights_on)
        
    def cleanup(self) -> None:
        """Clean up MIDI resources"""
        if self.midi_in:
            self.midi_in.close_port()
            del self.midi_in
            logger.info("MIDI port closed")

class RecordingLightController:
    """Main controller class"""
    
    def __init__(self, config_path: Union[str, Path] = "config.json"):
        try:
            self.config = Configuration(config_path)
            self.device_manager = DeviceManager(self.config.devices)
            self.midi_handler = MidiHandler(self.config.midi, self.device_manager)
        except (ConfigurationError, FileNotFoundError) as e:
            logger.error(f"Configuration error: {e}")
            raise
            
    async def run(self) -> None:
        """Main entry point"""
        logger.info("Recording Light Controller starting...")
        
        try:
            # Discover devices
            await self.device_manager.discover_devices()
            
            if not self.device_manager.devices:
                logger.error("No devices found! Please check your network connection and device configuration.")
                return
                
            logger.info(f"Successfully connected to {len(self.device_manager.devices)} devices")
            
            # Setup MIDI
            self.midi_handler.setup_midi_port()
            
            # Start monitoring
            await self.midi_handler.monitor_midi()
            
        except KeyboardInterrupt:
            logger.info("Application stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            self.midi_handler.cleanup()

async def main() -> None:
    """Main function"""
    try:
        controller = RecordingLightController()
        await controller.run()
    except Exception as e:
        logger.error(f"Failed to start controller: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
