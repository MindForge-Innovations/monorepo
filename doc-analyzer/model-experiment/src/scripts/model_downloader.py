from mlflow import MlflowClient
import mlflow
import logging
from pprint import pprint
import os

logging.basicConfig(level=logging.INFO)

client = MlflowClient()

model_name = "document-classifier"
versions = client.get_registered_model(model_name).latest_versions
logging.info(f"Downloading {len(versions)} versions of model {model_name}")
pprint(versions)
logging.debug(versions)

for version in versions:
    model_uri = f"models:/{model_name}/{version.version}"
    local_path = f"/models/{model_name}-v{version.version}"
    if not os.path.exists(local_path):
        mlflow.artifacts.download_artifacts(artifact_uri=model_uri, dst_path=local_path)
        logging.info(f"Downloaded model version {version.version} to {local_path}")
    else:
        logging.info(f"Model version {version.version} already exists at {local_path}")

