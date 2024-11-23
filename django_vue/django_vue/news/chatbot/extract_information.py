import json
import os

import fitz
import re

import glob

from pprint import pprint
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class Extractor:
    def __init__(self, target_path):
        self.extracted_data = []
        self.target_path = target_path
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def query_openai(self, prompt):
        # response = openai.ChatCompletion.create(
        #     model='gpt-4o-mini',
        #     messages=[
        #         {'role': "system", 'content': "당신은 PDF 내용으로부터 사용자가 원하는 정보를 추출하는 챗봇입니다."},
        #         {'role': "system", 'content': "PDF 문서의 텍스트 정보가 입력으로 들어갈 것인데, 굉장히 난해한 형태를 보이고 있습니다. 잘 추출하여 사용자가 만족할 수 있도록 하세요."},
        #         {'role': "system", 'content': "텍스트에서 가져와야 할 정보는, 1) 문서의 제목 2) 문서의 study area 3) 문서의 목차 정보 4) 문서 내에 포함된 'scope' 내용입니다."},
        #         {'role': "system", 'content': "각 정보의 예시는 다음과 같습니다. 1) 문서의 제목: 'TR 38.716 V16.0.0, 2) 문서의 study area: 'Technial Specification Group Radio Access Networks'."},
        #         {"role": "user", 'content': prompt}
        #     ]
        # )
        messages=[
            {'role': "system", 'content': "당신은 PDF 내용으로부터 사용자가 원하는 정보를 추출하는 챗봇입니다."},
            {'role': "system", 'content': "PDF 문서의 텍스트 정보가 입력으로 들어갈 것인데, 굉장히 난해한 형태를 보이고 있습니다. 잘 추출하여 사용자가 만족할 수 있도록 하세요."},
            {'role': "system", 'content': "텍스트에서 가져와야 할 정보는, 1) 문서의 제목 2) 문서의 study area 3) 문서의 목차 정보 4) 문서 내에 포함된 'scope' 내용입니다."},
            {'role': "system", 'content': "각 정보의 예시는 다음과 같습니다. 1) 문서의 제목: 'TR 38.716 V16.0.0, 2) 문서의 study area: 'Technial Specification Group Radio Access Networks'."},
            {"role": "user", 'content': prompt}
        ]
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

        return response['choices'][0]['message']['content']

    def extract_content_from_pdf(self):
        pdf_files = glob.glob(f"{self.target_path}/*.pdf")

        for filename in pdf_files:
            file_path = os.path.abspath(f"./{filename}")

            pdf = fitz.open(file_path)
            all_text = ""
            for page_num in range(len(pdf)):
                page = pdf[page_num]  # 현재 페이지 가져오기
                text = page.get_text()  # 페이지에서 텍스트 추출
                all_text += text  # 텍스트를 누적
                all_text += "\n"  # 페이지 구분을 위해 줄바꿈 추가
            
            pdf.close()
            try:
                sp_text = all_text.split("\n")
                title = sp_text[0]
                
                area_s = all_text.index('Technical Report')
                area_e = all_text.index('The present document has been developed within the 3rd Generation Partnership Project')
                area = all_text[area_s:area_e]
                print(title, area)

                pattern = r"(?<=\n)[\w\s]+(?=\.{5,})"
                matches = re.findall(pattern, all_text)

                start_idx = 0
                for match in matches:
                    if 'Abbreviations' in match:
                        break
                    start_idx += 1
                all_indices = matches[start_idx+1:]

                processed_indices = []
                for idx, match in enumerate(all_indices):
                    spl_match = match.split("\n")
                    for spl in spl_match:
                        temp = spl.strip()
                        if temp.isdigit():
                            pass
                        else:
                            processed_indices.append(temp)
                print()
                print(set(processed_indices))
                print()

                self.extracted_data.append({
                    "title": title,
                    "area": area,
                    "indices": ", ".join(processed_indices),
                    "scope": "" 
                })
                pprint(self.extracted_data[-1])
            except Exception as e:
                print(e)
                pass

            # first_page = pdf.load_page(0)

            # try:
            #     content = first_page.get_text()
            #     content = content.replace("\n", "")
            #     content = content.replace(";", " ")
            #     content = content.split("Technical Specification Group Radio Access Network")

            #     standard_title = content[0][:content[0].index("(")]
            #     # print("Title: ", standard_title)
            #     study_area = content[1][:content[1].index("(Release")]
            #     # print("Area: ", study_area)

            #     release_s = content[1].index("(Release")
            #     release_e = content[1].index("The present document")
            #     release = content[1][release_s + 1:release_e]
            #     # print("Release: ", release)

            #     standard_title = standard_title.strip()
            #     study_area = study_area.strip()
            #     release = release.strip()[:-1]
            #     # 목차 정보 추추
            #     all_indices = []
            #     page_num = 2
            #     while True:
            #         pattern = r"(?<=\n)[\w\s]+(?=\.{5,})"
            #         matches = re.findall(pattern, pdf.load_page(page_num).get_text())

            #         if len(matches) == 0:
            #             break

            #         all_indices.extend(matches)
            #         page_num += 1

            #     start_idx = 0
            #     for match in all_indices:
            #         if 'Abbreviations' in match:
            #             break
            #         start_idx += 1
            #     all_indices = all_indices[start_idx+1:]

            #     processed_indices = []
            #     for idx, match in enumerate(all_indices):
            #         spl_match = match.split("\n")
            #         for spl in spl_match:
            #             temp = spl.strip()
            #             if temp.isdigit():
            #                 pass
            #             else:
            #                 processed_indices.append(temp)
            #     # print(processed_indices)
            #     # Scope 정보 가져오기
            #     while True:
            #         if "\nScope \n" in pdf.load_page(page_num).get_text():
            #             break
            #         page_num += 1
            #     scope_page_text = pdf.load_page(page_num).get_text()
            #     s = scope_page_text.index("\nScope \n")
            #     e = scope_page_text.index("\nReferences \n")
            #     scope_page_text = scope_page_text[s:e]
            #     scope_page_text = scope_page_text.replace("\n", " ").strip()
            #     # print(scope_page_text)
            #     self.extracted_data.append({
            #         "title": standard_title,
            #         "area": study_area,
            #         "indices": ", ".join(processed_indices),
            #         "scope": scope_page_text 
            #     })
            #     pprint(self.extracted_data[-1])
            # except Exception as e:
            #     print("Error occured: ", e)
            #     pass
        
        return self.extracted_data
