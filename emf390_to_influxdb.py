import os
import time
import argparse
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from EMF390 import EMF390  # Import the EMF390 class
import statistics

# InfluxDB Configuration
BUCKET = "health_data"
ORG = "chromebook"
URL = "http://localhost:8086"
TOKEN = os.environ.get("INFLUXDB_TOKEN")  # Ensure the token is set in the environment

# Setup InfluxDB client
client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api()


def send_to_influx(timestamp, measurement, value, tags=None):
    """
    Send a data point to InfluxDB.

    :param timestamp: UTC timestamp of the data point.
    :param measurement: Name of the measurement (e.g., 'emf_value').
    :param value: Value to send to InfluxDB.
    :param tags: Optional dictionary of tags for the InfluxDB point.
    """
    point = Point("emf390_data").field(measurement, value).time(timestamp)
    if tags:
        for key, tag_value in tags.items():
            point = point.tag(key, tag_value)
    write_api.write(bucket=BUCKET, org=ORG, record=point)
    print(f"Sent {measurement} data to InfluxDB: {timestamp}, {value}")


def main():
    parser = argparse.ArgumentParser(description="Read data from GQ EMF-390 and send it to InfluxDB.")
    parser.add_argument('--interval', type=int, default=20, help='Interval in seconds between readings.')
    args = parser.parse_args()
    interval = args.interval

    # Initialize the EMF390 device
    emf = EMF390(port="/dev/gqemf390", baudrate=115200)

    try:
        while True:
            # Retrieve the timestamp
            timestamp = datetime.utcnow().isoformat() + "Z"

            try:
                # Retrieve and send EMF and EF values
                emf_value = emf.get_emf()
                send_to_influx(timestamp, "emf_value", float(emf_value))

                ef_value = emf.get_ef()
                send_to_influx(timestamp, "ef_value", float(ef_value))

                # Retrieve and process RF band data
                rf_band_data = emf.get_rf_band_data()
                mode = emf.get_mode()  # Retrieve the current RF band/mode
                if rf_band_data and len(rf_band_data) > 0:
                    # Compute statistics
                    max_dbm = max(rf_band_data)
                    min_dbm = min(rf_band_data)
                    avg_dbm = sum(rf_band_data) / len(rf_band_data)
                    median_dbm = statistics.median(rf_band_data)
                    stdev_dbm = statistics.stdev(rf_band_data) if len(rf_band_data) > 1 else 0

                    # Send summary statistics to InfluxDB
                    tags = {"mode": mode}
                    send_to_influx(timestamp, "rf_max_dbm", max_dbm, tags)
                    send_to_influx(timestamp, "rf_min_dbm", min_dbm, tags)
                    send_to_influx(timestamp, "rf_avg_dbm", avg_dbm, tags)
                    send_to_influx(timestamp, "rf_median_dbm", median_dbm, tags)
                    send_to_influx(timestamp, "rf_stdev_dbm", stdev_dbm, tags)
                else:
                    print("No RF band data retrieved.")

            except ValueError as e:
                print(f"Error parsing data: {e}")

            # Wait before the next iteration
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nExiting script.")
    finally:
        write_api.close()
        client.close()
        emf.close()


if __name__ == "__main__":
    main()

