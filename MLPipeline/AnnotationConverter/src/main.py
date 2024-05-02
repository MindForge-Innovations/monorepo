import boto3
import logging
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from botocore.session import Session
import os
from config import Config
from tqdm import tqdm
from label_studio_converter import Converter

load_dotenv()

def setup_directory():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        filename="logs/main.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if not os.path.exists("data"):
        os.makedirs("data")

def main():

    config = Config()

    setup_directory()

    try:
        config.load_from_env()
    except Exception as e:
        logging.error(e)
        return 1
    
    try:
        s3 = boto3.resource("s3")
    except ClientError as e:
        logging.error(e)
        return 1

    try:
        annotations = s3.Bucket(config.lsTargetBucket)
    except ClientError as e:
        logging.error(e)
        return 1
    
    nb_downloaded = 0
    for obj in tqdm(annotations.objects.all()):
        # save the object to the data directory
        if not os.path.exists(f"data/{obj.key}.json"):
            annotations.download_file(obj.key, f"data/{obj.key}.json")
            nb_downloaded += 1
    logging.info(f"Downloaded {nb_downloaded} files from {config.lsTargetBucket}")

    converter_json = Converter("ls-label-config.xml", "")
    converter_json.convert_to_json("data/", "tmp/json")

    converter_coco = Converter("ls-label-config.xml", "")
    converter_coco.convert_to_coco("tmp/json/", "tmp/coco")

if __name__ == "__main__":
    main()
 