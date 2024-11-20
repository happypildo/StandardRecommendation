"""
In this project,

We aim to get 3GPP standard documents and to transform docs to pdf file.
"""
from selenium import webdriver                                  # 동적 사이트 수집
from webdriver_manager.chrome import ChromeDriverManager        # 크롬 드라이버 설치
from selenium.webdriver.chrome.service import Service           # 자동적 접근
from selenium.webdriver.chrome.options import Options           # 크롭 드라이버 옵션 지정
from selenium.webdriver.common.by import By                     # find_element 함수 쉽게 쓰기 위함
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import requests
import os
import threading
import time

from convert_docs_to_pdf import Unzip
from extract_information import Extractor


def file_download_with_thread(download_link, path, file_name):
    try:
        response = requests.get(url=download_link, stream=True)

        with open(path + "/" + file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"\t\t|---[✔] Successfully downloaded: {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"\t\t|---[✘] Failed to download {file_name}: {e}")


options = Options()
# options.add_argument('headless')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          options=options)

# 뉴스 사이트 입장
driver.get("https://www.3gpp.org/news-events/3gpp-news")

# 쿠키 설정 거절 버튼
try:
    deny_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".cc-btn.cc-deny"))
        )
    deny_btn.click()
except:
    print("There is no cookie component. Keep going...")

# len_elem = driver.find_element(By.XPATH, '//*[@id="sp-component"]/div/div[6]/div[2]/p')
# len_elem = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, '//*[@id="sp-component"]/div/div[6]/div[2]/p'))
#         )
WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, '//*[@id="sp-component"]/div/div[6]/div[2]/p').text.strip() != "")
len_elem = driver.find_element(By.XPATH, '//*[@id="sp-component"]/div/div[6]/div[2]/p')
maximum_length = int(len_elem.text.split(' ')[-1])
page_cnt = 0
while True:
    news_components = driver.find_elements(By.CLASS_NAME, "com-content-custom-blog__item")

    for news_component in news_components:
        try:
            a_elem = news_component.find_element(By.CSS_SELECTOR, "div > div > a")
            link = a_elem.get_attribute("href")

            driver.execute_script(f"window.open('{link}')")
            driver.switch_to.window(driver.window_handles[-1])

            # 제목 가져오기
            title_elem = driver.find_element(By.CSS_SELECTOR, ".customHeader > h2")
            title = title_elem.text

            # 날짜 가져오기
            date_elem = driver.find_element(By.CSS_SELECTOR, ".customHeader .header_date")
            date = date_elem.text

            # 본문 내용 가져오기
            content_elem = driver.find_element(By.CSS_SELECTOR, "div.sppb-addon.sppb-addon-text-block")
            p_tags = content_elem.find_elements(By.TAG_NAME, "p")
            contents = []
            for p in p_tags:
                WebDriverWait(p, 10).until(lambda p: p.text.strip() != "")
                contents.append(p.text)
            contents = " ".join(contents)

            print("-" * 10)
            print(f"Title: {title}")
            print(f"Date: {date}")
            print(f"Contents: {contents}")
            print()

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass


    if page_cnt >= maximum_length - 1:
        break

    next_elem = driver.find_element(By.XPATH, '//*[@id="sp-component"]/div/div[6]/div[2]/div/ul/li[26]/a')
    href = next_elem.get_attribute('href')
    driver.get(href)
    page_cnt += 1
    print(page_cnt)
