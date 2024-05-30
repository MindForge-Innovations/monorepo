
Echec des premières tentatives de charger le modèle depuis MLFlow :
---
```
Downloading artifacts:   0%|                                                                                                                                                                  | 0/1 [01:03<?, ?it/s]
Traceback (most recent call last):
  File "/Users/jeff/Dev/MSE_Projects/PI/monorepo/doc-analyzer/model-experiment/src/scripts/test.py", line 33, in <module>
    model = load_model(1)
            ^^^^^^^^^^^^^
  File "/Users/jeff/Dev/MSE_Projects/PI/monorepo/doc-analyzer/model-experiment/src/scripts/test.py", line 27, in load_model
    model = mlflow.pytorch.load_model(model_uri)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jeff/Dev/MSE_Projects/PI/monorepo/doc-analyzer/model-experiment/.venv/lib/python3.12/site-packages/mlflow/pytorch/__init__.py", line 682, in load_model
    local_model_path = _download_artifact_from_uri(artifact_uri=model_uri, output_path=dst_path)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jeff/Dev/MSE_Projects/PI/monorepo/doc-analyzer/model-experiment/.venv/lib/python3.12/site-packages/mlflow/tracking/artifact_utils.py", line 111, in _download_artifact_from_uri
    return repo.download_artifacts(
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jeff/Dev/MSE_Projects/PI/monorepo/doc-analyzer/model-experiment/.venv/lib/python3.12/site-packages/mlflow/store/artifact/models_artifact_repo.py", line 190, in download_artifacts
    model_path = self.repo.download_artifacts(artifact_path, dst_path)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jeff/Dev/MSE_Projects/PI/monorepo/doc-analyzer/model-experiment/.venv/lib/python3.12/site-packages/mlflow/store/artifact/artifact_repo.py", line 274, in download_artifacts
    raise MlflowException(
mlflow.exceptions.MlflowException: The following failures occurred while downloading one or more artifacts from https://br2-mlflow.kube.isc.heia-fr.ch/api/2.0/mlflow-artifacts/artifacts/0/1734c35a7ba2480f8df5a73d480e57da/artifacts/model:
##### File  #####
API request to https://br2-mlflow.kube.isc.heia-fr.ch/api/2.0/mlflow-artifacts/artifacts/0/1734c35a7ba2480f8df5a73d480e57da/artifacts/model/ failed with exception HTTPSConnectionPool(host='br2-mlflow.kube.isc.heia-fr.ch', port=443): Max retries exceeded with url: /api/2.0/mlflow-artifacts/artifacts/0/1734c35a7ba2480f8df5a73d480e57da/artifacts/model/ (Caused by ResponseError('too many 500 error responses'))
```