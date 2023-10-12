# Blockchain_Project

## Setup: Can be installed in windows and linux
1. Install Postgres. Create user "admin_ems" with password "iamadmin@123"
2. Install ipfs desktop.
3. Make sure postgres runs on port 5432 and ipfs runs on port 5001
4. Clone this repository. Goto the cloned folder. Create a python virtual environment using `` python -m venv virtualvenv ``
5. Activate the virtual environment using `` virtualenv\Scripts\activate `` in Windows and `` source virtualenv/bin/activate `` in Linux
6. Install all packages using `` pip install -r requirements.txt ``
7. Then follow the following steps:
- ``python manage.py makemigrations``
- ``python manage.py migrate``
- ``python manage.py createsuperuser``
- ``python manage.py runserver`` to start the server

![Image of Flow Chart](https://raw.githubusercontent.com/TXH2020/Blockchain_Project/main/Blockchain_Project.png)

## Background of the Project Development:
The entire development was done on a Kali Linux VM with 4GB RAM and 2 CPU's. It is a resource constrained environment for the project yet the web development part and IPFS were successfully tested and integrated.

The web development part was done using Django which allow rapid development of secure and powerful websites. The most useful feature provided by Django is the Admin console which is at the core of the web system. It is through this that we add new users(teachers, COEs, superintendents) along with subject codes to the system. Django server side rendering allows us to dynamically server web pages.
We used postgres db as Django has special support for postgres and it is much more scalable compared to MySQL.

The IPFS is the decentralized blockchain storage that is used in our project. However, the hash(UID of file) generated by IPFS is currently stored in a database. To install IPFS, the binary source files were used and installed in the system's PATH environment variable. An ultralight node(for development and resource constrained purposes) was initialized. Then CORS access was enabled. The below commands summarize this discussion:
- ipfs init --profile=lowpower
- ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '["*"]'
- ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods '["PUT", "GET", "POST"]'
- ipfs config --json API.HTTPHeaders.Access-Control-Allow-Credentials '["true"]'
Later the IPFS server(daemon) was started using the following command: `` ipfs daemon ``. IPFS desktop can be used due to its more convenient UI but since it is too heavy for the VM it is avoided.

The original plan was to the hyperledger fabric with hyperledger compose as an intermediator between the web system and the fabric, where the hyperledger would store the file hash with some other information. But hyperledger compose was found unsuitable because it's development has been stalled, it uses python2 and its developers recommend developing smart contracts using hyperledger fabric SDK's.

The hyperledger fabric installation process is based on docker. This is a brilliant idea because we can spin up an a peer to peer network with more than one nodes in a single machine. Hyperledger fabric requires Go programming language hence the latest Go version was installed. It also requires some predefined environment variables to be setup.

The hyperledger has been successfully tested. Hence it was felt to use a python SDK which would allow us to integrate the hyperledger with the web system. However this was unsuccessful because of the following:
- python sdk is not official and does not have proper tutorials.
- It requires the use of a network profile which is a JSON file that must be manually set.
- The usage of Certificate Authorities is the most difficult part. The private and public keys have to be copied from the docker containers and pasted in the configuration files of the python SDK. Otherwise the SSL Handshake fails due to certificate verification failure. This was encountered during the development.

## Steps to fully configure project(on Linux only). Note that you must install golang, docker and hyperledger fabric:

Make sure the below lines are present in the bashrc file:
- export PATH=$PATH:/usr/local/go/bin/
- export GOPATH=$HOME/go
- export PATH=/home/kali/fabric-samples/bin:$PATH
- export FABRIC_CFG_PATH=/home/kali/fabric-samples/config/
- export CORE_PEER_TLS_ENABLED=true
- export CORE_PEER_LOCALMSPID="Org1MSP"
- export CORE_PEER_TLS_ROOTCERT_FILE=/home/kali/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
- export CORE_PEER_MSPCONFIGPATH=/home/kali/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
- export CORE_PEER_ADDRESS=localhost:7051

Then run the following commands:
- ipfs daemon
- sudo docker run --name some-postgres3 -p 5432:5432 -e POSTGRES_USER=admin_ems -e POSTGRES_PASSWORD=iamadmin@123 -d postgres
- Use this command if above container is stopped: sudo docker start some-postgres3

Place smartcontract.go present in this repo instead of fabric-samples/asset-transfer-basic/chaincode-go/../smartcontract.go
Goto the fabric samples/test network.
- sudo ./network.sh up
- sudo ./network.sh createChannel
- sudo ./network.sh deployCC  -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go

Goto the Blockchain_Project folder and run the following commands
- sudo su
- source <bashrc_loc>/.bashrc
- source <virtualenv>/bin/activate

Now open a browser. Open localhost:8000. Then open a private tab and goto localhost:8000/admin and enter django superuser credentials.

Then the flow is as follows:

In admin
- Add subject code
- Add COE with subject code.
- Add Teacher with subject code.
- Add Superintendent with subject code.

In other tab
- Login as COE. Submit. Send request.
- Login as Teacher. Submit paper.  ->CreateAsset
- Login as COE. Finalize paper.    ->ReadAsset
- Login as superintendent. Download paper.
