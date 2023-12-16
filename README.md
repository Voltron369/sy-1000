# Boss SY-1000 MIDI Controller

## Overview

This Python script is part of a project to overcome the normal limitations of using a multi-effects pedal such as the SY-1000 and expand it's functions using a Digital Audio Workstation (DAW) such as Mainstage.  
Normally you would control a DAW from the SY-1000 by transmitting the SY-1000's program changes to the DAW.  This results in dropout even if only the normal input is used or the SY-1000 instrument model is not changing.

The trick is to disable bank and patch changes on the SY's buttons and have them transmit midi CC instead.  
Python script interprets the midi CC and send program changes to the DAW and sets the patch LEDs on the SY.  
DAW sends program changes to the SY if needed.  
DAW sends title changes to the SY since the SY will rarely be changing patches (to avoid dropout)  
DAW sends midi CC to the Python script to control the button lights  

With a Properly configured DAW, this allows:

- Instant patch changes (mostly)
- Reverb and Delay spillover
- Looper with red/green LED indicator and one-button operation on SY-1000 CTRL-2 or EXT2
- Double press for bank changes, so the whole top row is available for effects
- DAW will remember effect on/off state when switching patches, so it acts more like an A/B/C/D switch
- Switch patches 1-4 using GK1 or EXT1 *and* control CC1 with the same button
- "Negative" bank numbers (A-Z) where you can alias patches for songs with a long press
- Set LED light colors from DAW

## Features

- **Set SY-1000 program title**: Generates a sysex file the DAW can send
- **Customizable Interaction**: Supports single, double, triple taps, and long presses for MIDI controls.
- **Dynamic SysEx Message Generation**: Creates and sends SysEx messages for title and button color changes.
- **Program and Bank Changes**: Facilitates program changes and bank switching on the DAW using the SY-1000 buttons without changing programs on the SY-1000.
- **Negative Banks**: Allows patches to be aliased to negative banks (A-Z) for use in songs, without having to copy or move them.  This is saved in JSON

## Prerequisites

- Python 3
- `mido` library for MIDI interaction

## Installation

1. Ensure Python 3 is installed on your system.
2. Install `mido` using pip: `pip install mido`

## Configuration

- Set your MIDI input and output port names in the `input_port_name`, `input_port_name2`, `input_port_name3`, and `output_port_name` variables.
- Adjust `DOUBLE_TAP_THRESHOLD` and `LONG_PRESS_THRESHOLD` as per your requirements.

## Usage

1. Run the script with Python 3: `python3 <script_name>.py`
2. The script will print available MIDI input names for reference.
3. Interact with your MIDI device; the script responds to the configured input and provides feedback through the output ports.

## Customization

- Modify callback functions for different MIDI control changes as per your needs.
- Adjust the SysEx message generation functions for different types of feedback.

## Important Functions

- `load_state_from_json(filename)`: Loads saved state from a JSON file.
- `save_state_to_json(filename, array1, array2, array3, array4)`: Saves state to a JSON file.
- `update_array(arrays, array_index, element_index, new_value)`: Updates a specific element in a state array.
- `make_title_sysex(input_name)`: Creates a SysEx message for title display.
- `make_color_sysex_patch(button, color)`: Creates a SysEx message for patch color change.
- `make_color_sysex_system(button, color)`: Creates a SysEx message for system color change.
- `send_messages_after_delay(port, messages, delay)`: Sends MIDI messages after a specified delay.
- `program_change(number, button)`: Changes the MIDI program based on input.

## MIDI Control Change (CC) Mappings

| CC Number | Action | Description |
|-----------|--------|-------------|
| `1`       | Echo Callback | Echoes the control change value. |
| `2`       | Echo Callback | Echoes the control change value. |
| `3`       | Bank Change Callback | Echoes the control change value.  Handles bank changes (Double tap). |
| `4`       | Bank Change Callback | Echoes the control change value.  Handles bank changes (Double tap). |
| `10`      | CC 10 Callback | Handles various presses (Single, Double, Triple, Long) for custom actions.* |
| `41`      | Color Callback | Changes the color of Bank Dn. |
| `42`      | Color Callback | Changes the color of Bank Up. |
| `43`      | Color Callback | Changes the color of CTRL 1. |
| `44`      | Color Callback | Changes the color of CTRL 2. |
| `71` to `74` | Patch Callback, Copy-Paste Callback | Handles patch changes and copy-paste actions (Long press for copy-paste). |

 \* for midi CC 10, single press toggles CC 1, double press goes to patch A2, triple A3, long press A4.  If you select the current patch, it returns to A1

## Troubleshooting

- Ensure the correct MIDI port names are set in the script.
- Check if `mido` is installed correctly.
- For specific issues with MIDI devices, consult the device's manual or support forums.

## License

MIT License (see LICENSE.md)

## Author

(c) 2023, Gerard Decatrel
