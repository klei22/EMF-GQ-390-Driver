# debug_emf390.py
import serial
import time

def main():
    port = "/dev/gqemf390"  # Update this if your device uses a different port
    baudrate = 115200        # Confirm the baud rate with your device's specifications
    timeout = 1             # Timeout for serial read operations

    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print(f"Opened serial port {port} at {baudrate} baud.")
    except serial.SerialException as e:
        print(f"Failed to open serial port {port}: {e}")
        return

    try:
        while True:
            # Read any incoming data
            data = ser.read(ser.in_waiting or 1)
            if data:
                # Display received data in hex and ASCII
                hex_data = ' '.join(f'{b:02X}' for b in data)
                ascii_data = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
                print(f"Received {len(data)} bytes: Hex: {hex_data} | ASCII: {ascii_data}")

            # Prompt user for command
            command = input("Enter command to send (or 'exit' to quit): ")
            if command.lower() == 'exit':
                break
            if command:
                # Send command to the device
                ser.write(command.encode('utf-8'))
                print(f"Sent command: {command}")
                time.sleep(0.1)  # Wait for device to respond

                # Read response from the device
                response = ser.read(ser.in_waiting or 1)
                if response:
                    hex_response = ' '.join(f'{b:02X}' for b in response)
                    ascii_response = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in response)
                    print(f"Received response: Hex: {hex_response} | ASCII: {ascii_response}")
                else:
                    print("No response received.")
    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        ser.close()
        print("Serial port closed.")

if __name__ == "__main__":
    main()

