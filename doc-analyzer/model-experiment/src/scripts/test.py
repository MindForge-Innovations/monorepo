import mlflow
from mlflow import MlflowClient
import torch
from pprint import pprint
import requests
import os

def print_model_info(rm):
    print("--")
    print(f"name: {rm.name}")
    print(f"tags: {rm.tags}")
    print(f"description: {rm.description}")

experiment_id = mlflow.get_experiment_by_name("doc-classifier-v1.0").experiment_id
with mlflow.start_run(experiment_id=experiment_id) as run:
    pprint(dict(run.info), indent=4)
        

# # Créez un client MLFlow
# client = MlflowClient()
# name = "document-classifier"
# tag = {'framework': 'pytorch'}
# dsc = "Document classifier"

# client.create_registered_model(name=name, tags=tag, description=dsc)


# model = client.get_registered_model(name)
# print_model_info(model)

# for rm in client.search_registered_models():
#     pprint(dict(rm), indent=4)

# model_name = "document_classifier"
# model_versions = client.get_registered_model(model_name).latest_versions

# # Afficher les informations sur chaque version
# for version in model_versions:
#     print(f"Version: {version.version}")
#     print(f"Run ID: {version.run_id}")
#     print(f"Status: {version.current_stage}")
#     print(f"Creation Timestamp: {version.creation_timestamp}")
#     print(f"Last Updated Timestamp: {version.last_updated_timestamp}")
#     print("-" * 30)


# def load_model(version):

#     model_uri = f"models:/document_classifier/{version}"
#     model = mlflow.pytorch.load_model(model_uri)
#     model.eval()
#     print(f'Model version {version} loaded')

#     return model

# model = load_model(1)