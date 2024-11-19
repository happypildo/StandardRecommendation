import glob
import zipfile
import os
import threading


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
        print("------------------------------------------")


