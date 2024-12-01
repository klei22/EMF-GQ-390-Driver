import serial
import time
import re


class EMF390:
    def __init__(self, port="/dev/gqemf390", baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self._connect()

    def _connect(self):
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
        if not self.serial or not self.serial.is_open:
            raise Exception("Serial port is not open.")
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.write(command.encode())
        time.sleep(0.1)
        response = self.serial.read_all().decode(errors="ignore").strip()
        return response

    def _parse_response(self, response, pattern, value_name, flags=0):
        match = re.search(pattern, response, flags)
        if match:
            try:
                return float(match.group(1))
            except ValueError as e:
                print(f"Error converting {value_name} to float: {e}")
                return None
        else:
            print(f"Unexpected {value_name} response format.")
            print(f"Response: '{response}'")
            return None

    def get_emf(self):
        response = self.send_command("<GETEMF>>")
        pattern = r'EMF\s*=\s*([\d\.]+)'
        return self._parse_response(response, pattern, 'EMF')

    def get_ef(self):
        response = self.send_command("<GETEF>>")
        pattern = r'EF\s*=\s*([\d\.]+)'
        return self._parse_response(response, pattern, 'EF')

    def get_rf_band_data(self):
        response = self.send_command("<GETBANDDATA>>")
        response = response.replace(' dBm', '').strip()
        response = re.sub(r'[^\d\.,\-]', '', response)
        try:
            data_str_list = response.split(',')
            return [float(value.strip()) for value in data_str_list if value.strip()]
        except ValueError as e:
            print(f"Error parsing RF band data: {e}")
            return None

    def get_mode(self):
        response = self.send_command("<GETMODE>>")
        return response

    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Connection closed.")

