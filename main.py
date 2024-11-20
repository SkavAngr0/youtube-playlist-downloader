from webdriver_setup import setup_webdriver
from playlist_scraper import get_playlist_info
from youtube_downloader import download_video, download_audio
from folder_selector import choose_directory

def main():
    playlist_url = input("Enter the playlist URL: ").strip()
    
    save_path = choose_directory()
    if not save_path:
        print("No folder selected.")
        return

    driver = setup_webdriver()

    try:
        playlist_name, creator_name, url_list = get_playlist_info(driver, playlist_url)
        print(f"\nPlaylist: {playlist_name} {creator_name}")
        print(f"Total videos: {len(url_list)}\n")

        print("Videos in the playlist:")
        for index, video_url in enumerate(url_list, start=1):
            print(f"{index}/ {url_list}\n")

        confirm_download = input("\nConfirm download? Enter 'y' to continue, 'n' to cancel: ").strip().lower()
        if confirm_download != "y":
            print("Download cancelled.")
            return

        choice = input("Enter 'v' to download videos.mp4 or 'a' to download audio.mp3: ").strip()

        for video in url_list:
            if choice == 'v':
                download_video(video_url, save_path)
            elif choice == 'a':
                download_audio(video_url, save_path)
            else:
                print("Invalid choice. Skipping download.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()