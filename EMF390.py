# EMF390.py
import serial
import time
import re

class EMF390:
    """
    A class to interface with the GQ EMF-390 device via serial communication.
    """

    def __init__(self, port="/dev/gqemf390", baudrate=115200, timeout=1):
        """
        Initialize the EMF390 object.

        :param port: Serial port to connect to the device (default: '/dev/gqemf390')
        :param baudrate: Baud rate for the serial connection (default: 115200)
        :param timeout: Timeout for serial read/write operations (default: 1 second)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

        # Open the serial port
        self._connect()

    def _connect(self):
        """Establish a connection to the device."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            print(f"Connected to EMF-390 on {self.port}")
        except serial.SerialException as e:
            raise Exception(f"Failed to connect to {self.port}: {e}")

    def send_command(self, command):
        """
        Send a command to the EMF-390 device and retrieve its response.

        :param command: The command string to send (e.g., '<GETEMF>>').
        :return: The response from the device as a string.
        """
        if not self.serial or not self.serial.is_open:
            raise Exception("Serial port is not open.")
        
        # Flush input and output buffers
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        # Send the command
        self.serial.write(command.encode())
        time.sleep(0.1)  # Wait for device response

        # Read response from the device
        response = self.serial.read_all().decode(errors="ignore").strip()
        # Debug: print the raw response
        # print(f"Raw response: '{response}'")
        return response

    def _parse_response(self, response, pattern, value_name, flags=0):
        """
        Parse the device response using the given pattern.

        :param response: The raw response string from the device.
        :param pattern: The regex pattern to extract the value.
        :param value_name: The name of the value for error messages.
        :param flags: Regex flags to use (e.g., re.IGNORECASE).
        :return: The extracted float value or None if parsing fails.
        """
        match = re.search(pattern, response, flags)
        if match:
            try:
                return float(match.group(1))
            except ValueError as e:
                print(f"Error converting {value_name} to float: {e}")
                return None
        else:
            print(f"Unexpected {value_name} response format.")
            print(f"Expected pattern: '{pattern}'")
            print(f"Actual response: '{response}'")
            return None

    def get_emf(self):
        """Retrieve the EMF value from the device."""
        response = self.send_command("<GETEMF>>")
        pattern = r'EMF\s*=\s*([\d\.]+)'
        return self._parse_response(response, pattern, 'EMF')

    def get_ef(self):
        """Retrieve the EF value from the device."""
        response = self.send_command("<GETEF>>")
        pattern = r'EF\s*=\s*([\d\.]+)'
        return self._parse_response(response, pattern, 'EF')

    def get_rf_band_data(self):
        """
        Retrieve the RF band data from the device.

        :return: A list of dBm values.
        """
        response = self.send_command("<GETBANDDATA>>")
        # Debug: print the raw response
        print(f"Raw RF band data response: '{response}'")
        # Response may include ' dBm' at the end or within the data
        try:
            # Remove any ' dBm' suffix if present
            response = response.replace(' dBm', '').strip()
            # Remove any other non-numeric characters or extra text
            response = re.sub(r'[^\d\.,\-]', '', response)
            data_str_list = response.split(',')
            data_values = [float(value.strip()) for value in data_str_list if value.strip()]
            return data_values
        except ValueError as e:
            print(f"Error parsing RF band data: {e}")
            return None

    def get_mode(self):
        """Retrieve the current mode of the device."""
        response = self.send_command("<GETMODE>>")
        return response  # Mode is returned as text

    def get_version(self):
        """Retrieve the device version."""
        response = self.send_command("<GETVER>>")
        # Adjust the pattern to extract version number
        pattern = r'GQ-EMF390v2Re\s*([\d\.a-zA-Z]+)'
        match = re.search(pattern, response)
        if match:
            return match.group(1)
        else:
            print("Unexpected Version response format.")
            print(f"Expected pattern: '{pattern}'")
            print(f"Actual response: '{response}'")
            return response  # Return the raw response if pattern doesn't match

    def close(self):
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Connection closed.")

# Example usage
if __name__ == "__main__":
    try:
        emf = EMF390(port="/dev/gqemf390", baudrate=115200)

        version = emf.get_version()
        print("Device Version:", version)

        emf_value = emf.get_emf()
        if emf_value is not None:
            print("EMF Value:", emf_value, "mG")

        ef_value = emf.get_ef()
        if ef_value is not None:
            print("EF Value:", ef_value, "V/m")

        rf_band_data = emf.get_rf_band_data()
        if rf_band_data is not None:
            print("RF Band Data (first 10 values):", rf_band_data[:10])
            # You can process rf_band_data as needed

        mode = emf.get_mode()
        print("Current Mode:", mode)

        emf.close()
    except Exception as e:
        print("Error:", e)

