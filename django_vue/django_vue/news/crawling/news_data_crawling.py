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

import time


class Crawler:
    def __init__(self):
        options = Options()
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('headless')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                options=options)
        self.driver.set_page_load_timeout(30)  

        self.home_link = "https://www.3gpp.org/news-events/3gpp-news"      

    def crawl_data(self):
        self.driver.get(self.home_link)

        try:
            deny_btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".cc-btn.cc-deny"))
                )
            deny_btn.click()
        except:
            print("There is no cookie component. Keep going...")

        WebDriverWait(self.driver, 10).until(lambda driver: driver.find_element(By.XPATH, '//*[@id="sp-component"]/div/div[6]/div[2]/p').text.strip() != "")
        len_elem = self.driver.find_element(By.XPATH, '//*[@id="sp-component"]/div/div[6]/div[2]/p')
        maximum_length = int(len_elem.text.split(' ')[-1])
        page_cnt = 0

        while True:
            news_components = self.driver.find_elements(By.CLASS_NAME, "com-content-custom-blog__item")
            for news_component in news_components:
                try:
                    a_elem = news_component.find_element(By.CSS_SELECTOR, "div > div > a")
                    link = a_elem.get_attribute("href")

                    self.driver.execute_script(f"window.open('{link}')")
                    self.driver.switch_to.window(self.driver.window_handles[-1])

                    # 스크롤할 대상 찾기 (페이지 전체나 특정 div)
                    scrollable_element = self.driver.find_element(By.TAG_NAME, "body")  # 페이지 전체 스크롤

                    # ActionChains로 스크롤 시뮬레이션
                    for _ in range(10):  # 10번 스크롤
                        ActionChains(self.driver).scroll_by_amount(0, 300).perform()  # 300픽셀씩 스크롤
                        time.sleep(0.5)  # 스크롤 후 로딩 대기

                    # 제목 가져오기
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, ".customHeader > h2")
                    title = title_elem.text

                    # 날짜 가져오기
                    date_elem = self.driver.find_element(By.CSS_SELECTOR, ".customHeader .header_date")
                    date = date_elem.text

                    contents = []
                    if page_cnt == 0:
                        parent = self.driver.find_element(By.XPATH, '//*[@id="column-id-1649676445471"]/div')
                    else:
                        try:
                            parent = self.driver.find_element(By.XPATH, '//*[@id="sp-component"]/div/div[2]/div[3]/div/div[1]/div')
                        except:
                            parent = self.driver.find_element(By.XPATH, '//*[@id="sp-component"]/div/div[2]/div[4]/div/div[1]/div')

                    children = parent.find_elements(By.XPATH, './*')
                    if len(children) == 0:
                        continue
                    for child in children:
                        contents.append(child.text)

                    # 데이터를 yield로 반환
                    yield {
                        "title": title,
                        "date": date,
                        "contents": " ".join(contents)
                    }
                except Exception as e:
                    print(f"Error while processing: {e}")
                finally:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

            if page_cnt >= maximum_length - 1:
                break

            next_elem = self.driver.find_element(By.XPATH, '//*[@id="sp-component"]/div/div[6]/div[2]/div/ul/li[26]/a')
            href = next_elem.get_attribute('href')
            self.driver.get(href)
            page_cnt += 1

