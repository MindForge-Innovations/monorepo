from lightning.pytorch import Trainer
import torch
from lightning.pytorch.loggers import MLFlowLogger
import colorlog
import logging
import rootutils
import mlflow
from mlflow.models import infer_signature
from mlflow import MlflowClient
from mlflow.store.artifact.runs_artifact_repo import RunsArtifactRepository

# ~~~ Project imports ~~~
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

# ------------------------------------------------------------------------------------ #
# the setup_root above is equivalent to:
# - adding project root dir to PYTHONPATH
#       (so you don't need to force user to install project as a package)
#       (necessary before importing any local modules e.g. `from src import utils`)
# - setting up PROJECT_ROOT environment variable
#       (which is used as a base for paths in "configs/paths/default.yaml")
#       (this way all filepaths are the same no matter where you run the code)
# - loading environment variables from ".env" in root dir
# more info: https://github.com/ashleve/rootutils
# ------------------------------------------------------------------------------------ #
from src.models.classification import DocumentClassifier
from src.dataloader.classification import ClassificationDataModule
from src.scripts.trainConfig import TrainConfig, MLFlowUri

# ~~~ Configuration du logger ~~~
handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s[%(filename)s]",
    datefmt=None,
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={},
    style="%",
)
handler.setFormatter(formatter)
logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
# logger = logging.getLogger("mlflow")
logger.setLevel(logging.DEBUG)



def main(config: TrainConfig, mlflow_uri: MLFlowUri):
    logger.info(f"Configuration: {config}")
    logger.info(f"MLFlow URI: {mlflow_uri}")
    logger.info(f"Experiment name: {config.experiment_name}")
    
    # ~~~ Logger ~~~
    mlf_logger = MLFlowLogger(
        experiment_name=config.experiment_name,
        tracking_uri=mlflow_uri.logger_uri,
        log_model=True,
    )

    run_id = mlf_logger.run_id
    mlf_logger.log_hyperparams(config.__dict__)
    logger.info(f"Active run : {run_id}")
    if run_id is None:
        raise Exception("No active run found")
    # ~~~ Data Preparation ~~~
    data_module = ClassificationDataModule(
        config.data_dir, config.batch_size, config.num_workers, config.shuffle
    )

    data_module.set_logger(logger)
    data_module.set_mlflow_logger(mlf_logger)

    data_module.setup()
    logger.info("Data chargée avec succès")

    # ~~~ Model Initialization ~~~
    model = DocumentClassifier()

    # ~~~ Training ~~~
    trainer = Trainer(
        limit_train_batches=config.limit_train_batches,
        max_epochs=config.max_epochs,
        logger=mlf_logger,
        enable_progress_bar=False
    )

    logger.info("Entraînement du modèle...")
    trainer.fit(
        model,
        train_dataloaders=data_module,
    )
    logger.info("Entraînement terminé.")
    
    mlflow.set_experiment(config.experiment_name)
    experiment_id = mlflow.get_experiment_by_name(config.experiment_name).experiment_id
    logger.info(f"Experiment ID: {experiment_id}")

    mlflow.pytorch.log_model(model, artifact_path="document-classifier")
    scripted_pytorch_model = torch.jit.script(model)
    mlflow.pytorch.log_model(scripted_pytorch_model, "document-classifier-scripted")

    client: MlflowClient = mlf_logger.experiment
    desc = "Document classification model"
    runs_uri = f"runs:/{run_id}/document-classifier-scripted"
    model_src = RunsArtifactRepository.get_underlying_uri(runs_uri)
    mv = client.create_model_version("document-classifier", model_src, run_id, description=desc)
    logger.info(f"Model registered: id={mv.run_id}, version={mv.version}")

if __name__ == "__main__":

    logger.info("Welcome to the object detection training script.")
    try:
        config = TrainConfig()
        mlflow_uri = MLFlowUri()
        main(config, mlflow_uri)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
