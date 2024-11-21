# Logitech G29 publisher

Reads raw data input from Logitech G29 steering wheel such as steering angle, up shifts, down shifts, and brake/throttle pedal position. Then Forwards them to a kuksa databroker according to their respective VSS topics.

The pubisher currently only handles a predefined set of inputs from the wheel, however, it's possible to handle more inputs using the following snippet/template:

```
my_input = joystick.get_<input mapping in controller>
if data_dict.get('my_input', -1) != my_input:
    data_dict["my_input"] = my_input
    client.set_current_values({'Input.Vehicle.Signal.Specification.Topic': Datapoint(data_dict['my_input'])})
```

# How to run it

1. Make sure to have docker or podman installed
2. Make sure you Kuksa databroker is running. You can the following command to run the databroker locally.

```
docker run -it --rm --name Server --network host ghcr.io/eclipse-kuksa/kuksa-databroker:main --insecure
```

3. Build and run the container

```
docker build -t g29-publisher .
docker run -it g29-publisher --privileged --network host
```
privilege access required to access joystick device
4. Check the results using databoker client

```
docker run -it --rm --net=host ghcr.io/eclipse-kuksa/kuksa-python-sdk/kuksa-client:main
```
- example query :

```
> subscribe Vehicle.Chassis.Accelerator.PedalPosition
```
