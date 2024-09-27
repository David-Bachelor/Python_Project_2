import logging
import shutil
from datetime import datetime
import os

BASE_PATH = r"Logging filepath"

def setup_logging(base_path):
    
    now = datetime.now()
    folder_name = now.strftime("%m%Y")
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    log_file_name = now.strftime("%d%m.log")
    log_file_path = os.path.join(folder_path, log_file_name)
    logging.basicConfig(
        filename=log_file_path,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.debug("Logging setup complete.")

setup_logging(BASE_PATH)

def Archive_old_Files():
    for i in os.listdir("Filepath\\Fees"):
        if i != "Archive":
            shutil.move("Filepath\\Fees\\" + i, "Filepath\\Fees\\Archive\\" + i)
        else: 
            continue
Archive_old_Files()

def Upload_To_Enfusion():
    shutil.copy(r'Filepath\Expenses_For_Loading.xlsx', r'Destination Path')

Upload_To_Enfusion()
logging.info("Process complete")