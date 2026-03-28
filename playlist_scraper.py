from selenium.webdriver.common.by import By
import time

def get_playlist_info(driver, playlist_url):
    driver.get(playlist_url)
    time.sleep(3)

    playlist_name = driver.find_element(By.XPATH, '//h1[@class="dynamicTextViewModelH1"]').text
    creator_name = driver.find_element(By.XPATH, '//a[contains(@href, "/@")]').text.strip()
    video_elements = driver.find_elements(By.XPATH, '//a[@id="video-title"]')
    
    videos = []
    for video in video_elements:
        url = video.get_attribute("href")
        title = video.get_attribute("title")
        if url and title:
            videos.append({"title": title, "url": url})
    
    return playlist_name, creator_name, videos