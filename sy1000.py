#!/usr/bin/env python3
import mido
import sys
from collections import defaultdict
import time
import threading
import time

print(mido.get_input_names())

input_port_name = "SY-1000"  # Replace with your MIDI input port name
input_port_name2 = "SY-1000 DAW CTRL"  # Replace with your MIDI input port name
input_port_name3 = "IAC Driver Automation"
output_port_name = "IAC Driver Bus 1"  # Replace with your MIDI output port name

output = mido.open_output(output_port_name)
output2 = mido.open_output(input_port_name)



def calculate_checksum(data):
    checksum = 128 - (sum(data) % 128)
    return checksum

def make_color_sysex(button, color):
    data=[0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12]
    data2=[0x10, 0x00, 0x03, button, color]
    sysex = data+data2+[calculate_checksum(data2)]
    return sysex

def send_messages_after_delay(port, messages, delay):
    for msg in messages:
        print(f"Waiting for {delay} seconds before sending the SysEx message...")
        port.send(msg)  # Send the SysEx message
        time.sleep(delay)  # Delay before sending the message
        port.send(msg)  # Send the SysEx message
        print("SysEx message sent.")


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
    global program_number
    global last_double
    global was
    program_number = 1
    last_double = None
    was = 10

    program_change(program_number)
    output2.send(mido.Message('sysex', data=[ 0x41, 0x10, 0x00, 0x00, 0x00, 0x69, 0x12, 0x7F, 0x00, 0x00, 0x01, 0x01, 0x7F]))

    # Define a function to handle MIDI messages
    def handle_midi_message(msg):
        if not msg:
            return
        if msg.type != 'clock':
            print(msg)
        global program_number
        if msg.type == 'control_change':
            cc_number = msg.control
            if cc_number == 40 and msg.value < 8:
                print(f"40: {msg.value}")
                # output2.send(mido.Message('sysex', data=make_color_sysex(0x0C, msg.value)))
                # output2.send(mido.Message('sysex', data=make_color_sysex(0x0D, msg.value)))
                threading.Thread(target=send_messages_after_delay, args=(output2, [mido.Message('sysex', data=make_color_sysex(0x0F, msg.value))], 0.3)).start()
            if cc_number == 41 and msg.value < 8:
                print(f"41: {msg.value}")
                threading.Thread(target=send_messages_after_delay, args=(output2, [mido.Message('sysex', data=make_color_sysex(0x0E, msg.value))], 0.3)).start()
            if cc_number == 42 and msg.value < 8:
                print(f"42: {msg.value}")
                threading.Thread(target=send_messages_after_delay, args=(output2, [mido.Message('sysex', data=make_color_sysex(0x0C, msg.value)), mido.Message('sysex', data=make_color_sysex(0x0D, msg.value))], 0.3)).start()
            if cc_number == 10 and msg.value == 0 and cc_history[cc_number] is not None and time.time() - cc_history[cc_number] > 2 * DOUBLE_TAP_THRESHOLD:
                output.send(mido.Message('control_change', control=1, value = 127))
                output.send(mido.Message('control_change', control=1, value = 0))
                program_number = program_number//5*4 + 1 if (program_number%5==4) else 4
                program_change(program_number)
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
                    # cc_history[cc_number] = None
                else:
                    cc_history[cc_number] = timestamp

    def my_callback2(cc_number):
        print("cc is {}".format(cc_number))
        match cc_number:
            case 10:
                output.send(mido.Message('control_change', control=1, value = 127))
                output.send(mido.Message('control_change', control=1, value = 0))

    # Define a callback function for a specific CC number
    def my_callback(cc_number):
        global last_double
        global program_number
        global was
        match cc_number:
            case 10:
                if last_double is not None and time.time() - last_double < 2*DOUBLE_TAP_THRESHOLD:
                    print("triple")
                    program_number = program_number//5*4 + 1 if (was%5==3) else 3
                    program_change(program_number)
                else:
                    print("double")
                    last_double = time.time()
                    was = program_number
                    # output.send(mido.Message('control_change', control=1, value = 127))
                    # output.send(mido.Message('control_change', control=1, value = 0))
                    program_number = program_number//5*4 + 1 if (program_number%5==2) else 2
                    program_change(program_number)
            case 3:
                print('bank up')
                program_number += 4
                program_change(program_number)
            case 4:
                print('bank down')
                if program_number > 4:
                    program_number -= 4
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
    cc_double_callback[10] = my_callback
    cc_double_callback[3] = my_callback
    cc_double_callback[4] = my_callback
    cc_callback[10] = my_callback2
    cc_callback[71] = my_callback
    cc_callback[72] = my_callback
    cc_callback[73] = my_callback
    cc_callback[74] = my_callback

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

