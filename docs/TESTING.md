# Testing Instruction: mini-TOR System

This guide explains how to verify the anonymity, traffic shaping, and robustness of the **mini-TOR** project.

## 1. Prerequisites

**Docker & Docker Compose**: Installed on your machine.


**Python 3.11+**: For local unit testing.
**OpenSSL**: To generate the required TLS certificates.



## 2. Environment Setup

Before running the containers, you must generate the TLS certificates used for the secure tunnel.

1. **Generate Certificates**:
Run setup_certs.sh localized in {project_root}/scripts while being in project root directory.


2. **Build and Start Containers**:
Launch the Client, Node, and Target Server.


```bash

cd deployments
docker-compose up --build

```



---

## 3. Functional Testing (The Demonstration)

Verify that the system masks your identity and applies traffic delays.

### Step 1: Run the Demo Client

Execute the client application inside the running container.

```bash
docker exec -it demo-client python3 -m demo.client_app

```

### Step 2: Verify Anonymity

Check the logs of the `target-server` container.

**Success**: The logs should show a connection from the IP of **`proxy-node.local`**, not the `demo-client`.



### Step 3: Verify Traffic Shaping

Observe the data arrival in the client terminal.

**Success**: The response should arrive in chunks with visible, pseudorandom pauses between segments.



---

## 4. Unit Testing

Run the automated test suite to verify individual components.

1. **Install Pytest**:
```bash
pip install pytest

```


2. **Run Tests**:
From the project root, execute:
```bash
python -m pytest

```



### Test Coverage Areas:

* **Protocol**: Validates `CONNECT` request parsing and generation.
* **Shaper**: Verifies data segmentation logic and random delay timing.
* **Socket**: Mocks the TLS tunnel to test connection state management.

---