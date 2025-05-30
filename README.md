
# Anikoto Downloader

Dowload anime from anikoto.tv




## Installation

Install Dependencies 

```bash
   pip install bs4 requests yt-dlp
```
    
## Usage/Examples

```python
python3 anikoto.py https://anikoto.tv/watch/one-piece-odmau  -p /Users/Downloads  -a sub --range 1129-1129
```
```python
python3 anikoto.py "https://anikoto.tv/watch/solo-leveling-ilh08/ep-1"
````

```python
python3 anikoto.py "https://anikoto.tv/watch/frieren-beyond-journey-s-end-c6fbj/ep-1" -p /Users/Downloads
```

```python
python3 anikoto.py "https://anikoto.tv/watch/bottom-tier-character-tomozaki-2nd-stage-0et8i" -p /Users/Downloads  --source megaplay
```

Sources: megaplay and Kiwi (Kiwi being Default)
Default Audio is Dub 
Subs for sub/dub are downloaded first

## help

```
>python3 anikoto.py --help
usage: anikoto.py [-h] [--version] [--debug]
                  [--quality {2160,1440,1080,720,480,360}] [--audio {sub,dub}]
                  [--subtitles] [--list] [--last] [--path PATH]
                  [--source SOURCE] [--range RANGE]
                  url

Anikoto (https://anikoto.tv/) Downloader

positional arguments:
  url                   Video Url like: https://anikoto.tv/watch/solo-
                        leveling-ilh08/ep-1

options:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --debug               Enable debug mode
  --quality, -q {2160,1440,1080,720,480,360}
                        Choose a Quality
  --audio, -a {sub,dub}
                        Download Audio
  --subtitles, -ss      Download Subs
  --list                List Episodes
  --last                Only Download Last Episode
  --path, -p PATH       path to save the file
  --source SOURCE       select source
  --range, -r RANGE     Specify episode range (e.g. 1-5) if you want to
                        download only episode 1129 use 1129-1129

Example usage: python3 anikoto.py OPTIONS URL
```
