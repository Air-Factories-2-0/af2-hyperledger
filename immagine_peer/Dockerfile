FROM golang:buster as peer-base
RUN apt-get install tzdata
RUN echo 'hosts: files dns' > /etc/nsswitch.conf

FROM golang:buster as golang
RUN apt-get install bash \
	gcc \
	git \
	make \
	libc6

ADD . $GOPATH/src/github.com/hyperledger/fabric
WORKDIR $GOPATH/src/github.com/hyperledger/fabric

FROM golang as peer
ARG GO_TAGS=""
RUN make peer GO_TAGS=${GO_TAGS}

FROM peer-base

RUN apt-get update
RUN apt-get install jq wget gcc -y
RUN apt install wget software-properties-common build-essential libnss3-dev zlib1g-dev libgdbm-dev libncurses5-dev   libssl-dev libffi-dev libreadline-dev libsqlite3-dev libbz2-dev
RUN wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz
RUN tar xvf Python-3.9.10.tgz
RUN .Python-3.9.10/configure --enable-optimizations
RUN .Python-3.9.10/make altinstall

RUN apt-get install python3-pip -y
RUN apt-get install python3-opencv -y
RUN pip install matplotlib 
RUN pip install rembg 


ENV FABRIC_CFG_PATH /etc/hyperledger/fabric
VOLUME /etc/hyperledger/fabric
VOLUME /var/hyperledger
VOLUME /python/scripts
COPY --from=peer /go/src/github.com/hyperledger/fabric/build/bin /usr/local/bin
COPY --from=peer /go/src/github.com/hyperledger/fabric/sampleconfig/msp ${FABRIC_CFG_PATH}/msp
COPY --from=peer /go/src/github.com/hyperledger/fabric/sampleconfig/core.yaml ${FABRIC_CFG_PATH}
EXPOSE 7051
CMD ["peer","node","start"]
