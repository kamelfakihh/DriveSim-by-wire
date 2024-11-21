#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
from kuksa_client.grpc import VSSClient, Datapoint

# Pin configuration
LED_PIN = 18  # GPIO pin number where the LED is connected
# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(LED_PIN, GPIO.OUT)  # Set the pin as an output

def blink_led():
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("LED is ON")
    time.sleep(2)
    GPIO.output(LED_PIN, GPIO.LOW)
    print("LED is OFF")

def cleanup_gpio():
    GPIO.cleanup()
    print("GPIO cleanup done.")

def fetch_store_and_predict(databroker_host, databroker_port, interval=0.1, verbose=False):
    """
    Fetch telemetry data from Kuksa Data Broker, store it in a JSON file, and run inference using a TensorFlow model.
    Detect anomalies if the prediction deviates from the true value by more than the cutoff percentage.
    Publish anomaly status to a new topic in the Kuksa Data Broker.
    """
    print(f"Connecting to Kuksa Data Broker at {databroker_host}:{databroker_port}")

    # Connect to Kuksa Data Broker
    client = VSSClient(databroker_host, databroker_port)
    try:
        client.connect()
        print("Connected successfully to Kuksa Data Broker.")
    except Exception as e:
        print(f"Failed to connect to Kuksa Data Broker: {e}")
        return

    while True:
        try:
            # Fetch specific data points from the Data Broker
            anomaly = client.get_current_values(['Vehicle.Analytics.Anamoly']).get('Vehicle.Analytics.Anamoly', {}).value

            # Check for anomaly
            print(f"Anomaly: {anomaly}")

            if anomaly:
                blink_led()
                
            # Wait for the next polling interval
            time.sleep(interval)

        except Exception as e:
            print(f"Error fetching data: {e}")

        except KeyboardInterrupt:
            print("\nShutting down...")
            client.disconnect()
            cleanup_gpio()
            sys.exit(0)


if __name__ == "__main__":
    import argparse

    description = 'Client script to fetch telemetry data from Kuksa Data Broker, store it in a JSON file, run inference, and detect anomalies.'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '-th', '--host', type=str, default='localhost',
        help='Hostname of the Kuksa Data Broker (default: localhost)'
    )
    parser.add_argument(
        '-tp', '--port', type=int, default=55555,
        help='Port of the Kuksa Data Broker (default: 55555)'
    )
    parser.add_argument(
        '-i', '--interval', type=float, default=0.1,
        help='Time interval (in seconds) between polling data (default: 0.1 second)'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Print telemetry data to stdout'
    )

    args = parser.parse_args()

    fetch_store_and_predict(
        databroker_host=args.host,
        databroker_port=args.port,
        interval=args.interval,
        verbose=args.verbose
    )
