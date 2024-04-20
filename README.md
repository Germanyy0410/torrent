# Torrent Application

An application created in Computer Network Course - CO3093

## I. Module description

- ```main.py```: Main file to request download Torrent
- ```tracker.py```: Start local tracker using Flask
- ```peer.py```: Connect to tracker (run on Ubuntu)
- ```peer.json```: Store list of peers connected to tracker

## II. Installation

To install all the required packages, run the following command:

```bash
pip install -r ref/requirements.txt
```

## III. Getting Started

1. Clone the repository:

```bash
git clone https://github.com/Germanyy0410/torrent.git
```

2. Naviagte to the project directory:

```bash
cd torrent
```

3. Start the tracker:

```bash
cd python tracker.py
```

4. Connect peer(s) to tracker by:

 ```bash
cd python peer.py
```

5. To start download torrent, run:

 ```bash
cd python main.py
```
