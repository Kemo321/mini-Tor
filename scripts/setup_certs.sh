#!/bin/bash
echo "[*] Creating project directory structure..."
mkdir -p certs src/minitor src/node src/shared demo deployments

echo "[*] Generating TLS Certificates for node..."
openssl req -new -x509 -days 365 -nodes \
    -out certs/node.crt \
    -keyout certs/node.key \
    -subj "/CN=proxy-node.local"

echo "[*] Generating TLS Certificates for server..."
openssl req -new -x509 -days 365 -nodes \
    -out certs/server.crt \
    -keyout certs/server.key \
    -subj "/CN=proxy-node.local"

echo "[+] Setup complete. You can now run: docker-compose up --build"