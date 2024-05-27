from dotenv import load_dotenv
import rootutils

rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from src.dataloader.downloader import download_titles_and_content

load_dotenv()

books = ["Grotius-DG", "Puf-DNG", "Vattel-DG"]
categories = ["page_with_content", "page_with_title"]

download_titles_and_content(books, categories)
