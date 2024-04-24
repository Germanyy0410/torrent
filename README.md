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


# Up-coming Tasks

- Download từ nhiều peers
- Xoá các file ```.part```, tự generate mỗi khi run code
- Upload file (seeder)
- Report


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
