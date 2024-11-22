#!/usr/bin/python3
import json
import time
from kuksa_client.grpc import VSSClient, Datapoint

import vgamepad as vg
import time

gamepad = vg.VX360Gamepad()

def fetch_and_update_control(databroker_host, databroker_port, interval=1, verbose=False):
    """
    Reads control signals from the kuksa databroker and passes them as controller input to the game/simulator

    Parameters:
    databroker_host (string) : Databroker instance hostname or ip address.
    databroker_port (int)    : Databroker instance port
    verbose         (boolean): Prints incoming data to STDOUT

    Example:
    >>> publish_control_signals(127.0.0.1, 5555, True)
    """
    
    # Connect to Kuksa Data Broker
    client = VSSClient(databroker_host, databroker_port)
    try:
        client.connect()
        print("Connected successfully to Kuksa Data Broker.")
    except Exception as e:
        print(f"Failed to connect to Kuksa Data Broker: {e}")
        return

    current_gear = 0

    while True:
        # Fetch specific data points from the Data Broker
        # speed = client.get_current_values(['Vehicle.Speed']).get('Vehicle.Speed', {}).value
        if client.get_current_values(['Vehicle.Chassis.Brake.PedalPosition']).get(
            'Vehicle.Chassis.Brake.PedalPosition'):
            brake_position = client.get_current_values(['Vehicle.Chassis.Brake.PedalPosition']).get(
            'Vehicle.Chassis.Brake.PedalPosition').value
        else:
            brake_position = 0

        if client.get_current_values(['Vehicle.Chassis.Accelerator.PedalPosition']).get(
            'Vehicle.Chassis.Accelerator.PedalPosition') :
            accel_position = client.get_current_values(['Vehicle.Chassis.Accelerator.PedalPosition']).get(
            'Vehicle.Chassis.Accelerator.PedalPosition').value
        else:
            accel_position = 0

        if client.get_current_values(['Vehicle.Chassis.Axle.Row1.SteeringAngle']).get(
            'Vehicle.Chassis.Axle.Row1.SteeringAngle'):
            steering_angle = client.get_current_values(['Vehicle.Chassis.Axle.Row1.SteeringAngle']).get(
            'Vehicle.Chassis.Axle.Row1.SteeringAngle').value
        else:
            steering_angle = 0

        if client.get_current_values(['Vehicle.Powertrain.Transmission.CurrentGear']).get(
            'Vehicle.Powertrain.Transmission.CurrentGear', {}):
            gear = client.get_current_values(['Vehicle.Powertrain.Transmission.CurrentGear']).get(
            'Vehicle.Powertrain.Transmission.CurrentGear', {}).value
        else:
            gear = 0

        if current_gear > gear:            
            current_gear = gear
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            gamepad.update()
            time.sleep(0.2)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            gamepad.update()
        elif current_gear < gear:            
            current_gear = gear
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            gamepad.update()
            time.sleep(0.2)
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            gamepad.update()
            
        gamepad.left_trigger(int(brake_position*2.55))
        gamepad.right_trigger(int(accel_position*2.55))
        gamepad.left_joystick_float(x_value_float=steering_angle, y_value_float=0.0)
        gamepad.update()

        # Wait for the next polling interval
        # time.sleep(interval)

    client.disconnect()


if __name__ == "__main__":
    import argparse

    description = 'Client script to fetch telemetry data from Kuksa Data Broker and store it in a JSON file.'
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
        '-i', '--interval', type=int, default=1,
        help='Time interval (in seconds) between polling data (default: 1 second)'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Print telemetry data to stdout'
    )

    args = parser.parse_args()

    fetch_and_update_control(
        databroker_host=args.host,
        databroker_port=args.port,
        interval=args.interval,
        verbose=args.verbose
    )
