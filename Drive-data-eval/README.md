# README.md

## **Data Evaluation Client**

This script fetches telemetry data from the **Kuksa Data Broker**, performs anomaly detection using a pre-trained LSTM/GRU TensorFlow model, and publishes the results to a new topic in the data broker. Optionally, it logs telemetry data to a JSON file for further analysis.

---

## **Setup**

### **Hardware Requirements**

- Raspberry Pi or any system capable of running Python.
- Access to a **Kuksa Data Broker** instance.

### **Software Requirements**

- Python 3.7+
- TensorFlow 2.x
- `kuksa-client` Python library
- Standard Python libraries: `numpy`, `json`, `argparse`

Install required Python libraries:

```bash
pip install tensorflow numpy
```

---

## **Usage**

### **Run the Script**

Save the script as `data_eval_client.py` and execute it with the following command:

```bash
python3 data_eval_client.py -th <host> -tp <port> -m <model_path> [-w <write_to_file>] [-o <output_file>] [-i <interval>] [--verbose]
```

### **Arguments**

| **Argument**     | **Description**                                         | **Default**           |
| ---------------- | ------------------------------------------------------- | --------------------- |
| `-th, --host`    | Hostname of the Kuksa Data Broker.                      | `localhost`           |
| `-tp, --port`    | Port of the Kuksa Data Broker.                          | `55555`               |
| `-w, --write`    | Whether to write telemetry data to a JSON file.         | `False`               |
| `-o, --output`   | Output JSON file path for telemetry data.               | `telemetry_data.json` |
| `-m, --model`    | Path to the pre-trained TensorFlow model. **Required**. |                       |
| `-i, --interval` | Time interval (in seconds) between data polling.        | `0.1`                 |
| `--verbose`      | Print telemetry data and predictions to the console.    | Disabled              |

---

## **Example Command**

```bash
python3 data_eval_client.py -th localhost -tp 55555 -m lstm_model.h5 -w True -o telemetry.json -i 0.5 --verbose
```

---

## **Troubleshooting**

1. **Connection Issues**:

   - Verify that the Kuksa Data Broker is running and accessible at the specified host and port.
   - Check the network connectivity between the client and the broker.

2. **TensorFlow Model Compatibility**:

   - Ensure the LSTM/GRU TensorFlow model matches the input shape and features used in the script.

3. **Error Handling**:
   - Enable verbose mode (`--verbose`) to debug issues with telemetry data or predictions.

---

For further questions or support, feel free to reach out!
