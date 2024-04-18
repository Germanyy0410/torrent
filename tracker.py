from flask import Flask, request, jsonify # type: ignore
import hashlib
import random
import json
# from dotenv import load_dotenv # type: ignore
import os
import socket
app = Flask(__name__)

def get_ip():
  hostname = socket.gethostname()
  ip = socket.gethostbyname(hostname)
  return ip

os.environ['CURRENT_IP'] = get_ip()
print(os.environ['CURRENT_IP'])

# Dictionary to store peer information
peers = {}

@app.route('/announce', methods=['GET'])
def announce():
    # Get parameters from the request
    info_hash = request.args.get('info_hash')
    peer_id = request.args.get('peer_id')
    port = request.args.get('port')

    # Generate peer dictionary key
    peer_key = hashlib.sha1((info_hash + peer_id).encode()).hexdigest()

    # Update peer information or add new peer
    if peer_key in peers:
        peers[peer_key]['port'] = port
        peers[peer_key]['ip'] = request.remote_addr
    else:
        peers[peer_key] = {
            'peer_id': peer_id,
            'port': port,
            'ip': request.remote_addr
        }

    # Generate response
    response = {
        'peers': list(peers.values())
    }

    print(json.dumps(response, indent=4))

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
