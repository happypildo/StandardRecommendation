import json
import os

import fitz
import re

import glob


class Extractor:
    def __init__(self, target_path):
        self.extracted_data = []
        self.target_path = target_path

    def extract_content_from_pdf(self):
        pdf_files = glob.glob(f"{self.target_path}/*.pdf")

        for filename in pdf_files:
            file_path = os.path.abspath(f"./{filename}")

            pdf = fitz.open(file_path)

            first_page = pdf.load_page(0)

            try:
                content = first_page.get_text()
                content = content.replace("\n", "")
                content = content.replace(";", " ")
                content = content.split("Technical Specification Group Radio Access Network")

                standard_title = content[0][:content[0].index("(")]
                study_area = content[1][:content[1].index("(Release")]

                release_s = content[1].index("(Release")
                release_e = content[1].index("The present document")
                release = content[1][release_s + 1:release_e]

                standard_title = standard_title.strip()
                study_area = study_area.strip()
                release = release.strip()[:-1]

                print("-"*10)
                print("Title: ", standard_title)
                print("Area: ", study_area)
                print("Release: ", release)

                # 목차 정보 추추
                all_indices = []
                page_num = 2
                while True:
                    pattern = r"(?<=\n)[\w\s]+(?=\.{5,})"
                    matches = re.findall(pattern, pdf.load_page(page_num).get_text())

                    if len(matches) == 0:
                        break

                    all_indices.extend(matches)
                    page_num += 1

                start_idx = 0
                for match in all_indices:
                    if 'Abbreviations' in match:
                        break
                    start_idx += 1
                all_indices = all_indices[start_idx+1:]

                processed_indices = []
                for idx, match in enumerate(all_indices):
                    spl_match = match.split("\n")
                    for spl in spl_match:
                        temp = spl.strip()
                        if temp.isdigit():
                            pass
                        else:
                            processed_indices.append(temp)

                print("Indices: ", ", ".join(processed_indices))

                # Scope 정보 가져오기
                while True:
                    if "\nScope \n" in pdf.load_page(page_num).get_text():
                        break
                    page_num += 1
                scope_page_text = pdf.load_page(page_num).get_text()
                s = scope_page_text.index("\nScope \n")
                e = scope_page_text.index("\nReferences \n")
                scope_page_text = scope_page_text[s:e]
                scope_page_text = scope_page_text.replace("\n", " ").strip()
                print("Scope: ", scope_page_text)

                print()

                temp_dict = {
                    'title': standard_title,
                    'area': study_area,
                    'release': release,
                    'scope': scope_page_text,
                    'index': ", ".join(processed_indices)
                }
                self.extracted_data.append(temp_dict)
            except:
                pass
