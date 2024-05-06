import json
import boto3
import logging
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import os
from config import Config
from tqdm import tqdm
from label_studio_sdk import Client as LSClient
import zipfile

load_dotenv()

def setup_directory():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
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
        lsClient = LSClient(config.lsUrl, config.lsToken, make_request_raise=True)
        lsClient.check_connection()
    except Exception as e:
        logging.error(e)
        return 1
    
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
            return 1
        
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
        images = s3.Bucket(config.lsSourceBucket)
    except ClientError as e:
        logging.error(e)
        return 1

    # objects = list(images.objects.all())
    # for obj in objects:
    #     print(obj.key)
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
            return 1

if __name__ == "__main__":
    main()
 