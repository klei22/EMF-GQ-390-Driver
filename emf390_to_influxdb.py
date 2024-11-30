import os
import time
import argparse
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from EMF390 import EMF390  # Import the EMF390 class

# InfluxDB Configuration
BUCKET = "health_data"
ORG = "chromebook"
URL = "http://localhost:8086"
TOKEN = os.environ.get("INFLUXDB_TOKEN")  # Ensure the token is set in the environment

# Setup InfluxDB client
client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api()

def send_to_influx(timestamp, measurement, value):
    """
    Send a data point to InfluxDB.

    :param timestamp: UTC timestamp of the data point.
    :param measurement: Name of the measurement (e.g., 'emf_value').
    :param value: Value to send to InfluxDB.
    """
    point = (
        Point("emf390_data")
        .tag("device", "gq_emf390")
        .field(measurement, value)
        .time(timestamp)
    )
    write_api.write(bucket=BUCKET, org=ORG, record=point)
    print(f"Sent {measurement} data to InfluxDB: {timestamp}, {value}")

def main():
    parser = argparse.ArgumentParser(description="Read data from GQ EMF-390 and send it to InfluxDB.")
    parser.add_argument('--interval', type=int, default=5, help='Interval in seconds between readings.')
    args = parser.parse_args()
    interval = args.interval

    # Initialize the EMF390 device
    emf = EMF390(port="/dev/gqemf390", baudrate=57600)

    try:
        while True:
            # Retrieve all measurements
            timestamp = datetime.utcnow().isoformat() + "Z"  # Use UTC timestamp
            try:
                emf_value = emf.get_emf()
                send_to_influx(timestamp, "emf_value", float(emf_value))

                ef_value = emf.get_ef()
                send_to_influx(timestamp, "ef_value", float(ef_value))

                rf_watts = emf.get_rf_watts()
                send_to_influx(timestamp, "rf_watts", float(rf_watts))

                rf_dbm = emf.get_rf_dbm()
                send_to_influx(timestamp, "rf_dbm", float(rf_dbm))

                rf_density = emf.get_rf_density()
                send_to_influx(timestamp, "rf_density", float(rf_density))

                total_density = emf.get_total_density()
                send_to_influx(timestamp, "total_density", float(total_density))

                density_peak = emf.get_density_peak()
                send_to_influx(timestamp, "density_peak", float(density_peak))
            except ValueError as e:
                print(f"Error parsing data: {e}")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nExiting script.")
    finally:
        write_api.close()
        client.close()
        emf.close()  # Ensure the device is properly closed

if __name__ == "__main__":
    main()

