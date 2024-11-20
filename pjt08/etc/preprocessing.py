# 데이터 소스 경로
import json
import os

import fitz
import re


# def load_json_files_and_merge(base_directory):
#     all_data = []
#     # 디렉토리 내의 모든 JSON 파일 순회
#     for filename in os.listdir(base_directory):
#         if filename.endswith('.json'):
#             file_path = os.path.join(base_directory, filename)

#             # JSON 파일 읽기
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 data = json.load(f)

#                 if 'SJML' in data and 'text' in data['SJML']:
#                     for text_item in data['SJML']['text']:
#                         all_data.append(text_item)

#             # 데이터 리스트에 추가
#             all_data.append(data)

#     return all_data


def extractContentsFromTR(base_directory):
    all_data = []
    for filename in os.listdir(base_directory):
        if filename.endswith('.pdf'):
            temp_dict = {}

            file_path = os.path.join(base_directory, filename)

            pdf_doc = fitz.open(file_path)

            during_contents = False
            title = ""
            processed_contents = []
            scope_content = ""
            for i, page in enumerate(pdf_doc):
                # 페이지 내용은 "\nContents"로 시작해 "\nForeword" 전까지이다.
                # print(page.get_text())
                if i == 0:
                    for item in page.get_text().split('\n'):
                        if "38" in item:
                            title = item
                            break

                if "\nContents" in page.get_text():
                    during_contents = True
                if "\nContents" not in page.get_text() and "\nForeword" in page.get_text():
                    during_contents = False
                if during_contents:
                    # 내용 추출
                    lines = page.get_text().split('\n')
                    start = 0
                    for line in lines:
                        if 'Foreword' in line:
                            break
                        start += 1
                    contents = lines[start::2]
                    processed = contents[:]
                    for idx in range(len(processed)):
                        try:
                            last_idx = processed[idx].index('.')
                            processed[idx] = processed[idx][0:last_idx]
                        except:
                            break

                    processed_contents.extend(processed)

                if (not during_contents) and ("\n1 \nScope" in page.get_text()):
                    text = page.get_text()
                    start_idx = text.index('\nScope')
                    scope_content = text[start_idx:].replace('\n', " ")


            print(title)
            print(processed_contents)
            print(scope_content)

            temp_dict = {
                'title': title,
                'contents': processed_contents[:],
                'scope': scope_content
            }

            all_data.append(temp_dict)

    return all_data


if __name__ == "__main__":
    base_directory = '/home/ssafy/pjt08/chatbot_data'

    # 데이터 로드 및 병합 (이 부분을 크롤링으로 대체해도 좋습니다)
    # merged_data_list = load_json_files_and_merge(base_directory)
    merged_data_list = extractContentsFromTR(base_directory)

    print(len(merged_data_list))
    print(merged_data_list[0])