#!/usr/bin/env python3
"""
MIDI Test Script for Recording Light Controller
Tests MIDI virtual port creation and message reception
"""

import rtmidi
import time
import sys

def test_midi_port():
    """Test MIDI virtual port creation and monitoring"""
    print("MIDI Virtual Port Test")
    print("=" * 50)
    
    try:
        # Create MIDI input
        midi_in = rtmidi.MidiIn()
        port_name = "Recording Light Controller (Test)"
        
        # Open virtual port
        midi_in.open_virtual_port(port_name)
        print(f"✓ Virtual MIDI port '{port_name}' created successfully")
        print("\nThe port should now be visible in:")
        print("  - Pro Tools MIDI setup")
        print("  - Audio MIDI Setup application")
        print("\nWaiting for MIDI messages...")
        print("Send CC 117 (Play/Stop) or CC 118 (Record) to test")
        print("Press Ctrl+C to exit\n")
        
        # Monitor for messages
        while True:
            msg = midi_in.get_message()
            if msg:
                message, delta_time = msg
                
                if len(message) >= 3:
                    status, cc_number, value = message[0], message[1], message[2]
                    
                    # Decode message type
                    if status == 176:  # CC message
                        print(f"CC {cc_number}: {value}", end="")
                        
                        if cc_number == 117:
                            print(f" - Play {'ON' if value > 0 else 'OFF'}")
                        elif cc_number == 118:
                            print(f" - Record {'ENABLED' if value > 0 else 'DISABLED'}")
                        else:
                            print(" - Other CC")
                    else:
                        print(f"Other MIDI: {message}")
                else:
                    print(f"Short message: {message}")
                    
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    finally:
        if 'midi_in' in locals():
            midi_in.close_port()
            del midi_in
            print("MIDI port closed")
            
    return True

def list_midi_ports():
    """List all available MIDI ports"""
    print("\nAvailable MIDI Ports:")
    print("-" * 30)
    
    try:
        midi_in = rtmidi.MidiIn()
        midi_out = rtmidi.MidiOut()
        
        # Input ports
        print("Input Ports:")
        if midi_in.get_port_count() == 0:
            print("  No input ports found")
        else:
            for i in range(midi_in.get_port_count()):
                print(f"  {i}: {midi_in.get_port_name(i)}")
                
        # Output ports
        print("\nOutput Ports:")
        if midi_out.get_port_count() == 0:
            print("  No output ports found")
        else:
            for i in range(midi_out.get_port_count()):
                print(f"  {i}: {midi_out.get_port_name(i)}")
                
    except Exception as e:
        print(f"Error listing ports: {e}")

if __name__ == "__main__":
    print("Recording Light Controller - MIDI Test\n")
    
    # List existing ports
    list_midi_ports()
    
    print("\n" + "=" * 50)
    print("Creating test MIDI port...")
    print("=" * 50 + "\n")
    
    # Test virtual port
    test_midi_port() 