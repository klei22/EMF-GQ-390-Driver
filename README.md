# GQ EMF-390 PySerial Driver

This repository provides Python scripts to interface with the GQ EMF-390 device
using the `pyserial` library. It includes functionality for retrieving
electromagnetic field (EMF) data, environmental field (EF) data, RF density,
and more. Additionally, it supports sending data to an InfluxDB database for
monitoring and visualization.

---

## Table of Contents

1. [Installation](#installation)
2. [Python Scripts](#python-scripts)
   - [RealTime Data Retrieval](#realtime-data-retrieval)
   - [Send Data to InfluxDB](#send-data-to-influxdb)
3. [General Usage](#general-usage)
5. [Troubleshooting](#troubleshooting)

---

## Installation

1. **Add User to Dialout Group**:
   Ensure the current user has access to serial ports:
   ```bash
   sudo adduser $USER dialout
   ```
   Log out and back in for the changes to take effect.

2. **Install the Udev Rule**:
   Copy the provided udev rule to assign a consistent name to the GQ EMF-390 device:
   ```bash
   sudo cp 99-GQEMF390.rules /etc/udev/rules.d
   ```

3. **Reload Udev Rules**:
   Apply the udev rule:
   ```bash
   bash reload_udev.sh
   ```

4. **Set Up a Virtual Environment**:
   Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Python Dependencies**:
   Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

---

## Python Scripts

### 1. RealTime Data Retrieval

The `EMF390.py` script provides a Python class for communicating with the GQ EMF-390 device. Example usage:

```python
from EMF390 import EMF390

# Initialize the device
emf = EMF390(port="/dev/gqemf390", baudrate=57600)

# Retrieve EMF and EF values
print("EMF Value:", emf.get_emf())
print("EF Value:", emf.get_ef())

# Close the device connection
emf.close()
```

---

### 2. Send Data to InfluxDB

The `emf390_to_influx.py` script sends measurements to an InfluxDB instance at regular intervals.

#### Usage

```bash
python3 emf390_to_influx.py [--interval INTERVAL]
```

- **Default Interval**: 5 seconds
- **Custom Interval**: Use the `--interval` flag to specify a custom interval (in seconds).

#### Example:
```bash
python3 emf390_to_influx.py --interval 10
```

#### InfluxDB Configuration

Ensure the following environment variable is set with a valid InfluxDB token:

```bash
export INFLUXDB_TOKEN="your_influxdb_token"
```

### Script Features:

- Sends the following data points to InfluxDB:
  - `emf_value`
  - `ef_value`
  - `rf_watts`
  - `rf_dbm`
  - `rf_density`
  - `total_density`
  - `density_peak`
- Configurable interval between measurements.
- Uses the `health_data` bucket by default.

---

## General Usage

### Start Device Communication
1. Connect the GQ EMF-390 to your system.
2. Ensure the device appears as `/dev/gqemf390` (or the configured device name).
3. Run the desired script for data retrieval or InfluxDB integration.

---

## Troubleshooting

### Device Not Recognized
If the device does not appear as `/dev/gqemf390`:
1. Verify the udev rules were installed and reloaded:
   ```bash
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```
2. Check if the `brltty` service is interfering:
   ```bash
   sudo systemctl stop brltty
   sudo systemctl disable brltty
   sudo apt remove brltty
   sudo apt purge brltty
   ```

### Serial Communication Errors

Ensure the correct permissions are set on the serial port:
```bash
sudo chmod a+rw /dev/gqemf390
```
