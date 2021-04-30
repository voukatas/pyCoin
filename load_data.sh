#!/bin/bash

# insert nodes
curl --header "Content-Type: application/json" --request POST --data '{"nodes": ["http://127.0.0.1:4001","http://127.0.0.1:4002"]}' http://localhost:4000/add_node
curl --header "Content-Type: application/json" --request POST --data '{"nodes": ["http://127.0.0.1:4000","http://127.0.0.1:4002"]}' http://localhost:4001/add_node
curl --header "Content-Type: application/json" --request POST --data '{"nodes": ["http://127.0.0.1:4000","http://127.0.0.1:4001"]}' http://localhost:4002/add_node

# insert data and mine block
curl --header "Content-Type: application/json" --request POST --data '{"sender": "alice","receiver": "bob","amount": 500}' http://localhost:4000/add_transaction
curl localhost:4000/mine_block
curl --header "Content-Type: application/json" --request POST --data '{"sender": "alice","receiver": "bob","amount": 550}' http://localhost:4001/add_transaction
curl localhost:4001/mine_block
curl --header "Content-Type: application/json" --request POST --data '{"sender": "alice","receiver": "bob","amount": 600}' http://localhost:4002/add_transaction
curl localhost:4002/mine_block
curl --header "Content-Type: application/json" --request POST --data '{"sender": "alice","receiver": "bob","amount": 1000}' http://localhost:4002/add_transaction
curl localhost:4002/mine_block

# check and change the chain
curl localhost:4000/replace_chain
curl localhost:4001/replace_chain
curl localhost:4002/replace_chain
