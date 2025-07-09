import time
import sys
from instaloader import Instaloader, Profile, Post, ConnectionException, LoginRequiredException

# Configurações
SESSIONFILE = 'C:/Users/usina/AppData/Local/Instaloader/session-gustavo_testes_soft'
IG_USERNAME = 'gustavo_testes_soft'
TARGET_PROFILE = 'guilherme_vazan'  # <== Substitua pelo perfil desejado

def setup_instaloader():
    loader = Instaloader(
        download_pictures=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True
    )
    try:
        loader.load_session_from_file(IG_USERNAME, SESSIONFILE)
        print(f"[✔] Sessão iniciada como '{IG_USERNAME}'")
    except (ConnectionException, FileNotFoundError) as e:
        print(f"[✖] Falha na autenticação: {e}")
        sys.exit(1)
    return loader

def is_video_post(post: Post) -> bool:
    return (
        post.typename == 'GraphVideo' or
        (post.typename == 'GraphSidecar' and any(n.is_video for n in post.get_sidecar_nodes()))
    )

def coletar_videos(loader, perfil_usuario):
    try:
        profile = Profile.from_username(loader.context, perfil_usuario)
        print(f"[→] Acessando perfil: {perfil_usuario}")
        
        video_urls = []
        for post in profile.get_posts():
            time.sleep(5)
            if is_video_post(post):
                shortcode = post.shortcode
                if post.typename == 'GraphVideo':
                    url = f"https://www.instagram.com/p/{shortcode}/"
                else:  # Pode ser vídeo em carrossel
                    url = f"https://www.instagram.com/p/{shortcode}/"
                video_urls.append(url)

        print(f"[✔] {len(video_urls)} vídeos encontrados.")
        return video_urls

    except LoginRequiredException:
        print("[✖] Sessão expirada ou perfil privado.")
        return []
    except Exception as e:
        print(f"[✖] Erro inesperado: {e}")
        return []

def main():
    loader = setup_instaloader()
    urls = coletar_videos(loader, TARGET_PROFILE)
    print("\nLista de vídeos:")
    for u in urls:
        print(u)

if __name__ == '__main__':
    main()
