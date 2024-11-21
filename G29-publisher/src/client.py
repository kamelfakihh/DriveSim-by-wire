import argparse
import json
import socket
import pygame
from kuksa_client.grpc import Datapoint
from kuksa_client.grpc import DataEntry
from kuksa_client.grpc import DataType
from kuksa_client.grpc import EntryUpdate
from kuksa_client.grpc import Field
from kuksa_client.grpc import Metadata
from kuksa_client.grpc import VSSClient

import time


def publish_control_signals(databroker_host, databroker_port, verbose=False):
    """
    Reads raw data input from Logitech G29 steering wheel such as steering angle, up shifts, down shifts, and brake/throttle pedal position. Then Forwards them to a kuksa databroker according to their respective VSS topics.

    Parameters:
    databroker_host (string) : Databroker instance hostname or ip address.
    databroker_port (int)    : Databroker instance port
    verbose         (boolean): Prints incoming data to STDOUT

    Example:
    >>> publish_control_signals(127.0.0.1, 5555, True)
    """

    try:
        print(f"starting G29Client")
        print(f"sending data to Kuksa databroker instance at host {databroker_host}, port {databroker_port}")
        print(f"verbose mode is: {bool(verbose)}")
        print('connecting to Logitech G29')

        # initialize G29 as joystick
        pygame.init()
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        # Connect to the Kuksa databroker
        client = VSSClient(databroker_host, databroker_port)
        client.connect()

        # Initial state
        data_dict = {
            'steering'  : 0,
            'throttle'  : 0,
            'brake'     : 0,
            'gear'      : 0
        }

        shift_up_high = False
        shift_down_high = False
        current_gear = 0

        # Sample controller inputs
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            try:

                # read value and publish it to the Broker if the value changes
                steering = joystick.get_axis(0)
                if data_dict.get('steering', -1) != steering:
                    data_dict["steering"] = steering
                    client.set_current_values({'Vehicle.Chassis.Axle.Row1.SteeringAngle': Datapoint(data_dict['steering'])})

                throttle = joystick.get_axis(1)
                if data_dict.get('throttle', -1) != throttle:
                    data_dict["throttle"] = throttle
                    client.set_current_values({'Vehicle.Chassis.Accelerator.PedalPosition': Datapoint(100 - min(100, max(0, data_dict['throttle'] * 100)))})

                brake = joystick.get_axis(2)
                if data_dict.get('brake', -1) != brake:
                    data_dict["brake"] = brake
                    client.set_current_values({'Vehicle.Chassis.Brake.PedalPosition': Datapoint(100 - min(100, max(0, data_dict['brake'] * 100)))})

                # NOTE: currently the publisher doesn't define a special topic for shift up and down signal, instead we keep track of an arbitrary value "current gear" that doesn't directly represent the current gear in the vehicle. We only care about the variation of that of variable. If the current gear increases then it was definitely an upshift
                shift_up = joystick.get_button(4)
                shift_down = joystick.get_button(5)

                # upshift/downshift debounce (kinda ?)
                if not shift_up_high and shift_up == 1 :
                    shift_up_high = 1
                    current_gear += 1
                elif shift_up_high and shift_up == 0:
                    shift_up_high = 0

                if not shift_down_high and shift_down == 1 :
                    shift_down_high = 1
                    current_gear -= 1
                elif shift_down_high and shift_down == 0:
                    shift_down_high = 0

                if data_dict.get('gear', 0) != current_gear:
                    data_dict["gear"] = current_gear
                    client.set_current_values({'Vehicle.Powertrain.Transmission.CurrentGear': Datapoint(current_gear)})

                if verbose :
                    print(data_dict)
            except Exception as e:
                print(f"error processing: {e}")
    except Exception as e:
        print(f"error initializing or running the publisher: {e}")


def main():

    description = 'Grabs raw data from Logitech G29 and forwards them to kuksa databroker'
    cli_parser = argparse.ArgumentParser(description=description)

    cli_parser.add_argument(
        '-th', type=str, dest='databroker_host', default='localhost',
        help='hostname of the kuksa databroker instance')
    cli_parser.add_argument(
        '-tp', type=str, dest='databroker_port', default=55555,
        help='port of the kuksa databroker instance')
    cli_parser.add_argument(
        '--verbose', action='store_true',
        help='print incoming data to stdout')

    args = cli_parser.parse_args()
    publish_control_signals(args.databroker_host, int(args.databroker_port), args.verbose)
    return


if __name__ == "__main__":
    main()
