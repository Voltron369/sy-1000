# Boss SY-1000 MIDI Controller

## Overview

This Python script provides a robust MIDI controller functionality. It enables the manipulation of MIDI messages, supports various interaction patterns like single/double/triple taps and long presses, and updates the display and button LEDs through SysEx messages.

## Features

- **MIDI Port Interaction**: Allows interaction with multiple MIDI input and output ports.
- **Customizable Interaction**: Supports single, double, triple taps, and long presses for MIDI controls.
- **Dynamic SysEx Message Generation**: Creates and sends SysEx messages for title and color changes.
- **State Persistence**: Saves and loads the controller state to and from a JSON file.
- **Program and Bank Changes**: Facilitates program changes and bank switching.
- **Negative Banks**: Allows patches to be aliased to negative banks (A-Z) for use in songs, without having to copy or move them

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
| `3`       | Bank Change Callback | Handles bank changes (Double and Triple tap supported). |
| `4`       | Bank Change Callback | Handles bank changes (Double and Triple tap supported). |
| `10`      | CC 10 Callback | Handles various presses (Single, Double, Triple, Long) for custom actions. |
| `41`      | Color Callback | Changes the color of the specified button (Patch). |
| `42`      | Color Callback | Changes the color of the specified button (Patch). |
| `43`      | Color Callback | Changes the color of the specified button (Patch). |
| `44`      | Color Callback | Changes the color of the specified button (Patch). |
| `71` to `74` | Patch Callback, Copy-Paste Callback | Handles patch changes and copy-paste actions (Long press for copy-paste). |

for midi CC 10, single press toggles CC 1, double press goes to patch A2, triple A3, long press A4.  If you select the current patch, it returns to A1

## Troubleshooting

- Ensure the correct MIDI port names are set in the script.
- Check if `mido` is installed correctly.
- For specific issues with MIDI devices, consult the device's manual or support forums.

## License

MIT License (see LICENSE.md)

## Author

(c) 2023, Gerard Decatrel
