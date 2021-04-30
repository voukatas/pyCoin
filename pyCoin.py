import sys
import getopt
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Block:

    def __init__(self, index, previous_hash, data, timestamp = None, nonce = 0, current_block_hash = None):
        self.index = index
        self.nonce = nonce
        if timestamp is None:
            self.timestamp = str(datetime.datetime.now())
        else:
            self.timestamp = timestamp
        self.previous_block_hash = previous_hash
        self.data = data
        self.current_block_hash = current_block_hash

    def __str__(self):
        return json.dumps(self.toJSON())

    def toJSON(self):
        response = {'index': self.index,
                    'nonce': self.nonce,
                    'timestamp': self.timestamp,                
                    'previous_block_hash': self.previous_block_hash,
                    'data': self.data,
                    'current_block_hash': self.current_block_hash}
        return response
        

class Blockchain:

    def __init__(self):
        self.chain = []
        self.mempool = []
        self.create_genesis_block(previous_hash = '0')
        self.nodes = set()

    def create_genesis_block(self, previous_hash):
        block = Block(index = (len(self.chain) + 1), previous_hash = previous_hash, data = self.mempool)        
        self.proof_of_work(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def get_block_hash(self, block):
        hashed_block = (str(block.index) + str(block.nonce) + block.timestamp + block.previous_block_hash + str(block.data)).encode()
        #print("hashed block =",hashed_block)
        return hashlib.sha256(hashed_block).hexdigest()

    def proof_of_work(self, block):        
        is_hash_discovered = False
        while is_hash_discovered is False:
            block.timestamp = str(datetime.datetime.now())
            hash_operation = self.get_block_hash(block)
            if hash_operation[:4] == '0000':
                is_hash_discovered = True
                print(f'PoW hash = {hash_operation}')
                block.current_block_hash = hash_operation
                self.mempool = []
                self.chain.append(block)
            else:
                block.nonce += 1                
    
    def is_chain_valid(self, chain):
        #print('is_chain_valid:')
        #self.print_chain(chain)
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            #print(f'previous_block:',previous_block)
            hash_operation = self.get_block_hash(previous_block)            
            if (block.previous_block_hash != hash_operation) or (hash_operation[:4] != '0000'):
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.mempool.append({'sender': sender,
                            'receiver': receiver,
                            'amount': amount})
        return self.get_previous_block().index + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    #convert json list of objects to block objects
    def json_chain_to_obj(self, chain):
        obj_list = []
        for obj in chain:
            block = Block(index = obj['index'], previous_hash = obj['previous_block_hash'], timestamp = obj['timestamp'], data = obj['data'], nonce = obj['nonce'], current_block_hash = obj['current_block_hash'])
            obj_list.append(block)        
        return obj_list

    # longest chain is King
    def replace_chain(self):
        longest_chain = None
        max_len = len(self.chain)
        for node in self.nodes:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                #print(f'max_len:{max_len}')
                #print(f'length:{length}')
                #print(f'chain:{chain}')                
                if length > max_len:
                    chain_of_objects = self.json_chain_to_obj(chain)
                    #self.print_chain(chain_of_objects)
                    #print(f'value: {self.is_chain_valid(chain_of_objects)}')                    
                    if self.is_chain_valid(chain_of_objects):
                        max_len = length
                        longest_chain = chain_of_objects
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
    def chain_toJSON(self):
        chain = [block.toJSON() for block in self.chain]
        #print("chain1::",chain)
        return chain

    def print_chain(self, chain_of_objects):
        for obj in chain_of_objects:
            print(f'object in chain: {obj}')

# flask
app = Flask(__name__)

# Mine a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    if not blockchain.mempool:
        response = {'message': 'Error: No transactions found!'}
        return jsonify(response), 403
    previous_block = blockchain.get_previous_block()
    previous_hash = blockchain.get_block_hash(previous_block)
    # reward for miner
    blockchain.add_transaction(sender = node_address, receiver = node_address, amount = 100)
    # create new block
    new_block = Block(index = (len(blockchain.chain) + 1), previous_hash = previous_hash, data = blockchain.mempool)
    blockchain.proof_of_work(new_block)    
    response = {'message': 'Congrats! New block on the hood!',
                'index': new_block.index,
                'timestamp': new_block.timestamp,                
                'previous_hash': new_block.previous_block_hash,
                'data': new_block.data,
                'current_block_hash': new_block.current_block_hash}
    return jsonify(response), 200

# Return all the records of the Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain_toJSON(),
                'length': len(blockchain.chain)}    
    return json.dumps(response),200

# Validate the Blockchain
@app.route('/is_valid_chain', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'The Blockchain is valid!'}
    else:
        response = {'message': 'The Blockchain is NOT valid!'}
    return jsonify(response), 200

# Add transaction
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    req_json = request.get_json()
    tx_keys = ['sender','receiver','amount']
    if not all (key in req_json for key in tx_keys):
        return 'Error: Missing keys in tx', 400
    index = blockchain.add_transaction(req_json['sender'],req_json['receiver'],req_json['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/add_node', methods = ['POST'])
def add_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No nodes found", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Nodes added',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The chain is replaced',
                    'new_chain': blockchain.chain_toJSON()}
    else:
        response = {'message': 'The chain is NOT replaced, it is the largest',
                    'chain': blockchain.chain_toJSON()}
    return jsonify(response), 200

if __name__ == '__main__':    
    # default port
    server_port = 4000

    # read arguments
    try:
      opts, args = getopt.getopt(sys.argv[1:],"hp:",["port="])
    except getopt.GetoptError:
      print (sys.argv[0],'-p PortNumber')
      sys.exit(2)    
    if not opts:
        print (sys.argv[0],'-p PortNumber')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print (sys.argv[0],'-p PortNumber')
            sys.exit()
        elif opt in ("-p", "--port"):
            server_port = arg
        else:
            print (sys.argv[0],'-p PortNumber!')
            sys.exit()

    # create node address
    node_address = str(uuid4()).replace('-','')
    # Blockchain init
    blockchain = Blockchain()
    # Start flask app    
    app.run(host = '0.0.0.0', port = server_port)
    #app.run(host = '127.0.0.1', port = 5000)