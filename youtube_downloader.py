from pytubefix import YouTube
from pytubefix.cli import on_progress
import subprocess
import os

def get_safe_title(title: str) -> str:
    """Removes special characters from title to use as a filename."""
    return "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()

def download_video(url, save_path):
    """Downloads a YouTube video in the highest available resolution and merges audio using ffmpeg."""
    try:
        yt = YouTube(url, use_po_token=True, on_progress_callback=on_progress)
        safe_title = get_safe_title(yt.title)

        # Select best video stream — prefer avc1 (H.264) for compatibility
        video_stream = (
            yt.streams.filter(adaptive=True, only_video=True)
            .filter(lambda s: "avc1" in s.codecs[0])
            .order_by('resolution')
            .first()
        )

        # Fallback to any available stream if avc1 not found
        if not video_stream:
            video_stream = (
                yt.streams.filter(adaptive=True, only_video=True)
                .order_by('resolution')
                .last()
            )
        
        # Select best audio stream
        audio_stream = (
            yt.streams.filter(adaptive=True, only_audio=True)
            .order_by('abr')
            .last()
        )

        # Define temp and output file paths
        video_path = os.path.join(save_path, f"{safe_title}_video.mp4")
        audio_path = os.path.join(save_path, f"{safe_title}_audio.mp4")
        output_path = os.path.join(save_path, f"{safe_title}.mp4")

        print(f"Downloading: {yt.title} [{video_stream.resolution} | {video_stream.codecs[0]}]")
        video_stream.download(output_path=save_path, filename=f"{safe_title}_video.mp4")
        audio_stream.download(output_path=save_path, filename=f"{safe_title}_audio.mp4")
    
        # Merge video and audio using ffmpeg
        print(f"Merging:     {yt.title} ")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            output_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
        # Remove temp files after merging
        os.remove(video_path)
        os.remove(audio_path)

        print(f"✓ Done:      {yt.title}\n")

    except Exception as e:
        print(f"✗ Error downloading video: {e}\n")
    
def download_audio(url, save_path):
    try:
        yt = YouTube(url, use_po_token=True, on_progress_callback=on_progress)
        safe_title = get_safe_title(yt.title)

        # Select best audio stream
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').last()


        print(f"Downloading: {yt.title}")
        audio_stream.download(output_path=save_path, filename=f"{safe_title}.mp3")
        print(f"✓ Done:      {yt.title}\n")

    except Exception as e:
        print(f"✗ Error downloading audio: {e}\n")