from dotenv import load_dotenv
import rootutils

rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from src.dataloader.downloader import download_titles_and_content

load_dotenv()

download_titles_and_content()

