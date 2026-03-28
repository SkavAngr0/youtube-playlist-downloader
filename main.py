from webdriver_setup import setup_webdriver
from playlist_scraper import get_playlist_info
from youtube_downloader import download_video, download_audio
from folder_selector import choose_directory

def print_header():
    print("\n" + "=" * 50)
    print("       YouTube Playlist Downloader")
    print("=" * 50)


def display_playlist_summary(playlist_name: str, creator_name: str, url_list: list) -> None:
    """Prints playlist details and video list."""
    print(f"\n  Playlist : {playlist_name}")
    print(f"  Creator  : {creator_name}")
    print(f"  Videos   : {len(url_list)}")
    print("\n" + "-" * 50)
    print("  Videos in playlist:")
    print("-" * 50)
    for index, url in enumerate(url_list, start=1):
        print(f"  {index:>3}. {url}")
    print("-" * 50)

def get_download_choice() -> str:
    """Prompts user to choose between video or audio download."""
    print("\n  [V] Download as MP4 (video)")
    print("  [A] Download as MP3 (audio)")
    return input("\n  Enter your choice: ").strip().lower()

def main():
    print_header()

    playlist_url = input("\n  Enter playlist URL: ").strip()

    print("\n  Select a folder to save downloads...")
    save_path = choose_directory()
    if not save_path:
        print("\n  [!] No folder selected. Exiting.")
        return

    print("\n  Fetching playlist info...\n")
    driver = setup_webdriver()

    try:
        playlist_name, creator_name, url_list = get_playlist_info(driver, playlist_url)
        display_playlist_summary(playlist_name, creator_name, url_list)

        confirm = input("\n  Confirm download? [y/n]: ").strip().lower()
        if confirm != "y":
            print("\n  Download cancelled. Exiting.")
            return

        choice = get_download_choice()
        if choice not in ('v', 'a'):
            print("\n  [!] Invalid choice. Exiting.")
            return
        
        print("\n" + "=" * 50)
        print("  Starting downloads...")
        print("=" * 50 + "\n")

        for video_url in url_list:
            if choice == 'v':
                download_video(video_url, save_path)
            elif choice == 'a':
                download_audio(video_url, save_path)

        print("=" * 50)
        print("  All downloads complete!")
        print("=" * 50 + "\n")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()