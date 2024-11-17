from selenium.webdriver.common.by import By

def get_playlist_info(driver, playlist_url):
    driver.get(playlist_url)
    playlist_name = driver.find_element(By.XPATH, '//h1[@class="dynamic-text-view-model-wiz__h1"]').text
    creator_name = driver.find_element(By.XPATH, '//a[contains(@href, "/@")]').text.strip()
    video_elements = driver.find_elements(By.XPATH, '//a[@id="video-title"]')
    
    url_list = []
    for video in video_elements:
        url = video.get_attribute("href")
        url_list.append(url)
    
    return playlist_name, creator_name, url_list