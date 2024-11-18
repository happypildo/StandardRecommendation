"""
In this project,

We aim to get 3GPP standard documents and to transform docs to pdf file.
"""
from selenium import webdriver                                  # 동적 사이트 수집
from webdriver_manager.chrome import ChromeDriverManager        # 크롬 드라이버 설치
from selenium.webdriver.chrome.service import Service           # 자동적 접근
from selenium.webdriver.chrome.options import Options           # 크롭 드라이버 옵션 지정
from selenium.webdriver.common.by import By                     # find_element 함수 쉽게 쓰기 위함

import requests

from convert_docs_to_pdf import Unzip


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 표준 사이트 입장
driver.get("https://portal.3gpp.org/Specifications.aspx?q=1&series=0&releases=all&draft=False&underCC=False&withACC=False&withBCC=False&numberNYA=False")

# 시리즈 별 요소 확인
drop_down_a = driver.find_element(By.ID, "dnn_ctr593_SpecificationsList_rpbSpecSearch_i0_rcbSeries_Arrow")
drop_down_a.click()
drop_down_div = driver.find_element(By.ID, "dnn_ctr593_SpecificationsList_rpbSpecSearch_i0_rcbSeries_DropDown")
labels = drop_down_div.find_elements(By.CSS_SELECTOR, "li > label")
series_dict = {}

for idx, label in enumerate(labels):
    print(label.text, "************************")
    series_num = int(label.text.split('.')[0])
    series_dict[series_num] = (idx, label.text)

# 나와 있는 series 행 별로 다운로드 진행
amount_of_standards = int(driver.find_element(By.CSS_SELECTOR, ".rgWrap.rgInfoPart").text.split()[0])
amount_of_hopping = int(driver.find_element(By.CSS_SELECTOR, ".rgWrap.rgInfoPart").text.split()[-1])

print("Downloading documents...")
print(f"   The amount of standards to download: {amount_of_standards} with hopping {amount_of_hopping}.")
web_cnt = 0
for i in range(0, amount_of_standards, amount_of_hopping):
    for offset in range(min(amount_of_hopping, amount_of_standards - web_cnt * amount_of_hopping)):
        row_of_standard = driver.find_element(By.ID, f'dnn_ctr593_SpecificationsList_rgSpecificationList_ctl00__{offset}')
        extracted_link = row_of_standard.find_element(By.ID, 'imgViewSpecifications').get_attribute('onclick')
        sub_link = extracted_link.split("'")[1]
        download_link = 'https://portal.3gpp.org' + sub_link

        driver.get(download_link)
        driver.find_element(By.CSS_SELECTOR, ".rtsLink.rtsAfter").click()

        try:
            elem = driver.find_element(By.ID, "SpecificationReleaseControl1_rpbReleases_i0_ctl00_specificationsVersionGrid_ctl00_ctl04_lnkFtpDownload")
            download_link = elem.get_attribute('href')

            print(f"\tTry to download from {download_link}...")

            file_name = download_link.split("/")[-1]

            try:
                response = requests.get(
                    url=download_link,
                    stream=True
                    )

                with open(file_name, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                print(f"\t\tFile was downloaded successfully")
            except requests.exceptions.RequestException as e:
                print(f"\t\t!!! Fail to download: {e} !!!")
        except:
            print(f"\t\t!!! There is no available standard. Try next standard... !!!")

        driver.back()

    web_cnt += 1
    driver.find_element(By.CLASS_NAME, "rgPageNext").click()

    print(f"\tNow...............[{web_cnt * amount_of_hopping}/{amount_of_standards}]")

print("")