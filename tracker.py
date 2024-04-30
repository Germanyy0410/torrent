from flask import Flask, request, jsonify # type: ignore
import hashlib
import random
import json
import os
import socket
import time

peers = {}

#* ============================ TRACKER SYSTEM ============================
def get_ip():
    hostname = socket.gethostname()
    os.environ['CURRENT_IP'] = socket.gethostbyname(hostname)
    with open('.env', 'w') as env_file:
        env_file.write(f"CURRENT_IP={os.getenv('CURRENT_IP')}")

app = Flask(__name__)
if __name__ == '__main__':
	get_ip()

@app.route('/announce', methods=['GET'])
def announce():
	# Get parameters from the request
	path = request.args.get('path')
	peer_id = request.args.get('peer_id')
	port = request.args.get('port')
	ip = request.args.get('ip')

	# Generate peer dictionary key
	peer_key = hashlib.sha1((peer_id + ip).encode()).hexdigest()
	peers[peer_key] = {
		'path': path,
		'peer_id': peer_id,
		'port': port,
		'ip': ip,
	}

	response = {
		'peers': list(peers.values())
	}

	return jsonify(response)


@app.route('/get_peers', methods=['GET'])
def get_peers():
	return jsonify(peers)

#* ========================================================================

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=False)
