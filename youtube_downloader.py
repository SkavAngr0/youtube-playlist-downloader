from pytubefix import YouTube

def download_video(url, save_path):
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        highest_res_stream = streams.get_highest_resolution()
        print(f"Downloading video: {yt.title}")
        highest_res_stream.download(output_path=save_path)
        print(f"Downloaded video: {yt.title}")
    except Exception as e:
        print(f"Error downloading video: {e}")
    
def download_audio(url, save_path):
    try:
        yt = YouTube(url)
        audio_streams = yt.streams.filter(only_audio=True, file_extension='mp3').first()
        print(f"Downloading audio: {yt.title}")
        audio_streams.download(output_path=save_path, file_name=f"{yt.title}.mp3")
        print(f"Downloaded audio: {yt.title}")
    except Exception as e:
        print(f"Error downloading audio: {e}")