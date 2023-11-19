#!/usr/bin/env python3
import mido
import sys
from collections import defaultdict
import time
import threading
import time
import json

# Constants
DOUBLE_TAP_THRESHOLD = 0.5  # Adjust this threshold as needed (in seconds)
class Press:
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3

print(mido.get_input_names())

input_port_name = "SY-1000"  # Replace with your MIDI input port name
input_port_name2 = "SY-1000 DAW CTRL"  # Replace with your MIDI input port name
input_port_name3 = "IAC Driver Automation"
output_port_name = "IAC Driver Bus 1"  # Replace with your MIDI output port name

output = mido.open_output(output_port_name)
output2 = mido.open_output(input_port_name)


def load_state_from_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data['array1'], data['array2'], data['array3'], data['array4']
    except FileNotFoundError:
        # Return default arrays if file not found
        return [1], [2], [3], [4]

def save_state_to_json(filename, array1, array2, array3, array4):
    data = {'array1': array1, 'array2': array2, 'array3': array3, 'array4': array4}
    with open(filename, 'w') as file:
        json.dump(data, file)

def update_array(arrays, array_index, element_index, new_value):
    # Ensure the array is large enough
    while len(arrays[array_index]) <= element_index:
        arrays[array_index].append(array_index)  # Append None or a default value
    # Update the element
    arrays[array_index][element_index] = new_value
    # Save the updated state
    save_state_to_json('arrays.json', *arrays)


# Load the arrays
array1, array2, array3, array4 = load_state_from_json('arrays.json')
arrays = [array1, array2, array3, array4]

# Example of updating an element (array index, element index, new value)
update_array(arrays, 0, 2, 100)  # Update 3rd element of the 1st array

def make_title_sysex(input_name):
    input_data = input_name.ljust(16)
    # Convert input characters to a list of ASCII values
    ascii_values = [ord(char) for char in input_data]

    # Additional data
    manufacturer_id = 0x41
    additional_data_1 = [0x10, 0x00, 0x00, 0x00, 0x69, 0x12]
    additional_data_2 = [0x10, 0x00, 0x00, 0x00]

    # Create the SysEx message
    sysex_message = [manufacturer_id]
    sysex_message.extend(additional_data_1)
    sysex_message.extend(additional_data_2)
    sysex_message.extend(ascii_values)
    checksum = calculate_checksum(ascii_values + additional_data_2)
    sysex_message.append(checksum)
    print(f"sending message {input_data}")
    return sysex_message

def calculate_checksum(data):
    checksum = 128 - (sum(data) % 128)
    return checksum

def make_color_sysex_patch(button, color):
    data=[0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12]
    data2=[0x10, 0x00, 0x03, button, color]
    sysex = data+data2+[calculate_checksum(data2)]
    return sysex

def make_color_sysex_system(button, color):
    data=[0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12]
    data2=[0x00, 0x01, 0x20, button, color]
    sysex = data+data2+[calculate_checksum(data2)]
    return sysex

def send_messages_after_delay(port, messages, delay):
    for msg in messages:
        # print(f"Waiting for {delay} seconds before sending the SysEx message...")
        port.send(msg)  # Send the SysEx message
        time.sleep(delay)  # Delay before sending the message
        port.send(msg)  # Send the SysEx message
        # print("SysEx message sent.")

def get_char_for_number(number):
    # ASCII value of 'A' is 65, subtract the number from 65 to get the desired ASCII value
    ascii_value = 65 - number
    # Convert the ASCII value back to a character
    return chr(ascii_value)

def bank_change(number):
    global bank_number
    bank_number = number
    if (number > 0):
        output2.send(mido.Message('sysex', data=make_title_sysex("bank "+str(number))))
    else:
        output2.send(mido.Message('sysex', data=make_title_sysex("bank "+get_char_for_number(number))))

def program_change(number):
    global program_number
    program_number = number
    print("program change: {}".format(number))
    button = (number - 1) % 4 + 1
    print("button: {}, program change: {}".format(button, number))
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x00, 0x01, 0x10, 0x00, 0x8 if button == 1 else 0x00, 0x67 if button == 1 else 0x6F]))
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x00, 0x01, 0x10, 0x02, 0x8 if button == 2 else 0x00, 0x65 if button == 2 else 0x6D]))
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x00, 0x01, 0x10, 0x04, 0x8 if button == 3 else 0x00, 0x63 if button == 3 else 0x6B]))
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x00, 0x01, 0x10, 0x06, 0x8 if button == 4 else 0x00, 0x61 if button == 4 else 0x69]))
    output.send(mido.Message('program_change', program=number-1))

def main():
    global was
    global bank_number
    program_number = 1
    bank_number = 1
    was = None

    program_change(1)
    # what is this?
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x7F, 0x00, 0x00, 0x01, 0x01, 0x7F]))

    # Define a function to handle MIDI messages
    def handle_midi_message(msg):
        if not msg:
            return
        global program_number
        if msg.type == 'control_change':
            cc_number = msg.control
            timestamp = time.time()
            if cc_number == 10 and msg.value == 0 and len(cc_history[cc_number]) > 0 and timestamp - cc_history[cc_number][-1] > 2 * DOUBLE_TAP_THRESHOLD:
                output.send(mido.Message('control_change', control=1, value = 127))
                output.send(mido.Message('control_change', control=1, value = 0))
                program_number = program_number//5*4 + 1 if (program_number%5==4) else 4
                program_change(program_number)
            if cc_callback[cc_number] is not None:
                cc_callback[cc_number](cc_number, msg.value)
            if msg.value == 127:
                if cc_single_callback[cc_number] is not None:
                    cc_single_callback[cc_number](cc_number, msg.value, Press.SINGLE)
                if cc_history[cc_number] is None:
                    cc_history[cc_number] = []
                cc_history[cc_number].append(timestamp)
                cc_history[cc_number] = cc_history[cc_number][-3:]  # Keep only the last 3 timestamps

                # Check for triple tap
                if len(cc_history[cc_number]) == 3 and cc_history[cc_number][-1] - cc_history[cc_number][0] < 2 * DOUBLE_TAP_THRESHOLD:
                    if cc_triple_callback[cc_number] is not None:
                        cc_triple_callback[cc_number](cc_number, msg.value, Press.TRIPLE)
                    cc_history[cc_number] = []
                # Check for double tap (only if triple tap was not detected)
                elif len(cc_history[cc_number]) >= 2 and cc_history[cc_number][-1] - cc_history[cc_number][-2] < DOUBLE_TAP_THRESHOLD:
                    if cc_double_callback[cc_number] is not None:
                        cc_double_callback[cc_number](cc_number, msg.value, Press.DOUBLE)

    def pulse_cc(cc_number):
        output.send(mido.Message('control_change', control=1, value = 127))
        output.send(mido.Message('control_change', control=1, value = 0))

    def cc_10_callback(cc_number, value, tap):
        global program_number, was
        print("cc 10 {}".format(tap))
        match tap:
            case Press.SINGLE:
                pulse_cc(1)
            case Press.DOUBLE:
                was = program_number
                program_change(program_number//5*4 + 1 if (program_number%5==2) else 2)
            case Press.TRIPLE:
                pulse_cc(1)
                program_change(program_number//5*4 + 1 if (was%5==3) else 3)

    def color_callback(cc_number, value):
            button_hex = 0x08 + 2 * (cc_number - 41)
            if value < 8:
                print(f"color {cc_number}: {value}")
                threading.Thread(target=send_messages_after_delay, args=(output2, [mido.Message('sysex', data=make_color_sysex_patch(button_hex, value)), mido.Message('sysex', data=make_color_sysex_patch(button_hex+1, value))], 0.3)).start()

    # Define a callback function for a specific CC number
    def patch_callback(cc_number, value, tap):
        global program_number
        global bank_number
        if (bank_number > 0):
            program_change((bank_number-1)*4 + cc_number - 70)
        else:
            program_change(array1[bank_number] or cc_number - 70)

    # Create a dictionary to store callback functions for each CC number
    cc_callback = defaultdict(lambda: None)
    cc_single_callback = defaultdict(lambda: None)
    cc_double_callback = defaultdict(lambda: None)
    cc_triple_callback = defaultdict(lambda: None)

    cc_single_callback[10] = cc_10_callback
    cc_triple_callback[10] = cc_10_callback
    cc_double_callback[10] = cc_10_callback
    cc_double_callback[3] = lambda cc_number, value, tap: bank_change(bank_number + 1)
    cc_double_callback[4] = lambda cc_number, value, tap: bank_change(bank_number - 1)
    cc_callback[41] = color_callback
    cc_callback[42] = color_callback
    cc_callback[43] = color_callback
    cc_callback[44] = color_callback
    cc_single_callback[71] = patch_callback
    cc_single_callback[72] = patch_callback
    cc_single_callback[73] = patch_callback
    cc_single_callback[74] = patch_callback

    # Create a dictionary to store the last timestamp for each CC number
    cc_history = defaultdict(lambda: None)

    if False:
        # async
        # Open a MIDI input port (change 'Your MIDI Input Port' to your actual port name)
        mido.open_input(name=input_port_name, callback=handle_midi_message)
        mido.open_input(name=input_port_name2, callback=handle_midi_message)
        mido.open_input(name=input_port_name3, callback=handle_midi_message)
    else:
        # polling
        open_ports = []
        open_ports.append(mido.open_input(name=input_port_name))
        open_ports.append(mido.open_input(name=input_port_name2))
        open_ports.append(mido.open_input(name=input_port_name3))
        while True:
            for port in open_ports:
                handle_midi_message(port.poll())

    # Keep the program running until the user presses CTRL+C
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting program...")

if __name__ == "__main__":
    main()

