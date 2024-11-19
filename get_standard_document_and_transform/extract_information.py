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
                print(standard_title)
                print(study_area)
                print(release)

                # Extract Indicies...
                pattern = r"(?<=\n)[\w\s]+(?=\.{5,})"
                matches = re.findall(pattern, pdf.load_page(2).get_text())

                print()

            except:
                pass

    def extract_information_from_tr(self, pdf):
        pass

    def extract_information_from_ts(self, pdf):
        pass
