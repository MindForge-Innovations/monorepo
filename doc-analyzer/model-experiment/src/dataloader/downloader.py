import json
import boto3
import logging
from botocore.exceptions import ClientError
import os
from tqdm import tqdm
from label_studio_sdk import Client as LSClient
import zipfile

from src.dataloader.config import Config

def setup_directory():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    if not os.path.exists("data"):
        os.makedirs("data")
        

def setup_downloader():

    config = Config()

    setup_directory()

    try:
        config.load_from_env()
    except Exception as e:
        logging.error(e)
        exit(1)
    
    try:
        s3Client = boto3.resource("s3")
    except ClientError as e:
        logging.error(e)
        exit(1)
    
    try:
        lsClient = LSClient(config.lsUrl, config.lsToken, make_request_raise=True)
        lsClient.check_connection()
    except Exception as e:
        logging.error(e)
        exit(1)

    return s3Client, lsClient, config


def download_coco():
    s3Client, lsClient, config = setup_downloader()
    if not os.path.exists('data/coco_annotations.json'):
        try:
            zip_response = lsClient.make_request("GET", f"api/projects/{config.lsProjectId}/export?exportType=COCO")
            logging.info(f"Downloaded COCO file from {config.lsUrl}")

            with open('data/out.zip', 'wb') as f:
                f.write(zip_response.content)
                with zipfile.ZipFile('data/out.zip', 'r') as zip_ref:
                    zip_ref.extractall('data/')

            with open('data/result.json', 'r') as f:
                result = json.load(f)

            for img in result['images']:
                img['file_name'] = img['file_name'].replace('s3://mse-pi-lstudio-source/', '')
            
            with open('data/coco_annotations.json', 'w') as f:
                json.dump(result, f)
                
            os.remove('data/out.zip')
            os.remove('data/result.json')
            os.rmdir('data/images')

        except Exception as e:
            logging.error(e)
            exit(1)
        
    else:
        logging.info("COCO file already exists")
    
    with open('data/coco_annotations.json', 'r') as f:
        coco_annotations = json.load(f)

    for img in coco_annotations['images']:
        img['file_name'] = img['file_name'].replace('s3://mse-pi-lstudio-source/', '')

    s3_files_endpoints = [ann['file_name'] for ann in coco_annotations['images']]
    s3_files_endpoints_set = set(s3_files_endpoints)

    logging.info(f"Found {len(s3_files_endpoints_set)} files in COCO annotations")
    if len(s3_files_endpoints) != len(s3_files_endpoints_set):
        logging.warning(f"Found {len(s3_files_endpoints)} files in COCO annotations, {len(s3_files_endpoints_set)} unique files")

    try:
        images = s3Client.Bucket(config.lsSourceBucket)
    except ClientError as e:
        logging.error(e)
        exit(1)
    
    nb_downloaded = 0
    for obj in tqdm(s3_files_endpoints_set):
        # save the object to the data directory preserving the directory structure
        if not os.path.exists(f"data/{obj}"):
            os.makedirs(f"data/{os.path.dirname(obj)}", exist_ok=True)
            images.download_file(obj, f"data/{obj}")
            nb_downloaded += 1
    logging.info(f"Downloaded {nb_downloaded} files from {config.lsSourceBucket}")

    for obj in s3_files_endpoints_set:
        if not os.path.exists(f"data/{obj}"):
            logging.error(f"Failed to download {obj}")

def download_titles_and_content():
    s3Client, _, config = setup_downloader()

    books = ["Grotius-DG", "Puf-DNG", "Vattel-DG"]
    categories = ["page_with_content", "page_with_title"]

    try:
        images = s3Client.Bucket(config.lsSourceBucket)
    except ClientError as e:
        logging.error(e)
        exit(1)

    for book in books:
        if not os.path.exists(f"data/{book}"):
            os.makedirs(f"data/{book}")
        for category in categories:
            if not os.path.exists(f"data/{book}/{category}"):
                os.makedirs(f"data/{book}/{category}")
            # get the list of objects in the bucket
            objects = images.objects.filter(Prefix=f"{book}/{category}")
            logging.info(f"Downloading {len(objects)} files from {config.lsSourceBucket}")
            for obj in tqdm(objects):
                # save the object to the data directory preserving the directory structure
                images.download_file(obj.key, f"data/{obj.key}")


        