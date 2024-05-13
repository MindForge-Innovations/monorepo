import lightning as L
import mlflow
from mlflow.models import infer_signature
import torch
import numpy as np


class MLFlowModelRegistryCallback(L.Callback):
    def __init__(self, model_name, artifact_path="model"):
        """
        Args:
        - model_name: The name of the model in the MLFlow registry.
        - artifact_path: Path to the model artifact within the run's artifacts.
        """
        self.model_name = model_name
        self.artifact_path = artifact_path

    def on_train_end(self, trainer, pl_module):
        run_id = trainer.logger.run_id

        # ~~~ Model signature ~~~
        example_input = torch.randn(1, 3, 224, 224, device=pl_module.device)
        example_output = np.array(pl_module.model(example_input))

        signature = infer_signature(example_input.cpu().numpy(), example_output)

        # ~~~ PyTorch model logging ~~~
        with mlflow.start_run(run_id=run_id):
            mlflow.pytorch.log_model(
                pl_module.model, "model", signature=signature
            )

        model_uri = f"runs:/{run_id}/model"
        client = mlflow.tracking.MlflowClient()

        # ~~~ Model registration ~~~
        try:
            model_version_info = client.create_model_version(
                self.model_name, model_uri, run_id
            )
            print(
                f"Model {self.model_name} version {model_version_info.version} created in MLFlow Model Registry."
            )
        except mlflow.exceptions.RestException as e:
            if "RESOURCE_ALREADY_EXISTS" in str(e):
                # If the model already exists, just log this fact
                print(
                    f"Model {self.model_name} already exists. Creating a new version."
                )
                model_version_info = client.create_model_version(
                    self.model_name, model_uri, run_id
                )
                print(
                    f"New version {model_version_info.version} of model {self.model_name} registered."
                )
            else:
                # If there is another kind of error, raise it
                raise e
