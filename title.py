#!/usr/bin/env python3
import mido
import sys

def calculate_checksum(data):
    checksum = 128 - (sum(data) % 128)
    return checksum

def main():
    # Create a MIDI file and add a track to it
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # input_name = input("Enter up to 16 characters: ")
    input_name = sys.argv[1]

    # Pad the input with spaces if it's less than 16 characters
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

    print(sysex_message)

    # Add a delay of 400 milliseconds (400,000 microseconds)
    delay_time = 400000
    track.append(mido.Message('sysex', time=delay_time, data=sysex_message))

    # Add the SysEx message
    track.append(mido.Message('sysex', time=delay_time, data=sysex_message))

    # Add a delay of 1.5 seconds
    delay_time = 1500000
    track.append(mido.Message('sysex', time=delay_time, data=sysex_message))

    # Add the SysEx message
    track.append(mido.Message('sysex', time=delay_time, data=sysex_message))

    # Save the MIDI file
    mid.save(input_name+'.mid')


if __name__ == "__main__":
    main()

