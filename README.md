# mini-TOR

**mini-TOR** is a simplified anonymization system inspired by Tor (The Onion Router). It is designed to tunnel TCP traffic through an intermediate proxy node to protect user identity.

## Project Overview
The system allows a client to connect to a chosen intermediate node using a secure tunnel. Unlike the original Tor network, this implementation uses a single intermediate node that connects directly to the target destination.

## Key Features
* **TLS Tunneling:** Communication between the client and the node is encrypted using TLS.
* **Traffic Obfuscation:** The proxy node introduces pseudorandom delays and modifies stream segmentation/resizing to hinder statistical traffic analysis.
* **Developer Library:** The final product includes a Python mini-library providing a pre-connected socket for easy integration into applications.
* **Containerized Environment:** Every component (client, node, and target server) runs within its own container.

## Security & Privacy
* **Anonymity:** The system hides traffic details from telecommunication operators, server administrators, and local eavesdroppers.
* **Trust Model:** As a single-hop proxy, the node must decrypt and re-encrypt data. Therefore, the security of the client depends on the integrity of the intermediate node.

## Error Handling
The proxy node is designed to be self-sustaining. In case of timeouts or connection errors (e.g., unreachable target server), the node will notify the client, terminate the current connection, and return to listening for new requests.

## Development Roadmap
The project is divided into the following implementation phases:
1. Establishing a basic TCP connection between containers.
2. Implementing tunneling with a fixed server address.
3. Enabling the client to pass the target address to the node.
4. Wrapping client logic into a reusable library.
5. Integrating pseudorandom delays and traffic segmentation.

## Demonstration
The success of the implementation will be demonstrated by:
* Verifying that the target server sees the connection coming from the node's IP, not the client's.
* Demonstrating variable transfer speeds as evidence of the random delay mechanism.

## Team
* **Wojciech Kukiełka**
* **Tomasz Okoń**
* **Adam Szkolaski**
