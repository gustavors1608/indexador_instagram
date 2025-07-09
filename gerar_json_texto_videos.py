import os
import json
import whisper
from moviepy.editor import VideoFileClip
from tqdm import tqdm

VIDEOS_DIR = "videos"
SAIDA_JSON = "transcricoes.json"
INSTAGRAM_BASE_URL = "https://www.instagram.com"

def encontrar_videos(base_path):
    videos = []
    for shortcode in os.listdir(base_path):
        pasta_video = os.path.join(base_path, shortcode)
        if not os.path.isdir(pasta_video):
            continue

        arquivos_mp4 = [f for f in os.listdir(pasta_video) if f.endswith('.mp4')]
        if not arquivos_mp4:
            continue  # Ignora se não há vídeo

        for nome_arquivo in arquivos_mp4:
            caminho = os.path.join(pasta_video, nome_arquivo)
            url = f"{INSTAGRAM_BASE_URL}/p/{shortcode}/"
            videos.append((url, caminho))

    return videos


def extrair_audio(video_path, audio_temp_path="temp_audio.wav"):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_temp_path, logger=None)
    return audio_temp_path

def transcrever_audio(audio_path, model):
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1024:
        raise FileNotFoundError(f"Arquivo de áudio inválido ou vazio: {audio_path}")
    result = model.transcribe(audio_path, fp16=False)
    return result["text"].strip()


def main():
    print("[🔎] Buscando vídeos...")
    video_list = encontrar_videos(VIDEOS_DIR)

    if not video_list:
        print("[✖] Nenhum vídeo encontrado.")
        return

    model = whisper.load_model("small")  # Ou "small", "medium", "large" se quiser mais precisão

    transcricoes = {}
    for url, video_path in tqdm(video_list, desc="Transcrevendo vídeos"):

            audio_path = extrair_audio(video_path)
            texto = transcrever_audio(audio_path, model)
            transcricoes[url] = texto
            print(texto)
            os.remove(audio_path)  # Limpa o arquivo de áudio temporário

    with open(SAIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(transcricoes, f, ensure_ascii=False, indent=2)

    print(f"[✔] Transcrições salvas em: {SAIDA_JSON}")

if __name__ == "__main__":
    main()
