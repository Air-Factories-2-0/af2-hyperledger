# Prerequisiti  

* git
* curl
* go  
* docker  
* docker-compose  
* node
* npm

# Set up ambiente di sviluppo 

## Installazione di hyperledger fabric (v2.3.2)

Eseguire il comando  
`curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.3.2 1.5.0`

## Creazione immagine peer

* Scaricare fabric  
`git clone https://github.com/hyperledger/fabric.git`  
* Spostarsi all'interno della cartella scaricata  
`cd fabric`  
`git checkout v2.3.2`  
* Copiare il Dockerfile e lo script di python all'interno della cartella, con il nome `script.py`  
* Creare l'immagine
`docker build . -t custom_peer`
* Spostare il file `network-config/docker-compose-test-net.yaml` all'interno della cartella `fabric-samples/test-network/docker/` 

## External builders

* Creare una cartella chiamata `config-edit` all'interno di `fabric-samples/test-network/`  
* Spostare il file `network_config/core.yaml` all'interno di `fabric-samples/test-network/config-edit/`
* Spostare la cartella external-builder all'interno di `fabric-samples/test-network`
* Dare i permessi di esecuzione agli script presenti all'interno di `external-builder/bin/`  eseguendo `chmod +x *` all'interno della cartella bin

## Creazione container docker di ipfs

### creazione delle directory per importazione e esportazione dei dati  

Creare due cartelle quindi eseguire i seguenti comandi specificando il path delle cartelle create
<pre><code>export ipfs_staging=/absolute/path/to/somewhere/  
export ipfs_data=/absolute/path/to/somewhere_else/</pre></code>  

### Avvio del container

<pre><code>docker run -d --name ipfs_host -v $ipfs_staging:/export -v $ipfs_data:/data/ipfs -p 4001:4001 -p 4001:4001/udp -p 127.0.0.1:8080:8080 -p 127.0.0.1:5001:5001 ipfs/go-ipfs:latest</pre></code>

## Avvio di hyperledger

eseguire `app/script.sh` specificando come argomento il path di `fabric-samples/test-network`  

## Installazione del chaincode  

Eseguire  
`./network.sh deployCC -ccl go -ccp CHAINCODE_PATH -ccn chaincode` sostituendo il path del chaincode a CHAINCODE_PATH  

## Avvio del server

All'interno di `app` eseguire i comandi  
`npm install`  
`node enrollAdmin.js`  
`npm start`  
