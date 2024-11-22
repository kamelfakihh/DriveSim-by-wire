# Vehicle data publisher

Reads data from Assetto corsa shared memory and publishes it to the Kuksa broker. It currently publishes the following VSS topics :

- Vehicle.OBD.FuelLevel
- Vehicle.Powertrain.CombustionEngine.Speed
- Vehicle.Speed
- Vehicle.ADAS.ABS.isEngaged
- Vehicle.Acceleration

The list of avaialble telemetry data can be found in AssettoCorsaMemoryMapping.py. Below is an example on how to read a value from the Assetto Corsa telemetry:

```
from AssettoCorsaMemoryMapping import SimInfo

game = SimInfo()

# Telemetry data is categorized into three fields : Physics, Graphics, and Static
# a field can be accessed by SimInfo.<Category>.<Field Name>
speed = game.physics.speedKmh
```
## How to run it ?

This program is not managed by Ankaios. You need to run it on Windows using the following command :

```
python3 client.py --databroker_host <Databroker host ip> --databroker_port <Databroker port>
```
run `python3 client.py --help` for more information.

Note: The program can be run in any order with the simulator (Assetto Corsa). No additional configuration is required.
