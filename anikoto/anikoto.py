
try:
    from curl_cffi import requests
    from curl_cffi import CurlMime
except ImportError:
    import requests
import argparse
# from pydoc import html
import sys
from traceback import format_exc
from langcodes import Language
import logging
import os
import datetime
import re
from bs4 import BeautifulSoup
import base64
import yt_dlp
import subprocess
from urllib.parse import urlparse
import m3u8

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

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


def clean_name(name):
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def download(url, referer, path, anime, title, number,args):
    anime = clean_name(anime)
    if not os.path.exists(f"{path}/{anime}"):
        os.makedirs(f"{path}/{anime}")
    logging.info(f"Downloading E{number} {title} from {url}")
    if os.path.exists(f"{path}/{anime}/{anime} E{number} {title}.mp4"):
        logging.info(f"File already exists: {path}/{anime}/{anime} E{number} {title}.mp4")
        return
    
    downloader = args.downloader
    if downloader == 'yt-dlp':
        ydl_opts = {
            # 'format': 'bv+ba',  
            'http_headers':  {
                    
                    
                    
                    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
                    
                    'accept': "*/*",
                    'origin': referer,
                    
                    'referer': referer,
                    
                    'priority': "u=1, i"
                },

            'external_downloader': 'aria2c', 
            'hls_prefer_native': {'m3u8': 'native', 'dash': 'native'},
            'concurrent_fragment_downloads':10,

            'paths': {
                'temp': 'temp',  
                'home': f'{path}/{anime}' 
            },
            'outtmpl': f'{anime} E{number} {title}.%(ext)s', 
            'generic':{
                'impersonate': 'Edge',
            },
            # 'cookiesfrombrowser': ('chrome'),
            # 'verbose':True,
            # 'debug_printtraffic':True,
            'socket_timeout':10,
            'nocheckcertificate': True,
            # 'encoding':'gzip, deflate, br, zstd',
        }
        if args.debug:
            ydl_opts['debug_printtraffic'] = True
            ydl_opts['verbose'] = True

        if args.quality:
            # ydl_opts['format'] = f'bv[height<=?{args.quality}]+ba'
            ydl_opts['format_sort'] = [f'res:{args.quality}']
        if args.debug:
            logging.debug(ydl_opts)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    elif downloader == 'ffmpeg':
        headers = (
            "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36\r\n"
            f"referer: {referer}\r\n"
            f'accept-language:en-US,en;q=0.9\r\n'
            'accept-encoding: gzip, deflate, br, zstd\r\n'
            "accept: */*\r\n"
   
            "sec-fetch-dest: empty\r\n"
            "sec-fetch-mode: cors\r\n"
            "sec-fetch-site: cross-site\r\n"
        )
        # print(headers)
        cmd = [
            "ffmpeg",
            '-extension_picky', '0',
            "-headers", headers,
            "-i", url,
            "-acodec", "copy",
            '-vcodec', 'copy',
            "-loglevel", "debug",
            "-y",
            f"{path}/{anime}/{anime} E{number} {title}.mp4"
        ]
        if args.debug:
            print(cmd)
        subprocess.run(cmd, check=True)
    
    else:
        command = [
            'N_m3u8DL-RE',url,
            "-H","user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36",
            "-H",f"referer: {referer}",
            "-H",f'accept-language:en-US,en;q=0.9',
            "-H",'accept-encoding: gzip, deflate, br, zstd',
            "-H","accept: */*",

            "-H","sec-fetch-dest: empty",
            "-H","sec-fetch-mode: cors",
            "-H","sec-fetch-site: cross-site",
            '--save-dir',f"{path}/{anime}",
            '--log-level', 'DEBUG',
            '--save-name', f"{anime} E{number} {title} ",
            '-M', 'format=mp4'
    ]
        if args.debug:
            print(command)
        subprocess.run(command)
        
def subtitles(response, session, args, anime, number, title):
    anime = clean_name(anime)
    if "tracks" in response:
        for track in response['tracks']:
            try:
                logging.info(f"Track Found: {track.get('label')} ({track.get('kind')})")
                if args.subtitle_lang.lower() in track.get('label').lower():
                    logging.info(f"Track: {track.get('label')} ({track.get('kind')})")
                    if track.get('file'):
                        logging.info(f"Track URL: {track.get('file')}")
                        label = track["label"]
                        language_name = label.split()[0]
                        code = Language.find(language_name).language
                        if not os.path.exists(f"{args.path}/{anime}/{anime} E{number} {title}.{code}.vtt"):
                            logging.info(f"Downloading subtitles for E{number} {title} {track.get('label')}")
                            s_r = session.get(track.get('file'),headers={
                                "referer": "https://megaplay.buzz/",
                            })
                            if s_r.status_code == 200:
                                logging.info(f"{args.path}/{anime}/{anime} E{number} {title}.{code}.vtt")
                                if not os.path.exists(f"{args.path}/{anime}/"):
                                    os.makedirs(f"{args.path}/{anime}/")
                                with open(f"{args.path}/{anime}/{anime} E{number} {title}.{code}.vtt", 'wb') as f:
                                    f.write(s_r.content)
            except:
                logging.info(format_exc())       
                    
            # else:
            #     logging.warning(f"Track Request Error{s_r.text}")

def main():
    services_availble = ['megaplay', 'vidstream', 'kiwi', 'vidcloud', 'vidplay']
    
    def source_type(value):    
        sources = value.split(",") if ',' in value else [value]
        invalid = set(sources) - set(services_availble)
        if invalid:
            raise argparse.ArgumentTypeError(
                f"Invalid source(s): {', '.join(invalid)}"
            )
        return sources
    
    def episode_type(value):
        if ',' in value:
            episode_ = value.split(",")
        else:
            episode_ = [value]
        return episode_
    
    version = "3.5.0"
    session = requests.Session()
    # session.verify = False
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    })
    parser = argparse.ArgumentParser(description="Anikoto (https://anikoto.tv/) Downloader", epilog="Example usage:\n python3 anikoto.py OPTIONS URL")
    parser.add_argument("--version","-v", action="version", version=f"%(prog)s {version}")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("url", help="Video Url like: https://anikoto.tv/watch/solo-leveling-ilh08/ep-1")
    parser.add_argument("--quality","-q", choices=['2160','1440',"1080", "720", "480",'360'],default="1080", help="Choose a Quality")
    parser.add_argument("--audio", "-a", choices=['sub', 'dub'], default='dub', help="Download Audio")
    parser.add_argument("--downloader", "-d", choices=['yt-dlp', 'N_m3u8DL-RE', 'ffmpeg'], default='yt-dlp', help="Downloader")
    parser.add_argument("--subtitles", "-ss", action="store_true",default=True, help="Download Subs")
    parser.add_argument("--list", action="store_true",default=False, help="List Episodes")
    parser.add_argument("--last", action="store_true",default=False, help="Only Download Last Episode")
    parser.add_argument("--subtitle-lang", "-sl",metavar="LANG",default="English",help="Subtitle language to download (matches track label, e.g. English, Spanish, Arabic)")
    parser.add_argument("--path", "-p", help="path to save the file", default=os.getcwd())
    parser.add_argument("--source", '-s', help=f"Comma-separated list of sources to download from {[s for s in services_availble]}",  type=source_type, default=services_availble)
    parser.add_argument("--episode", '-e', help=f"Comma-separated list of Episodes to download",  type=episode_type,)
    
    parser.add_argument("--range", "-r", help="Specify episode range (e.g. 1-5) if you want to download only episode 1129 use 1129-1129")


    args = parser.parse_args()
    if args.debug:
        logging.info("Selected Args"+str(args))
    r = session.get(args.url)

    parsed = urlparse(r.url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    if not args.source:
        args.source = services_availble

    search = re.search(rf'{domain}/anime/getinfo/(\d+)', r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    title_element = soup.find('h1', class_='title d-title')
    anime = title_element.get_text(strip=True)
    if not search:
        logging.error("Error: Unable to find the video ID in the provided URL.")
        exit(1)
    video_id = search.group(1)
    r = session.get(f"{domain}/ajax/episode/list/{video_id}?vrf=")
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
        print(f"Scrapping {i}  ", end="\r")
        episode_data.append({'title': title, 'data-ids': data_ids, 'data-mel': data_mal, 'data-timestamp': data_timestamp, 'number': i})
        i+=1
    del i

    for number, data in enumerate(episode_data, start=1):
        print(f"{number}: {data['title']}")
        if args.debug:
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
            logging.info(f"Downloading episodes {start} to {end}:")
            for number, data in enumerate(episode_data, start=start):
                print(f"{number}: {data['title']}")
        except Exception as e:
            logging.info(f"Invalid range format. Use like '1-5'. Error: {e}")
            exit(1)
    
    if args.episode:
        episode_data = [episode_data[int(number)-1] for number in args.episode]
        logging.info(f"Downloading episodes :")
        for number, data in enumerate(episode_data):
            print(f"{number}: {data['title']}")
             
      

    if args.list:
        logging.info("List of Episodes:")
        for data in episode_data:
            print(f"{data['number']}: {data['title']}")
        exit(0)

    if args.last:
        episode_data = episode_data[-1:]
        logging.info("Last Episode:")
        # if args.debug:
        for data in episode_data:       
            print(f"{data['number']}: {data['title']}")


        
 


    # if 'megaplay' in args.source.lower() or args.subtitles:

    for data in episode_data: 
        try:
            number = data['number']
            title = data['title']
            url = f"{domain}/ajax/server/list"
            querystring = {"servers":data['data-ids']}

            r = session.get(url, params=querystring)
            soup = BeautifulSoup(r.json()['result'], 'html.parser')

            servers = soup.find_all('div', class_='type')

            server_data = []
            for server in servers:
    
                server_type = server.get('data-type').upper() 
                server_item = server.find_all('li') 
                for li in server_item:
                    data_link_id = li.get('data-link-id')
                    server_data.append({'type': server_type, 'data-link-id': data_link_id, 'li': li.text})

            
            for data in server_data:
                if args.debug:
                    print()
                    print(f"type: {data['type']}")
                    print(f"data-link-id: {data['data-link-id']}")
                    print(f'server_item: {data['li']}')
                    print()

                if args.source:
                    source = data['li'].lower()
                    if '-' in source:
                        source = source.split('-')[0].strip()
                    if source not in args.source:
                        continue

                url = f"{domain}/ajax/server"
                
                querystring = {"get":data['data-link-id']}
                try:
                    r = session.get(url, params=querystring)
                except Exception as e:
                    print(format_exc())
                    continue

                url = r.json()['result']['url']
     
                main_r = session.get(url, headers={
                    "referer": f"{domain}/",
                })
                
   
                if 'vidplay' in args.source:
                    data_id = re.search(r'data-id="(\d+)"', main_r.text)
                    if data_id:
                        data_id = data_id.group(1)
                    sub_type = re.search(r"type:\s*'([^']+)'", main_r.text)
                    if sub_type:
                        sub_type = sub_type.group(1)
                   
                    if data_id and sub_type:
                        if args.debug:
                            print(f"data_id: {data_id}")
                            print(f"sub_type: {sub_type}")
                        url = f'https://vidtube.site/stream/getSourcesNew?id={data_id}&type={sub_type}&id={data_id}&type={sub_type}'
                        domain2 = 'https://vidtube.site'
                        res = session.get(url, headers={
                            "referer": f"{domain2}/",
                        })
                        if res.status_code == 200:
                            if args.debug:
                                print(res.json())
                            subtitles(res.json(), session, args, anime, number, title)
                            # looks like they have garbage in the m3u8
                            
                            manifest = res.json()['sources']['file']

                            resp = session.get(manifest, headers={
                                "referer": f"{domain2}/",
                            })
                            logging.info(f"Rewriting m3u8 manifest for E{number} {title} to remove garbage segments")
                            if args.debug:
                                print(resp.text)
                            master = m3u8.loads(resp.text)

                            variant = max(master.playlists, key=lambda p: p.stream_info.bandwidth)

                            if args.quality:
                                target = int(args.quality)
                                variant = next(
                                    (
                                        p for p in master.playlists
                                        if p.stream_info.resolution
                                        and p.stream_info.resolution[1] == target
                                    ),
                                    None,
                                )
                  
                                # variant = next((p for p in master.playlists if p.stream_info.resolution and p.stream_info.resolution[1] <= int(args.quality)), variant)
                                if args.debug:
                                    logging.info(variant)
                   
                            media_url = manifest.rsplit("/", 1)[0] + "/" + variant.uri
                            resp = session.get(media_url, headers={
                                "referer": f"{domain2}/",
                            })
                            media = m3u8.loads(resp.text)

                            # filtered = [s for s in media.segments if "mt.nekostream.site" not in s.uri]
                            filtered = []
                            for segment in media.segments:
                                if 'mt.nekostream.site' in segment.uri:
                                    key = bytes([105, 63, 76, 77, 84, 65, 120, 48, 81, 54, 44, 58, 125, 53, 48, 85, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # extracted from dev tool with js debugging
                                    iv = bytes([87, 48, 59, 50, 55, 84, 111, 97, 85, 112, 108, 95, 80, 37, 39, 99])
                                    network_string = segment.uri.split('/')[-1]
                                    normalized = network_string.replace('-', '+').replace('_', '/')
                                    missing_padding = len(normalized) % 4
                                    if missing_padding:
                                        normalized += '=' * (4 - missing_padding)
                                    ciphertext_bytes = base64.b64decode(normalized)
                                    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                                    decryptor = cipher.decryptor()
                                    decrypted_data = decryptor.update(ciphertext_bytes) + decryptor.finalize()
                                    unpadder = padding.PKCS7(128).unpadder()
                                    try:
                                        data = unpadder.update(decrypted_data) + unpadder.finalize()
                                        clean_url = data.decode('utf-8')
                                        logging.info(f"Decrypted URL: {clean_url}")
                                        segment.uri = clean_url
                                        filtered.append(segment)
                                    except ValueError as e:
                                        logging.error(f"Decryption/Unpadding error: {e}")
                                else:
                                    filtered.append(segment)

                            media.segments.clear()
                            media.segments.extend(filtered)
                            if args.debug:
                                logging.info(media.dumps())
                            try:
                                upload = requests.post(
                                    "https://tmpfiles.org/api/v1/upload",
                                    files={
                                        "file": ("clean.m3u8", media.dumps(), "application/vnd.apple.mpegurl")
                                    },
                                )
                                logging.info(f"Uploading tmp m3u8: {upload.json()}")
                            except Exception as e:
                                logging.error(f"Upload Error: {e}")
                                if args.debug:
                                    print(format_exc())
                                mime = CurlMime()
                                mime.addpart(
                                    name="file",
                                    filename="clean.m3u8",
                                    content_type="application/vnd.apple.mpegurl",
                                    # data=media.dumps().encode("utf-8"),
                                    data=media.dumps()
                                )
                                upload = requests.post(
                                    "https://tmpfiles.org/api/v1/upload",
                                    multipart=mime,
                                )

                    
                            try:
                                data = upload.json()
                                if args.debug:
                                    logging.info(f"Upload Response: {data}")
                                direct_url = data["data"]["url"].replace(
                                        "https://tmpfiles.org/",
                                        "https://tmpfiles.org/dl/",
                                    )
                                logging.info(f"Direct URL: {direct_url}")

                                if sub_type.lower() == args.audio.lower():
                                    download(direct_url, "https://vidtube.site/", args.path, anime, title, number, args, )
                            except:
                                logging.info("Upload Error")
                                
                                os.makedirs(f"{args.path}/{anime}/temp", exist_ok=True)
                                with open(f'{args.path}/{anime}/temp.m3u8', 'w+') as f:
                                    media.dump(f)
                                logging.info("Force N_M3U8-RE Upload")
                                args.downloader = 'N_m3u8DL-RE'
                                if sub_type.lower() == args.audio.lower():
                                    download(f"{args.path}/{anime}/temp.m3u8", "https://vidtube.site/", args.path, anime, title, number, args, )

                else:   
                    # MegaPlay
                    # if not args.source or 'megaplay' in args.source.lower():
                    id_ = re.search(r' data-id=\"(\d+)\"', main_r.text)
                    if id_:
                        id_ = id_.group(1)

                        r = session.get("https://megaplay.buzz/stream/getSources", params={"id":id_})
                        if args.debug:
                            print(r.text, file=sys.stderr)
    
                        if r.headers.get('Content-Type') == 'application/json':
                            if isinstance(r.json(), dict) and 'sources' in r.json():  
                                if args.debug:
                                    print(r.json()['sources']['file'])

                                subtitles(r.json(), session, args, anime, number, title)
                            
                                if data['type'].lower() == args.audio.lower():
                                    download(r.json()['sources']['file'], "https://megaplay.buzz/", args.path, anime, title, number, args, )

                # vidstream
                # if not args.source or 'vidstream' in args.source.lower():
                    id_2 = re.search(r' data-ep-id=\"(\d+)\"', main_r.text)

                    if id_2:
                        id_2 = id_2.group(1)
                        type_ = re.search(r"type: '(\w+)',", main_r.text)
                        if not type_:
                            raise Exception("Error: type not found")
                        type_ = type_.group(1)
                        domain2 = re.search(r"domain2_url: '(.+)',", main_r.text)
                        if not domain2:
                            raise Exception("Error: domain not found")
                        domain2 = domain2.group(1)
                        
                        response = session.get(f'{domain2}/save_data.php?id={id_2}-{type_}', headers={
                            'referer': domain
                        })

                        subtitles(response.json()['data'], session, args, anime, number, title)

                        if type_.lower() == args.audio.lower():
                                download(response.json()['data']['sources'][0]['url'],domain, args.path, anime, title, number, args, )
                
        except Exception as e:
            logging.error(f'ERROR:{e}')
            if args.debug:
                print(format_exc())


    if 'kiwi' in args.source:
        try:
            if 'kiwi' in args.source:
                for data in episode_data:
                    number = data['number']
                    # print(f'https://mapper.kotostream.online/api/mal/{data['data-mel']}/{number}/{data['data-timestamp']}')
                    # r = session.get(f"https://mapper.kotostream.online/api/mal/{data['data-mel']}/{number}/{data['data-timestamp']}", timeout=5, verify=False) # seems down 
                    logging.info(f"Trying to get stream URL for E{number} {data['title']} from Kiwi Stream")
                    logging.info(f"Request URL: https://mapper.nekostream.site/api/mal/{data['data-mel']}/{number}/{data['data-timestamp']}")
                    r = session.get(f"https://mapper.nekostream.site/api/mal/{data['data-mel']}/{number}/{data['data-timestamp']}", headers={
                        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
                        'referer': domain,
                        'origin': domain,   

                    })
                    if r.status_code == 200:
                        for stream in r.json():
                            if "Stream" in stream and args.quality in stream:
                                # print(stream)
                                if args.debug:
                                    print(r.json())
                                server_code = r.json()[stream][args.audio]['url']
                                url = f"{domain}/ajax/server"
                                querystring = {"get":server_code}
                                r = session.get(url, params=querystring)
                                url = r.json()['result']['url']
                                if "#" in url:
                                    url = base64.b64decode(url.split("#")[1]).decode('utf-8')
                                    # download(url, f"{domain}/", args.path,anime, data['title'], number, args,)
                                    download(url, f"https://kwik.cx2.mewcdn.online", args.path,anime, data['title'], number, args,)
                    

                    
        except Exception as e:
            logging.error(f'ERROR:{e}')
            if args.debug:
                print(format_exc())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.debug(format_exc())