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

# Torrent Application

An application created in Computer Network Course - CO3093

## I. Module description

- ```main.py```: Main file to request download Torrent
- ```tracker.py```: Start local tracker using Flask
- ```peer.py```: Connect to tracker (run on Ubuntu)

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
python tracker.py
```

4. Connect peer(s) to tracker by:

 ```bash
python peer.py
```

5. To start download torrent, run:

 ```bash
python main.py
```

### Commands

•  ```b-create <path> <tracker-url>```: Create a .torrent file for the content at the specified path, with the given tracker URL.

•  ```b-show```: Display all managed torrent files, helping you keep track of your torrents easily.

•  ```b-info <torrent-file>```: View metadata associated with a .torrent file, such as file names, sizes, and hash values.

•  ```b-start <torrent-file>```: Start downloading files from the specified .torrent file seamlessly.

•  ```b-edit <torrent-file> <new-tracker-url>```: Modify the announce URL of a .torrent file, providing flexibility in managing torrents efficiently.

•  ```b-help```: View all commands and usages.

•  ```b-close```: Close the application.
