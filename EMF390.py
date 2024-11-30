import serial
import time

class EMF390:
    """
    A class to interface with the GQ EMF-390 device via serial communication.
    """

    def __init__(self, port="/dev/gqemf390", baudrate=57600, timeout=1):
        """
        Initialize the EMF390 object.

        :param port: Serial port to connect to the device (default: '/dev/gqemf390')
        :param baudrate: Baud rate for the serial connection (default: 57600)
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
        
        # Send the command
        self.serial.write(command.encode())
        time.sleep(0.1)  # Wait for device response
        response = self.serial.read_all().decode(errors="ignore").strip()
        return response

    def get_emf(self):
        """Retrieve the EMF value from the device."""
        return self.send_command("<GETEMF>>")

    def get_ef(self):
        """Retrieve the EF value from the device."""
        return self.send_command("<GETEF>>")

    def get_rf_watts(self):
        """Retrieve RF Watts from the device."""
        return self.send_command("<GETRFWATTS>>")

    def get_rf_dbm(self):
        """Retrieve RF -dBm from the device."""
        return self.send_command("<GETRFDBM>>")

    def get_rf_density(self):
        """Retrieve RF Density from the device."""
        return self.send_command("<GETRFDENSITY>>")

    def get_total_density(self):
        """Retrieve total RF density from the device."""
        return self.send_command("<GETRFTOTALDENSITY>>")

    def get_density_peak(self):
        """Retrieve total RF density peak from the device."""
        return self.send_command("<GETRFTOTALDENSITYPEAK>>")

    def get_version(self):
        """Retrieve the device version."""
        return self.send_command("<GETVER>>")

    def turn_power_on(self):
        """Turn the device power on."""
        return self.send_command("<POWERON>>")

    def turn_power_off(self):
        """Turn the device power off."""
        return self.send_command("<POWEROFF>>")

    def close(self):
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Connection closed.")

# Example usage
if __name__ == "__main__":
    try:
        emf = EMF390(port="/dev/gqemf390", baudrate=57600)

        print("Device Version:", emf.get_version())
        print("EMF Value:", emf.get_emf())
        print("EF Value:", emf.get_ef())

        emf.close()
    except Exception as e:
        print("Error:", e)

