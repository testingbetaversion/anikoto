import requests
import argparse
from traceback import format_exc

import logging
import os
import datetime
import re
from bs4 import BeautifulSoup
import base64
import yt_dlp

class CustomFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[31m',      # Red
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[36m',    # Cyan
        'ERROR': '\033[33m',      # Yellow
        'CRITICAL': '\033[31m\033[47m\033[1m',  # Red text on white background, bold
    }
    RESET = '\033[0m'  # Reset to default color

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        reset_color = self.RESET
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        process_id = os.getpid()
        log_message = f"{log_color}{timestamp}:{process_id}:{record.levelname}:{record.name}:{reset_color}{log_color}{record.msg}{reset_color}"
        return log_message

def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)    


configure_logging()

def download(url, referer, path, anime, title, number):
    if not os.path.exists(f"{path}/{anime}"):
        os.makedirs(f"{path}/{anime}")
    logging.info(f"Downloading E{number} {title} from {url}")
    if os.path.exists(f"{path}/{anime}/{anime} E{number} {title}.mp4"):
        logging.info(f"File already exists: {path}/{anime}/{anime} E{number} {title}.mp4")
        return
    ydl_opts = {
        # 'format': 'bv+ba',  
        'http_headers': {'Referer': referer}, 
        'external_downloader': 'aria2c', 
        'paths': {
            'temp': 'temp',  
            'home': f'{path}/{anime}' 
        },
        'outtmpl': f'{anime} E{number} {title}.%(ext)s', 
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    version = "1.0.0"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    })
    parser = argparse.ArgumentParser(description="TheChosen (https://anikoto.tv/) Downloader", epilog="Example usage:\n python3 anikoto.py OPTIONS URL")
    parser.add_argument("--version","-v", action="version", version=f"%(prog)s {version}")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("url", help="Video Url like: https://anikoto.tv/watch/solo-leveling-ilh08/ep-1")
    parser.add_argument("--quality","-q", choices=['2160','1440',"1080", "720", "480",'360'],default="1080", help="Choose a Quality")
    parser.add_argument("--audio", "-a", choices=['sub', 'dub'], default='dub', help="Download Audio")
    parser.add_argument("--subtitles", "-ss", action="store_true",default=True, help="Download Subs")
    parser.add_argument("--list", action="store_true",default=False, help="List Episodes")
    parser.add_argument("--last", action="store_true",default=False, help="Only Download Last Episode")
    parser.add_argument("--path", "-p", help="path to save the file", default=os.getcwd())
    parser.add_argument("--source", default="Kiwi",help="select source",)
    parser.add_argument("--range", "-r", help="Specify episode range (e.g. 1-5) if you want to download only episode 1129 use 1129-1129")


    args = parser.parse_args()



    r = session.get(args.url)
    search = re.search(r'https://anikoto.tv/anime/getinfo/(\d+)', r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    title_element = soup.find('h1', class_='title d-title')
    anime = title_element.get_text(strip=True)
    if not search:
        print("Error: Unable to find the video ID in the provided URL.")
        exit(1)
    video_id = search.group(1)
    r = session.get(f"https://anikoto.tv/ajax/episode/list/{video_id}?vrf=")
    html_code = r.json()['result']


    soup = BeautifulSoup(html_code, 'html.parser')
    episodes = soup.find_all('li', {'data-html': 'true'})
    episode_data = []

    i = 1
    for episode in episodes:
        title = episode.get('title')
        data_ids = episode.find('a').get('data-ids')
        data_mal = episode.find('a').get('data-mal')
        data_timestamp = episode.find('a').get('data-timestamp')
        episode_data.append({'title': title, 'data-ids': data_ids, 'data-mel': data_mal, 'data-timestamp': data_timestamp, 'number': i})
        i+=1
    del i

    for number, data in enumerate(episode_data, start=1):
        print(f"{number}: {data['title']}")
        title = data['title']
        print(f"Data IDs: {data['data-ids']}")
        data_ids = data['data-ids']
        data_mel = data['data-mel']
        print(f"Data MAL: {data_mal}")
        data_timestamp = data['data-timestamp']
        print(f"Data Timestamp: {data['data-timestamp']}")
        print()


    if args.range:
        try:
            start, end = map(int, args.range.split('-'))
            episode_data = episode_data[start-1:end]
            print(f"Downloading episodes {start} to {end}:")
            for number, data in enumerate(episode_data, start=start):
                print(f"{number}: {data['title']}")
        except Exception as e:
            print(f"Invalid range format. Use like '1-5'. Error: {e}")
            exit(1)

    if args.list:
        print("List of Episodes:")
        for number, data in enumerate(episode_data, start=1):
            print(f"{number}: {data['title']}")
        exit(0)

    if args.last:
        episode_data = episode_data[-1:]
        print("Last Episode:")
        for number, data in enumerate(episode_data, start=1):       
            print(f"{number}: {data['title']}")


        
    if 'kiwi' in args.source.lower():
        for data in episode_data:
            number = data['number']
            r = session.get(f"https://mapper.kotostream.online/api/mal/{data['data-mel']}/{number}/{data['data-timestamp']}")
            for stream in r.json():
                if "Stream" in stream and args.quality in stream:
                    print(stream)
                    if args.debug:
                        print(r.json())
                    server_code = r.json()[stream][args.audio]['url']
                    url = "https://anikoto.tv/ajax/server"
                    querystring = {"get":server_code}
                    r = session.get(url, params=querystring)
                    url = r.json()['result']['url']
                    if "#" in url:
                        url = base64.b64decode(url.split("#")[1]).decode('utf-8')
                        download(url, "https://anikoto.tv/", args.path,anime, data['title'], number)


    if 'megaplay' in args.source.lower() or args.subtitles:
    
        for number, data in enumerate(episode_data, start=1): 
            try:
                title = data['title']
                url = "https://anikoto.tv/ajax/server/list"
                querystring = {"servers":data['data-ids']}

                r = session.get(url, params=querystring)
                soup = BeautifulSoup(r.json()['result'], 'html.parser')

                servers = soup.find_all('div', class_='type')

                server_data = []
                for server in servers:
                    server_type = server.get('data-type').upper()  # Get SUB or DUB
                    server_item = server.find('li')  # Find the li element containing data-link-id
                    data_link_id = server_item.get('data-link-id') if server_item else None
                    server_data.append({'type': server_type, 'data-link-id': data_link_id})

                # Print the results
                for data in server_data:
                    print(f"type: {data['type']}")
                    print(f"data-link-id: {data['data-link-id']}")
                    print()


                url = "https://anikoto.tv/ajax/server"
                querystring = {"get":data['data-link-id']}
                r = session.get(url, params=querystring)
                url = r.json()['result']['url']

                r = session.get(url, headers={
                    "referer": "https://anikoto.tv/",
                })

                id_ = re.search(r' data-id=\"(\d+)\"', r.text).group(1)

                r = session.get("https://megaplay.buzz/stream/getSources", params={"id":id_})

                print(r.json()['sources']['file'])
            
                if "tracks" in r.json():
                    for track in r.json()['tracks']:
                        print(f"Track: {track.get('label')} ({track.get('kind')})")
                        if track.get('file'):
                            print(f"Track URL: {track.get('file')}")
                            if not os.path.exists(f"{args.path}/{anime}/{anime} E{number} {title} {track.get('label')}.vtt"):
                                logging.info(f"Downloading subtitles for E{number} {title} {track.get('label')}")
                                s_r = session.get(track.get('file'),headers={
                                    "referer": "https://megaplay.buzz/",
                                })
                                if s_r.status_code == 200:
                                    logging.info(f"{args.path}/{anime}/{anime} E{number} {title} {track.get('label')}.vtt")
                                    if not os.path.exists(f"{args.path}/{anime}/"):
                                        os.makedirs(f"{args.path}/{anime}/")
                                    with open(f"{args.path}/{anime}/{anime} E{number} {title} {track.get('label')}.vtt", 'wb') as f:
                                        f.write(s_r.content)
                                
                        else:
                            logging.warning(f"Track Request Error{s_r.text}")
                if args.subtitles and 'megaplay' not in args.source.lower():
                    continue
                download(r.json()['sources']['file'], "https://megaplay.buzz/", args.path, anime, title, number)
            except:
                print(format_exc()) 

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.debug(format_exc())