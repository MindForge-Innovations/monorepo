# ~~~ Imports ~~~
from dataclasses import dataclass
from omegaconf import DictConfig

from lightning.pytorch import Trainer
from lightning.pytorch.loggers import MLFlowLogger
import colorlog
import logging
import rootutils

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
from src.lightning_modules.object_detector import FasterRCNNModule
from src.utils.dataloader import create_dataloader

# ~~~ Configuration du logger ~~~
handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
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
logger.setLevel(logging.DEBUG)


# ~~~ Configuration ~~~
@dataclass
class Config:
    data_dir: str = (
        "/home/olivier/projet/pi/monorepo/doc-analyser/model-experiment/data"
    )
    batch_size: int = 4
    num_workers: int = 4
    shuffle: bool = True
    weights: str = "FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT"
    dataset_files = ("CRH.yaml", "fasterRCNN_v2.yaml")
    experiment_name: str = "doc-analyzer-v1.0"
    logger_uri: str = "file:./mlruns"
    max_epochs: int = 5


def main(config: Config):
    logger.info(f"Configuration: {config}")
    # ~~~ DataLoaders ~~~
    train_dataloader = create_dataloader(
        config.data_dir,
        "train",
        config.batch_size,
        config.num_workers,
        config.shuffle,
    )

    val_dataloader = create_dataloader(
        config.data_dir,
        "test",
        config.batch_size,
        config.num_workers,
        not config.shuffle,
    )

    logger.info("DataLoaders créés.")

    # ~~~ Model Initialization ~~~
    model = FasterRCNNModule(config.weights)

    # ~~~ Logger ~~~
    mlf_logger = MLFlowLogger(
        experiment_name=config.experiment_name, tracking_uri=config.logger_uri
    )

    # ~~~ Training ~~~
    trainer = Trainer(
        limit_train_batches=100,
        max_epochs=config.max_epochs,
        logger=mlf_logger,
    )

    logger.info("Entraînement du modèle...")
    trainer.fit(model, train_dataloader, val_dataloader)
    logger.info("Entraînement terminé.")


if __name__ == "__main__":

    logger.info("Welcome to the object detection training script.")
    config = Config()
    main(config)
