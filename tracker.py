from flask import Flask, request, jsonify # type: ignore
import hashlib
import random
import json
import os
import socket
app = Flask(__name__)

def get_ip():
  hostname = socket.gethostname()
  os.environ['CURRENT_IP'] = socket.gethostbyname(hostname)
  with open('.env', 'w') as env_file:
    env_file.write(f"CURRENT_IP={os.getenv('CURRENT_IP')}")

get_ip()

# Dictionary to store peer information
peers = {}

@app.route('/announce', methods=['GET'])
def announce():
  # Get parameters from the request
  info_hash = request.args.get('info_hash')
  peer_id = request.args.get('peer_id')
  port = request.args.get('port')
  ip = request.args.get('ip')

  # Generate peer dictionary key
  peer_key = hashlib.sha1((info_hash + peer_id).encode()).hexdigest()

  # Update peer information or add new peer
  if peer_key in peers:
    peers[peer_key]['port'] = port
    peers[peer_key]['ip'] = ip
  else:
    peers[peer_key] = {
        'peer_id': peer_id,
        'port': port,
        'ip': ip
    }

  # Generate response
  response = {
    'peers': list(peers.values())
  }

  print(json.dumps(response, indent=4))

  return jsonify(response)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
