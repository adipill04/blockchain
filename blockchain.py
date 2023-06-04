import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash = 1, proof=100)
        
    def new_block(self, proof):
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': hash(self.last_block())
        }
        self.chain.append(block)
        self.current_transactions = []
        return block

    def new_transaction(self,sender,recipient,amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    
    @staticmethod
    def hash(block):
        blockString = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, last_proof):
        num = 0
        while(self.valid_proof(last_proof,num) is False):
            num+=1
        return num 
 
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    lb = blockchain.last_block()
    ans = blockchain.proof_of_work(lb['proof'])
    
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    block = blockchain.new_block(ans)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response),200
  
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'missing values', 400
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



