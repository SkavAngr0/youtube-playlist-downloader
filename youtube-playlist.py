from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By                                            
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-features=OptimizationGuideModelDownloading")

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service)


# Playlist INPUT
#playlist = input("Enter your playlist: ")
        # https://www.youtube.com/playlist?list=PLLs_ak7laW3YVCPOlDQaOzt7Poi1kRDW8
        # https://www.youtube.com/playlist?list=PLLs_ak7laW3bquNeO56dtfyPOznImNCpe
playlist_url = ("https://www.youtube.com/playlist?list=PLLs_ak7laW3YVCPOlDQaOzt7Poi1kRDW8")
driver.get(playlist_url)

    # Playlist Informations
# Playlist NAME
playlist_name_elements = driver.find_element(By.XPATH, '//h1[@class="dynamic-text-view-model-wiz__h1"]')
playlist_name = playlist_name_elements.text
# Playlist CREATOR
creator_name_element = driver.find_element(By.XPATH, '//a[contains(@href, "/@")]')
creator_name = creator_name_element.text.strip()

# Playlist Video Informations
video_elements = driver.find_elements(By.XPATH, '//a[@id="video-title"]')



print(f"{playlist_name} {creator_name}.\nNumber of Videos: {len(video_elements)}")

video_url_list = []
for index, video in enumerate(video_elements, start=1):
    video_title = video.get_attribute("title")
    video_url = video.get_attribute("href")
    video_url_list.append(video_url)
    print(f"{index}/ {video_title}")

user_confirmation = input("Confirm download? press 'y' to proceed, or 'n' to cancel: ").strip().lower()

if user_confirmation == "y":
    print("\nDownload confirmed.")
else:
    print("\nDownload canceled.")

time.sleep(5)
driver.quit()