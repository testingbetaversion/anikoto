# 🌀 Anikoto Downloader

> **Download anime from `anikoto.tv` / `anikoto.bz`** 

## Screenshot

![App Screenshot](https://i.imgur.com/VEYUMcn.png)


[![PyPI](https://img.shields.io/pypi/v/anikoto.svg)](https://pypi.org/project/anikoto)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)]()

## Installation

Install from Pypie

```bash
python3 -m pip install anikoto
```

Install from Github

```bash
python3 -m pip install git+https://github.com/testingbetaversion/anikoto.git
```

## Usage/Examples

```bash
anikoto https://anikoto.tv/watch/one-piece-odmau  -p /Users/Downloads  -a sub --range 1129-1129
```
```bash
anikoto "https://anikoto.tv/watch/solo-leveling-ilh08/ep-1"
```

```bash
anikoto "https://anikoto.tv/watch/frieren-beyond-journey-s-end-c6fbj/ep-1" -p /Users/Downloads
```

```bash
anikoto "https://anikoto.tv/watch/bottom-tier-character-tomozaki-2nd-stage-0et8i" -p /Users/Downloads  
```

Default Audio is Dub 
Subs for sub/dub will be downloaded by default

## help

```cmd
 $ anikoto --help
usage: anikoto [-h] [--version] [--debug] [--quality {2160,1440,1080,720,480,360}] [--audio {sub,dub}]
               [--downloader {yt-dlp,N_m3u8DL-RE,ffmpeg}] [--subtitles] [--list] [--last] [--path PATH] [--range RANGE]
               url

Anikoto (https://anikoto.tv/) Downloader

positional arguments:
  url                   Video Url like: https://anikoto.tv/watch/solo-leveling-ilh08/ep-1

options:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --debug               Enable debug mode
  --quality, -q {2160,1440,1080,720,480,360}
                        Choose a Quality
  --audio, -a {sub,dub}
                        Download Audio
  --downloader, -d {yt-dlp,N_m3u8DL-RE,ffmpeg}
                        Downloader
  --subtitles, -ss      Download Subs
  --list                List Episodes
  --last                Only Download Last Episode
  --path, -p PATH       path to save the file
  --range, -r RANGE     Specify episode range (e.g. 1-5) if you want to download only episode 1129 use 1129-1129

Example usage: python3 anikoto.py OPTIONS URL
```



## ❤️ Thanks

This project was made with love. If it has helped you, a ⭐ on GitHub would be greatly appreciated.
