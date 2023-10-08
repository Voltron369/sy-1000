#!/usr/bin/env python3
import mido
import sys
from collections import defaultdict
import time

input_port_name = "SY-1000 DAW CTRL"  # Replace with your MIDI input port name
output_port_name = "IAC Driver Bus 1"  # Replace with your MIDI output port name

output = mido.open_output(output_port_name)
output2 = mido.open_output(input_port_name)

program_number = 1;

def calculate_checksum(data):
    checksum = 128 - (sum(data) % 128)
    return checksum

def program_change(number):
    print("program change: {}".format(number))
    button = (number - 1) % 4 + 1
    print("button: {}, program change: {}".format(button, number))
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x00, 0x01, 0x10, 0x00, 0x8 if button == 1 else 0x00, 0x67 if button == 1 else 0x6F]))
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x00, 0x01, 0x10, 0x02, 0x8 if button == 2 else 0x00, 0x65 if button == 2 else 0x6D]))
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x00, 0x01, 0x10, 0x04, 0x8 if button == 3 else 0x00, 0x63 if button == 3 else 0x6B]))
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x00, 0x01, 0x10, 0x06, 0x8 if button == 4 else 0x00, 0x61 if button == 4 else 0x69]))
    output.send(mido.Message('program_change', program=number-1))

def main():
    # Define the MIDI input and output ports

    program_change(program_number)

    # Define a function to handle MIDI messages
    def handle_midi_message(msg):
        if msg.type == 'control_change':
            cc_number = msg.control
            if msg.value == 127:
                timestamp = time.time()
                if cc_callback[cc_number] is not None:
                    cc_callback[cc_number](cc_number)
                # Check for double tap on the same CC number
                if cc_history[cc_number] is None:
                    cc_history[cc_number] = timestamp
                elif timestamp - cc_history[cc_number] < DOUBLE_TAP_THRESHOLD:
                    if cc_double_callback[cc_number] is not None:
                        cc_double_callback[cc_number](cc_number)
                    cc_history[cc_number] = None
                else:
                    cc_history[cc_number] = timestamp

    # Define a callback function for a specific CC number
    def my_callback(cc_number):
        global program_number
        match cc_number:
            case 3:
                print('bank down')
                if program_number > 4:
                    program_number -= 4
                    program_change(program_number)
            case 4:
                print('bank up')
                program_number += 4
                program_change(program_number)
            case 71:
                print('1')
                program_number = program_number//5*4 + 1
                program_change(program_number)
            case 72:
                print('2')
                program_number = program_number//5*4 + 2
                program_change(program_number)
            case 73:
                print('3')
                program_number = program_number//5*4 + 3
                program_change(program_number)
            case 74:
                print('4')
                program_number = program_number//5*4 + 4
                program_change(program_number)

    # Constants
    DOUBLE_TAP_THRESHOLD = 0.5  # Adjust this threshold as needed (in seconds)

    # Create a dictionary to store callback functions for each CC number
    cc_callback = defaultdict(lambda: None)
    cc_double_callback = defaultdict(lambda: None)
    cc_double_callback[3] = my_callback
    cc_double_callback[4] = my_callback
    cc_callback[71] = my_callback
    cc_callback[72] = my_callback
    cc_callback[73] = my_callback
    cc_callback[74] = my_callback

    # Create a dictionary to store the last timestamp for each CC number
    cc_history = defaultdict(lambda: None)

    # Open a MIDI input port (change 'Your MIDI Input Port' to your actual port name)
    with mido.open_input(input_port_name) as inport:
        print('Listening for MIDI messages...')
        try:
            for msg in inport:
                handle_midi_message(msg)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()

