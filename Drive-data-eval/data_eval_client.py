#!/usr/bin/python3
import json
import time
import sys
import numpy as np
from kuksa_client.grpc import VSSClient, Datapoint
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError

CUTOFF = 2  # Anomaly cutoff percentage

def fetch_store_and_predict(databroker_host, databroker_port, write_file, output_file, model_file, led, interval=0.1, verbose=False):
    """
    Fetch telemetry data from Kuksa Data Broker, store it in a JSON file, and run inference using a TensorFlow model.
    Detect anomalies if the prediction deviates from the true value by more than the cutoff percentage.
    Publish anomaly status to a new topic in the Kuksa Data Broker.
    """
    print(f"Connecting to Kuksa Data Broker at {databroker_host}:{databroker_port}")
    print(f"Saving telemetry data to: {output_file}")
    print(f"Using model file: {model_file}")

    # Load the TensorFlow model
    with tf.keras.utils.custom_object_scope({'mse': MeanSquaredError()}):
        model = load_model(model_file)
    print("Model loaded successfully.")

    # Connect to Kuksa Data Broker
    client = VSSClient(databroker_host, databroker_port)
    try:
        client.connect()
        print("Connected successfully to Kuksa Data Broker.")
    except Exception as e:
        print(f"Failed to connect to Kuksa Data Broker: {e}")
        return

    if write_file:
        with open(output_file, 'w') as json_out:
            json_out.write('[')

    # Placeholder for sequential data (LSTM input)
    input_sequence = []

    while True:
        try:
            # Fetch specific data points from the Data Broker
            speed = client.get_current_values(['Vehicle.Speed']).get('Vehicle.Speed', {}).value
            brake_position = client.get_current_values(['Vehicle.Chassis.Brake.PedalPosition']).get('Vehicle.Chassis.Brake.PedalPosition', {}).value
            accel_position = client.get_current_values(['Vehicle.Chassis.Accelerator.PedalPosition']).get('Vehicle.Chassis.Accelerator.PedalPosition', {}).value
            steering_angle = client.get_current_values(['Vehicle.Chassis.Axle.Row1.SteeringAngle']).get('Vehicle.Chassis.Axle.Row1.SteeringAngle', {}).value

            if write_file:
                # Build the telemetry data dictionary
                telemetry_data = {
                    "timestamp": time.time(),
                    "Vehicle": {
                        "Speed": speed,
                        "Chassis": {
                            "Brake": {
                                "PedalPosition": brake_position,
                            },
                            "Accelerator": {
                                "PedalPosition": accel_position,
                            },
                            "Axle": {
                                "Row1": {
                                    "SteeringAngle": steering_angle
                                }
                            }
                        },
                    }
                }

                # Print telemetry data if verbose mode is enabled
                if verbose:
                    print(json.dumps(telemetry_data, indent=4))

                # Write telemetry data to the JSON file
                with open(output_file, 'a') as json_out:
                    json.dump(telemetry_data, json_out, indent=4)
                    json_out.write(',')

            else:
                # Prepare data for prediction
                current_data = [speed, brake_position, accel_position, steering_angle]
                input_sequence.append(current_data)

                # Ensure the sequence has the correct length for the LSTM model
                time_steps = model.input_shape[1]  # Get time steps from model input shape
                if len(input_sequence) > time_steps:
                    input_sequence.pop(0)

                # Run inference if enough data is collected
                if len(input_sequence) == time_steps:
                    input_array = np.array(input_sequence).reshape(1, time_steps, -1)  # Reshape for LSTM input
                    prediction = model.predict(input_array)
                    prediction_value = prediction[0][0]/10  # Assuming the model predicts a single value

                    # Calculate percentage deviation
                    deviation = abs(speed - prediction_value) / (prediction_value if prediction_value != 0 else 1)
                    print(f"True: {speed}, Prediction: {prediction_value}, Deviation: {deviation}")

                    # Check for anomaly
                    is_anomaly = abs(deviation) > CUTOFF 
                    print(f"Anomaly: {is_anomaly}")

                    # Publish anomaly status to a new topic in the Kuksa Data Broker
                    client.set_current_values({
                         "Vehicle.Analytics.Anamoly": Datapoint(is_anomaly)
                    })

            # Wait for the next polling interval
            time.sleep(interval)

        except Exception as e:
            print(f"Error fetching data: {e}")

        except KeyboardInterrupt:
            print("\nShutting down...")
            client.disconnect()
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
        '-w', '--write', type=bool, default=False,
        help='Whether to write the data to a JSON file'
    )
    parser.add_argument(
        '-o', '--output', type=str, default='telemetry_data.json',
        help='Output file to store telemetry data (default: telemetry_data.json)'
    )
    parser.add_argument(
        '-m', '--model', type=str, required=True,
        help='Path to the pre-trained TensorFlow model'
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
        write_file=args.write,
        output_file=args.output,
        model_file=args.model,
        interval=args.interval,
        verbose=args.verbose
    )
