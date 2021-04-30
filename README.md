# pyCoin
Experimental blockchain/cryptocurrency written in python

## Getting Started
pyCoin is my personal project to learn and experiment with blockchain technology. It uses a proof of work consensus protocol like bitcoin and all the communication between the nodes is done through a web api designed in Flask.

### Requirements
Python >= 3.6 is required to run and the following dependencies
```
pip3 install Flask
pip3 install requests
```

## How to Execute
First you need to start the app in the systems you want or you can use one system by providing different ports each time you start it. For example for two instances you can do the following
```
python3 pyCoin.py -p 4000
python3 pyCoin.py -p 4001
```
## How to configure
Currently you need to add the nodes manually using the web api. For our example of two systems on the same machine you can do the following
```
curl --header "Content-Type: application/json" --request POST --data '{"nodes": ["http://127.0.0.1:4001"]}' http://localhost:4000/add_node
curl --header "Content-Type: application/json" --request POST --data '{"nodes": ["http://127.0.0.1:4000"]}' http://localhost:4001/add_node

```

### Playing around
In case you need to see how things work you can start three instances of the app in ports 4000, 4001, 4002 and use the load_data.sh script


## Web API
Currently the following api calls are supported:

Add a node
```
curl --header "Content-Type: application/json" --request POST --data '{"nodes": ["http://127.0.0.1:4001"]}' http://localhost:4000/add_node
```
Add a transaction in a node
```
curl --header "Content-Type: application/json" --request POST --data '{"sender": "alice","receiver": "bob","amount": 500}' http://localhost:4000/add_transaction
```
Mine a block in a node
```
curl localhost:4000/mine_block
```
Retrieve the chain that a node has
```
curl localhost:4000/get_chain
```
Check if chain is valid on the node
```
curl localhost:4000/is_valid_chain
```
Use and validate the longest recorded chain of the network
```
curl localhost:4000/replace_chain
```
## Example usage
Start the app for two different ports
```
python3 pyCoin.py -p 4000
python3 pyCoin.py -p 4001
```
Add some transactions
```
curl --header "Content-Type: application/json" --request POST --data '{"sender": "alice","receiver": "bob","amount": 500}' http://localhost:4000/add_transaction
curl --header "Content-Type: application/json" --request POST --data '{"sender": "alice","receiver": "carol","amount": 500}' http://localhost:4001/add_transaction
curl --header "Content-Type: application/json" --request POST --data '{"sender": "dean","receiver": "carol","amount": 500}' http://localhost:4001/add_transaction
```
Mine the blocks
```
curl localhost:4000/mine_block
curl localhost:4001/mine_block
```
Retrive the chains
```
curl localhost:4000/get_chain
curl localhost:4001/get_chain
```
Find and use the longest chain
```
curl localhost:4000/replace_chain
curl localhost:4001/replace_chain
```
Verify it is changed
```
curl localhost:4000/get_chain
curl localhost:4001/get_chain
```
