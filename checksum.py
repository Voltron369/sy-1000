def calculate_checksum(data):
    checksum = 128 - (sum(data) % 128)
    return checksum

def main():
    input_data = input("Enter up to 16 characters: ")
    
    # Pad the input with spaces if it's less than 16 characters
    input_data = input_data.ljust(16)

    # Convert input characters to a list of ASCII values
    ascii_values = [ord(char) for char in input_data]

    # Additional data
    manufacturer_id = 0x41
    additional_data_1 = [0x10, 0x00, 0x00, 0x00, 0x69, 0x12]
    additional_data_2 = [0x10, 0x00, 0x00, 0x00]

    # Create the SysEx message
    sysex_message = [0xF0, manufacturer_id]
    sysex_message.extend(additional_data_1)
    sysex_message.extend(additional_data_2)
    sysex_message.extend(ascii_values)
    checksum = calculate_checksum(ascii_values + additional_data_2)
    sysex_message.append(checksum)
    sysex_message.append(0xF7)

    # Convert the message to bytes and save it to a .syx file
    sysex_bytes = bytes(sysex_message)
    with open("output.syx", "wb") as syx_file:
        syx_file.write(sysex_bytes)

    print(f"SysEx Message: {sysex_bytes.hex()}")
    print("Data saved in output.syx")

if __name__ == "__main__":
    main()

