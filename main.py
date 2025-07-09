import os
import re
import sys
import json
import requests
from instaloader import Instaloader, Post, Profile, ConnectionException, BadResponseException, LoginRequiredException

# Configurações fixas
SESSIONFILE = 'C:/Users/usina/AppData/Local/Instaloader/session-gustavo_testes_soft'
IG_USERNAME = 'gustavo_testes_soft'
JSON_FILE = 'urls.json'
OUTPUT_DIR = 'videos'

def get_shortcode(url):
    match = re.search(r'/([A-Za-z0-9_-]{10,})/?$', url)
    return match.group(1) if match else None

def setup_instaloader():
    loader = Instaloader(
        download_pictures=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        post_metadata_txt_pattern='',
        quiet=True
    )
    try:
        loader.load_session_from_file(IG_USERNAME, SESSIONFILE)
        print(f"[✔] Sessão carregada com sucesso para: {IG_USERNAME}")
    except (ConnectionException, FileNotFoundError) as e:
        print(f"[✖] Falha ao carregar sessão: {e}")
        sys.exit(1)
    return loader

def carregar_urls(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return [item['url'] for item in dados if 'url' in item]
    except Exception as e:
        print(f"[✖] Erro ao ler o arquivo JSON: {e}")
        sys.exit(1)

def download_video(loader, url):
    shortcode = get_shortcode(url)
    if not shortcode:
        print(f"[!] URL inválida: {url}")
        return

    post_dir = os.path.join(OUTPUT_DIR, shortcode)
    os.makedirs(post_dir, exist_ok=True)

    try:
        post = Post.from_shortcode(loader.context, shortcode)

        if post.typename not in ["GraphVideo", "GraphSidecar"]:
            print(f"[!] Post não contém vídeo: {shortcode}")
            return

        if post.typename == "GraphSidecar":
            videos = [r.video_url for r in post.get_sidecar_nodes() if r.is_video]
        else:
            videos = [post.video_url]

        for idx, video_url in enumerate(videos):
            filename = f"video{'' if len(videos) == 1 else f'_{idx+1}'}.mp4"
            filepath = os.path.join(post_dir, filename)

            if os.path.exists(filepath):
                print(f"[✔] Já baixado: {filepath}")
                continue

            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(video_url, headers=headers, stream=True)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"[↓] Vídeo salvo: {filepath}")
            else:
                print(f"[✖] Erro ao baixar vídeo {shortcode}: HTTP {r.status_code}")
    except (LoginRequiredException, BadResponseException) as e:
        print(f"[✖] Erro ao acessar o post {shortcode}: {e}")
    except Exception as e:
        print(f"[✖] Erro inesperado com {shortcode}: {e}")

def main():
    loader = setup_instaloader()
    urls = carregar_urls(JSON_FILE)
    print(f"[→] {len(urls)} URLs carregadas do JSON.")
    for url in urls:
        download_video(loader, url)

if __name__ == '__main__':
    main()
