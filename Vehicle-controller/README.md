# Vehicle controller

Reads control information from the Kuksa broker and apply them in the simulator. The program uses `vgamepad` library to emulate and Xbox360 controller. You need to map the input setting in game to the Xbox controller. 
The following is the mapping between the VSS topics and controller output:

Vehicle.Chassis.Brake.PedalPosition -> left trigger (0:255)
Vehicle.Chassis.Accelerator.PedalPosition -> right trigger (0:255)
Vehicle.Chassis.Axle.Row1.SteeringAngle -> left_joystick (-1.0:1.0)
Vehicle.Powertrain.Transmission.CurrentGear -> Gamepad_x for downshifts and Gamepad_a for upshifts

## How to run it ?

This program is not managed by Ankaios. You need to run it on Windows using the following command :

```
python3 controller.py --databroker_host <Databroker host ip> --databroker_port <Databroker port>
```
run `python3 controller.py --help` for more information.

Note: The program can be run in any order with the simulator (Assetto Corsa).
