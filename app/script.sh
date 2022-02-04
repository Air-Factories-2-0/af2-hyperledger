#!/bin/bash

# avvia il test network e copia i file necessari alla connessione

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# export TEST_NETWORK="/home/andrea/go/src/github.com/sapone.andrea/fabric-samples/test-network"
export TEST_NETWORK=$1

rm -rf "./connection"
rm -rf "./wallet"
mkdir "./connection"
mkdir "./wallet"

docker network disconnect fabric_test ipfs_host
cd "$TEST_NETWORK"
./network.sh down

./network.sh up createChannel -ca

docker network connect fabric_test ipfs_host
cp "./organizations/peerOrganizations/org1.example.com/connection-org1.json" "${DIR}/connection/"
cp "./organizations/peerOrganizations/org2.example.com/connection-org2.json" "${DIR}/connection/"
