<strong><div align="center">
HO CHI MINH CITY
UNIVERSITY OF TECHNOLOGY
<br />
FACULTY OF COMPUTER SCIENCE AND ENGINEERING
<br />
<br />

[![N|Solid](https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/HCMUT_official_logo.png/238px-HCMUT_official_logo.png)](https://hcmut.edu.vn/)
<br /></strong>
<br />

**Computer Network - Semester 232**
<br/>
<br/>

</div>

# BitTorrent Application

In our Computer Network Course - CO3093, we have developed a simple BitTorrent application. This application includes features such as creating .torrent files, editing tracker URLs of .torrent files, and facilitating the download/upload of pieces from multiple clients.

## Workflow

### 1. Tracker Server

We've set up a local tracker server using Flask framework to act as a crucial link between peers. It keeps track of which files are available and who has them, helping peers connect and communicate more smoothly. Our tracker server has two main routes:

- ```/announce```: This route handles GET requests from peers. When a peer sends a request here, the server extracts information and then adds the peer's information to a dictionary.
- ```/get_peers```: This route also handles GET requests. When a client requests this endpoint, it receives the peer dictionary as JSON.

### 2. Active Peers

To become an active peer, one must send a GET request to the Tracker Server, providing essential information such as peer_id, path, port, and IP address.

### 3. BitTorrent Client

- At first, client make a GET request to get all of active peers from Tracker Server.

#### Download

- For each file in .torrent file:
  - Initialize a Thread and allocate a peer to download from.
  - The client then requests the peer to send the file's bit field.
  - Next, download all missing pieces from the peers concurrently.
  - If the file still lacks pieces, assign another peer to continue downloading.

#### Upload

- For every active peer:
  - If a peer is missing pieces, initiate a new Thread.
  - Check the bit field for each file to determine which pieces are missing from the peer.
  - Simultaneously begin uploading pieces from the client to all peers.

## Basic Commands

- ```b-create <path> <tracker-url>```: Create a .torrent file for the content at the specified path, with the given tracker URL.

- ```b-edit <torrent-file> <new-tracker-url>```: Modify the announce URL of a .torrent file, providing flexibility in managing torrents efficiently.

- ```b-show```: Display all managed torrent files, helping you keep track of your torrents easily.

- ```b-info <torrent-file>```: View metadata associated with a .torrent file, such as file names, sizes, and hash values.

- ```b-peer```: View all peers that connected to tracker server.

- ```b-start <torrent-file>```: Start downloading files from the specified .torrent file seamlessly.

- ```b-help```: View all commands and usages.

- ```b-close```: Close the application.

## Getting Started

1. Clone my repository:

```bash
git clone https://github.com/Germanyy0410/torrent.git
```

2. Navigate to the project directory and install all the required packages:

```bash
pip install -r ref/requirements.txt
```

3. Create the following empty folders to store the completed files from our torrent files.

```bash
mkdir output/books
mkdir output/slides
mkdir output/videos
```

1. Start the local Tracker Server:

```bash
python tracker.py
```

5. Connect peer(s) to Tracker Server by:

 ```bash
python peer.py
```

6. To start our main application, run:

 ```bash
python main.py
```
