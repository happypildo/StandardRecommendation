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

import requests
import os
import threading

from convert_docs_to_pdf import Unzip
from extract_information import Extractor

import openai
import psycopg2
import numpy as np
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

conn = psycopg2.connect(
    dbname='backend',
    user='ssafy',
    password='1234',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(input=text, model=model)
    return response['data'][0]['embedding']

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
options.add_argument('headless')

# target_series = int(input("Enter the series number to analysis: "))
for target_series in range(0, 56):
    temp_cnt = 0
    print("Current target series: ", target_series)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                            options=options)

    # 표준 사이트 입장
    driver.get("https://portal.3gpp.org/Specifications.aspx?q=1&series=0&releases=all&draft=False&underCC=False&withACC=False&withBCC=False&numberNYA=False")

    # 시리즈 별 요소 확인
    drop_down_a = driver.find_element(By.ID, "dnn_ctr593_SpecificationsList_rpbSpecSearch_i0_rcbSeries_Arrow")
    drop_down_a.click()
    drop_down_div = driver.find_element(By.ID, "dnn_ctr593_SpecificationsList_rpbSpecSearch_i0_rcbSeries_DropDown")
    labels = drop_down_div.find_elements(By.CSS_SELECTOR, "ul > li > label")
    series_dict = {}

    for idx, label in enumerate(labels):
        WebDriverWait(driver, 10).until(lambda driver: label.text.strip() != "")
        series_num = int(labels[idx].text.split('.')[0])

        cursor.execute(
            f"INSERT INTO series (series_number, series_title) VALUES ({series_num}, '{labels[idx].text.split('.')[1]}') ON CONFLICT (series_number) DO NOTHING;"
        )
        conn.commit()
    
        series_dict[series_num] = (idx, label.text)
        
    # 쓰레드 기반 다운로드
    threads = []

    # 압축 해제 요청
    unzip_class = Unzip()

    # 여기 수정해야 함 -> 원하는 시리즈로 갈 수 있게. -> Dropdown 요소 가져와서 click으로 처리함
    if series_dict.get(target_series, None) is None:
        print(f"There is no series with number {target_series}")
    else:
        idx, target_series_title = series_dict[target_series]

        print(f"Extraction process will be started... ------------------- target series: [{target_series_title}]")

        # target_series_title이 이미 존재하는지부터 확인.
        target_series_title = target_series_title.replace(" ", "_")
        target_series_title = target_series_title.replace(".", "_")
        unzip_class.setter(target_series_title)
        if os.path.isdir(target_series_title):
            print("The selected standard is already processed.")
        else:
            try:
                os.mkdir(target_series_title)

                # 해당 표준 사이트로 이동.
                # + TR 문서만 가져올 수 있도록 추가 수정
                labels[idx].click()
                drop_down_a.click()
                TR_btn = driver.find_element(By.ID, "dnn_ctr593_SpecificationsList_rpbSpecSearch_i0_cbTechnicalReport")
                TR_btn.click()

                btn_search = driver.find_element(By.ID, "dnn_ctr593_SpecificationsList_rpbSpecSearch_i0_btnSearch")
                btn_search.click()
                original_window = driver.current_window_handle

                _ = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, f'dnn_ctr593_SpecificationsList_rgSpecificationList_ctl00__0'))
                )

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

                        # 새 창에서 작업
                        driver.execute_script(f"window.open('{download_link}')")
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.find_element(By.CSS_SELECTOR, ".rtsLink.rtsAfter").click()

                        try:
                            elem = driver.find_element(By.ID, "SpecificationReleaseControl1_rpbReleases_i0_ctl00_specificationsVersionGrid_ctl00_ctl04_lnkFtpDownload")
                            download_link = elem.get_attribute('href')

                            print(f"\t\t[→] Preparing to download from {download_link}...")

                            file_name = download_link.split("/")[-1]

                            thread = threading.Thread(target=file_download_with_thread,
                                                    args=(download_link, target_series_title, file_name))
                            threads.append(thread)
                            thread.start()
                        except:
                            print(f"\t\t|---[!] No available standard found, skipping...")

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                        temp_cnt += 1
                        if temp_cnt > 5:
                            break
                    web_cnt += 1
                    driver.find_element(By.CLASS_NAME, "rgPageNext").click()
                    original_window = driver.current_window_handle

                    print(f"\tNow...............[{web_cnt * amount_of_hopping}/{amount_of_standards}]")
                    if temp_cnt > 5:
                            break
            except:
                pass
            print("")

    for thread in threads:
        thread.join()

    print("[✔] All downloads completed. Unzipping will be started...")

    unzip_class.setter(target_series_title)
    unzip_class.unzip_file()
    pdf_file_dir = "pdf_" + unzip_class.target_directory

    print("Good")
    pdf_extractor = Extractor(target_path=pdf_file_dir)
    extracted_data = pdf_extractor.extract_content_from_pdf()

    # 임베딩 후 데이터베이스에 삽입...
    print("Insert to table...")
    print(extracted_data)
    # for data in extracted_data:
    #     print(data)
    #     content = f"제목: {data['title']}\n\n문서 영역: {data['area']}\n\n목차 정보: {data['indices']}\n\n문서가 다루는 내용: {data['scope']}"

    #     embedding = get_embedding(content)
    #     embedding_arr = np.array(embedding).tolist()

    #     cursor.execute(
    #         f"INSERT INTO series_detail (series_id, title, area, indices, scope, content, embedding) VALUES ({target_series}, '{data['title']}', '{data['area']}', '{data['indices']}', '{data['scope']}', '{content}', '{embedding_arr}');"
    #     )
    #     conn.commit()
    for data in extracted_data:
        print(data)
        content = f"제목: {data['title']}\n\n문서 영역: {data['area']}\n\n목차 정보: {data['indices']}\n\n문서가 다루는 내용: {data['scope']}"

        embedding = get_embedding(content)
        embedding_arr = np.array(embedding).tolist()

        query = "SELECT id FROM series WHERE series_number = %s;"
        cursor.execute(query, (target_series,))

        # 결과 가져오기
        result = cursor.fetchone()  # 하나의 행만 가져옴
        if result:
            series_id = result[0]
            print(f"Series ID: {series_id}")

            query = """
            INSERT INTO series_detail (series_id, title, area, indices, scope, content, embedding) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            data_to_insert = (
                series_id,
                data['title'],
                data['area'],
                data['indices'],
                data['scope'],
                content,
                str(embedding_arr)  # embedding 배열을 문자열로 변환
            )
            cursor.execute(query, data_to_insert)
            conn.commit()    
        else:
            print(f"No entry found for series_number = {target_series}")