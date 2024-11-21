# Environment setup

```sh
# create a python virtual environment
python3 -m venv vehicle-dashboard-venv

# Activate the virtual environment
source ./vehicle-dashboard-venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt

# set the following environment variables
export BROKER_ADDRESS="127.0.0.1"

export BROKER_PORT=55555
 ```

# Run dashboard

```sh
python main.py
 ```
