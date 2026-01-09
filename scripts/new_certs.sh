mkdir -p demo/certs/ certs/

openssl req -new -x509 -days 365 -nodes \
    -out demo/certs/server.crt \
    -keyout demo/certs/server.key \
    -subj "/CN=target-server.com"

openssl req -new -x509 -days 365 -nodes \
    -out certs/node.crt \
    -keyout certs/node.key \
    -subj "/CN=proxy-node.local"