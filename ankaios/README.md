
## Ankaios Deployment Guide
This guide explains how to deploy our system by using Ankaios

## Overview

The ankaios deployment configulation is designed to:

1. Deploy  **Kuksa Data Broker** on a Raspberry Pi acting as both the Ankaios server and Agent A. 
2. Deploy **G29 Publisher** on another Raspberry Pi as Agent B. 

The **Kuksa Data Broker** listens on `192.168.1.99:55555`. You can connect any Kuksa client to interact with the broker.


## **Prepare the environment**:
* Connect 2 Raspberry Pis to the same network.
  * OS used were Ubuntu 24.04.1 and raspberrypi 6.6.51.
  * IP of raspberry pi for server should be 192.168.1.99
* install ankaos v0.5.0 
* install podman v3.4.4

please see : https://eclipse-ankaios.github.io/ankaios/latest/usage/installation/



## Folder Structure
```
.
├── README.md
├── deployment.yaml  # Deployment configuration file 
├── startup-agent-a.sh # Script to set up Raspberry Pi as Ankaios server and Agent A  # Script to set up another Raspberry Pi as Ankaios Agent B
├── startup-agent-b.sh
├── test # Simple deployment configuration files to test(& learn) Ankaios behavior
└── val.json # custom VSS definition for kuksa broker
```


## Deployment Steps

1. **Set up the Ankaios server and Agent A**:
   - Git clone and move to `challegers/ankaios` on the first Raspberry Pi.
   - run the following command:
     ```bash
     ./startup-agent-a.sh
     ```
   - This script configures the device as the Ankaios server and Agent A.

1. **Set up Ankaios Agent B**:
   - Git clone and move to `challegers/ankaios` on the second Raspberry Pi.
   - run the following command:
     ```bash
     ./startup-agent-b.sh
     ```
   - This script configures the device as Ankaios Agent B.

1. **Check the connected agents**
   - run the following command on one of Raspberry Pi.
   ```
   ank -k get agents
   ```
   It should print:

   ```
   NAME           WORKLOADS      CPU USAGE      FREE MEMORY
   agent_A        2              42%            42B
   agent-B        0              42%            42B
   ```

1. **Deploy**
   - run the following command on one of Raspberry Pi.
   ```
   ank -k apply deployment.yaml
   ```
1. **Check the deployment**
   ```
   ank -k get agents
   ```
   It should print:
   ```
   WORKLOAD NAME   AGENT     RUNTIME   EXECUTION STATE          ADDITIONAL INFO
   databroker      agent_A   podman    Running(Ok)
   g29-publisher   agent_B   podman    Running(Ok)
   ```

## Containerizing Applications

both application (**Kuksa Data Broker** and **G29 Publisher**) are already containerized and placed in a container repository.

Kuksa Data Broker
* github: https://github.com/eclipse-kuksa/kuksa-databroker
* container: ghcr.io/eclipse/kuksa.val/databroker:0.4.1

G29 Publisher
* github: https://github.com/Eclipse-SDV-Hackathon-Chapter-Two/challengers/tree/main/G29-publisher
* container: docker.io/bleach31/g29-publisher:latest
