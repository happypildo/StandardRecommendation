import glob
import zipfile
import os
import threading
import sys
import comtypes.client
import time


class Unzip:
    def __init__(self, target_directory=""):
        self.target_directory = target_directory
        self.unzip_directory = "unzip_" + target_directory

        self.threads = []

    def setter(self, target_dir):
        self.target_directory = target_dir
        self.unzip_directory = "unzip_" + target_dir

    def unzip_file(self):
        def unzipping(f):
            try:
                with zipfile.ZipFile(f, 'r') as zip_ref:
                    zip_ref.extractall(self.unzip_directory)
            except:
                pass

        self.threads = []

        if os.path.isdir(self.unzip_directory):
            print(f"Directory [{self.unzip_directory}] already exists.")
        else:
            os.mkdir(self.unzip_directory)
            zip_files = glob.glob(f"{self.target_directory}/*.zip")

            for file in zip_files:
                try:
                    thread = threading.Thread(target=unzipping,
                                              args=(file, ))
                    self.threads.append(thread)
                    thread.start()
                except zipfile.BadZipfile as e:
                    pass

            print("\n------------------------------------------")
            print(f"[~] Waiting for thread joining...")
            for thread in self.threads:
                thread.join()
            print(f"[✔] Successfully unzip all files")

            self.refine_files()

    def refine_files(self):
        print(f"[~] Trying to delete files w/o doc ex...")

        for filename in os.listdir(self.unzip_directory):
            file_path = os.path.join(self.unzip_directory, filename)

            if os.path.isfile(file_path):
                if not filename.endswith('.doc'):
                    os.remove(file_path)
                else:
                    pass

        print(f"[✔] Successfully refine all files")
        self.convert_to_pdf()

    def convert_to_pdf(self):
        print(f"[~] Trying to convert doc file to pdf file...")

        pdf_dir = "pdf_" + self.target_directory

        if os.path.isdir(pdf_dir):
            print(f"Directory [{pdf_dir}] already exists.")
        else:
            os.mkdir(pdf_dir)

            for filename in os.listdir(self.unzip_directory):
                file_path = os.path.abspath("./" + self.unzip_directory + "/" + filename)

                if os.path.isfile(file_path):
                    if filename.endswith('.doc'):
                        pdf_file_name = filename[:-4].replace(" ", "_")
                        pdf_file_name = pdf_file_name.replace(".", "_")

                        out_file_path = os.path.abspath("./" + pdf_dir + "/" + pdf_file_name)

                        word = comtypes.client.CreateObject('Word.Application')
                        time.sleep(3)
                        try:
                            doc = word.Documents.Open(file_path)
                        except:
                            pass
                        else:
                            time.sleep(3)

                            try:
                                doc.SaveAs(out_file_path, FileFormat=17)
                            except:
                                doc.Close()
                            else:
                                time.sleep(3)

                                doc.Close()
                                word.Quit()

        print(f"[✔] Successfully convert all files")
        print("------------------------------------------")
