from flask import Flask, request, jsonify # type: ignore
import hashlib
import random
import json
import os
import socket

# Dictionary to store peer information
peers = {}

# ======================== TRACKER SYSTEM ========================
def get_ip():
  hostname = socket.gethostname()
  os.environ['CURRENT_IP'] = socket.gethostbyname(hostname)
  with open('.env', 'w') as env_file:
    env_file.write(f"CURRENT_IP={os.getenv('CURRENT_IP')}")

app = Flask(__name__)
get_ip()

@app.route('/announce', methods=['GET'])
def announce():
  # Get parameters from the request
  info_hash = request.args.get('info_hash')
  peer_id = request.args.get('peer_id')
  port = request.args.get('port')
  ip = request.args.get('ip')
  chunks = json.loads(request.args.get('tracked_chunks'))

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
        'ip': ip,
        'chunks': chunks
    }

  response = {
    'peers': list(peers.values())
  }

  return jsonify(response)
# ================================================================


# ========================= TODO: MERGE CHUNKS =========================

# ================================================================

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
