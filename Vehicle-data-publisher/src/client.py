import argparse
import json
import socket
from kuksa_client.grpc import Datapoint
from kuksa_client.grpc import DataEntry
from kuksa_client.grpc import DataType
from kuksa_client.grpc import EntryUpdate
from kuksa_client.grpc import Field
from kuksa_client.grpc import Metadata
from kuksa_client.grpc import VSSClient

from AssettoCorsaMemoryMapping import SimInfo
import time

def read_mem(databroker_host, databroker_port, verbose=False):
    """
    Reads telemetry data from assetto corsa then Forwards them to a kuksa databroker according to their respective VSS topics.

    Parameters:
    databroker_host (string) : Databroker instance hostname or ip address.
    databroker_port (int)    : Databroker instance port
    verbose         (boolean): Prints incoming data to STDOUT

    Example:
    >>> publish_control_signals(127.0.0.1, 5555, True)
    """

    print(f"starting AssettoCorsaClient")
    print(f"sending data to Kuksa databroker instance at host {databroker_host}, port {databroker_port}")
    print(f"verbose mode is: {bool(verbose)}")

    #conntect to databroker
    client = VSSClient(databroker_host, databroker_port)
    client.connect()

    data_dict = {}

    game = SimInfo()
    print('connecting to Assetto Corsa')

    while True:
        
        if data_dict.get('fuel', -1) != game.physics.fuel:
            data_dict["fuel"] = game.physics.fuel
            client.set_current_values({'Vehicle.OBD.FuelLevel': Datapoint(data_dict['fuel'])}) 
        
        if data_dict.get('rpms', -1) != game.physics.rpms:
            data_dict["rpms"] = game.physics.rpms
            client.set_current_values({'Vehicle.Powertrain.CombustionEngine.Speed': Datapoint(data_dict['rpms'])}) 

        if data_dict.get('speedKmh', -1) != game.physics.speedKmh:
            data_dict["speedKmh"] = game.physics.speedKmh
            client.set_current_values({'Vehicle.Speed': Datapoint(data_dict['speedKmh'])}) 

        # if data_dictc.get('abs', -1) != game.physics.abs:
        #     data_dict["abs"] = game.physics.abs
        #     client.set_current_values({'Vehicle.ADAS.ABS.isEngaged': Datapoint(data_dict['abs'])}) 
        
        # if data_dict.get('accG', -1) != game.physics.accG:
        #     data_dict["accG"] = game.physics.accG
        #     client.set_current_values({'Vehicle.Acceleration': Datapoint(data_dict['accG'])}) 
        #     print(data_dict['accG'])

        if verbose :
            print(data_dict)




def main():
    description = 'Grabs data sent from Assetto Corsa\'s shared memory and forward them to kuksa databroker over gRPC format.'
    cli_parser = argparse.ArgumentParser(description=description)

    cli_parser.add_argument(
        '-th', type=str, dest='databroker_host', default='localhost',
        help='hostname of the kuksa databroker instance')
    cli_parser.add_argument(
        '-tp', type=int, dest='databroker_port', default=55555,
        help='port of the kuksa databroker instance')
    cli_parser.add_argument(
        '--verbose', action='store_true',
        help='print incoming data to stdout')

    args = cli_parser.parse_args()
    read_mem(args.databroker_host, args.databroker_port, args.verbose)
    return


if __name__ == "__main__":
    main()
