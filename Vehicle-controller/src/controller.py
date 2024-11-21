#!/usr/bin/python3
import json
import time
from kuksa_client.grpc import VSSClient, Datapoint

import vgamepad as vg
import time

gamepad = vg.VX360Gamepad()

gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
gamepad.update()
time.sleep(0.5)



def fetch_and_update_control(databroker_host, databroker_port, output_file, interval=1, verbose=False):

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
        brake_position = client.get_current_values(['Vehicle.Chassis.Brake.PedalPosition']).get(
            'Vehicle.Chassis.Brake.PedalPosition', {}).value
        accel_position = client.get_current_values(['Vehicle.Chassis.Accelerator.PedalPosition']).get(
            'Vehicle.Chassis.Accelerator.PedalPosition', {}).value
        steering_angle = client.get_current_values(['Vehicle.Chassis.Axle.Row1.SteeringAngle']).get(
            'Vehicle.Chassis.Axle.Row1.SteeringAngle', {}).value
        gear = client.get_current_values(['Vehicle.Powertrain.Transmission.CurrentGear']).get(
            'Vehicle.Powertrain.Transmission.CurrentGear', {}).value

        if current_gear > gear:
            print("down")
            current_gear = gear
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            gamepad.update()
            time.sleep(0.2)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            gamepad.update()
        elif current_gear < gear:
            print("up")
            current_gear = gear
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            gamepad.update()
            time.sleep(0.2)
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            gamepad.update()
        
        # if current_gear > gear :
        #     gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        #     gamepad.update()
        #     time.sleep(0.3)
        #     gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        #     # gamepad.update()
        # elif current_gear < gear :
        #     gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        #     gamepad.update()
        #     time.sleep(0.3)
        #     gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        #     # gamepad.update()

        # current_gear = gear
        # brake_light_status = client.get_current_values(['Vehicle.Body.Lights.Brake.IsActive']).get(
            # 'Vehicle.Body.Lights.Brake.IsActive', {}).value

        # print(steering_angle)

        # print(accel_position, brake_position)
        gamepad.left_trigger(int(brake_position*2.55))
        gamepad.right_trigger(int(accel_position*2.55))
        # gamepad.left_joystick_float(x_value_float=max(1, min(-1, 2.5*steering_angle)), y_value_float=0.0)
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
        '-o', '--output', type=str, default='telemetry_data.json',
        help='Output file to store telemetry data (default: telemetry_data.json)'
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
        output_file=args.output,
        interval=args.interval,
        verbose=args.verbose
    )
