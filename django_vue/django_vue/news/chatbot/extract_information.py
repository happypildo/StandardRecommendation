import json
import os

import fitz
import re

import glob

from pprint import pprint


class Extractor:
    def __init__(self, target_path):
        self.extracted_data = []
        self.target_path = target_path

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
        
        return self.extracted_data
