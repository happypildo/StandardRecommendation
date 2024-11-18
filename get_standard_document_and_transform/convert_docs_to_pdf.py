import glob
import zipfile
import os


class Unzip:
    def __init__(self, target_directory):
        self.target_directory = target_directory

    def unzip_file(self):
        zip_files = glob.glob(f"{self.target_directory}/*.zip")

        print(zip_files)


# zip_files =
#
# zip_file_path = "path_to_your_zip_file.zip"
# extract_to_path = "path_to_extract"
#
# # 디렉토리가 없는 경우 생성
# os.makedirs(extract_to_path, exist_ok=True)
#
# # ZIP 파일 열기 및 압축 해제
# try:
#     with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
#         zip_ref.extractall(extract_to_path)
#         print(f"ZIP 파일이 '{extract_to_path}'에 성공적으로 풀렸습니다!")
# except zipfile.BadZipFile:
#     print("ZIP 파일이 손상되었거나 유효하지 않습니다.")
