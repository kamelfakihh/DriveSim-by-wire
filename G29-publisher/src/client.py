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

def read_mem(databroker_host, databroker_port, verbose=False):

    print(f"starting G29Client")
    print(f"sending data to Kuksa databroker instance at host {databroker_host}, port {databroker_port}")
    print(f"verbose mode is: {bool(verbose)}")
    print('connecting to Logitech G29')

    # initialize G29
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    #conntect to databroker
    client = VSSClient(databroker_host, databroker_port)
    client.connect()

    data_dict = {}

    shift_up_high = False
    shift_down_high = False
    current_gear = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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

        shift_up = joystick.get_button(4)
        shift_down = joystick.get_button(5)

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


def main():
    description = 'Grabs data sent from Logitech G29 and forwards them to kuksa databroker over gRPC format.'
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
    read_mem(args.databroker_host, int(args.databroker_port), args.verbose)
    return


if __name__ == "__main__":
    main()
