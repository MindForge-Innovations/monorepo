# ~~~ Imports ~~~
# import hydra
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


# @hydra.main(
#     config_path="../../configs",
#     config_name="experiment.yaml",
#     version_base="1.1",
# )
def main(cfg: DictConfig):
    logger.info(f"Configuration: {cfg}")
    # ~~~ DataLoaders ~~~
    train_dataloader = create_dataloader(
        cfg.dataset.data_dir,
        "train",
        cfg.dataset.batch_size,
        cfg.dataset.num_workers,
        cfg.dataset.shuffle,
    )

    val_dataloader = create_dataloader(
        cfg.dataset.data_dir,
        "val",
        cfg.dataset.batch_size,
        cfg.dataset.num_workers,
        not cfg.dataset.shuffle,
    )
    logger.info("DataLoaders créés.")

    # ~~~ Model Initialization ~~~
    model = FasterRCNNModule(cfg.model.weights)

    # ~~~ Logger ~~~
    mlf_logger = MLFlowLogger(
        experiment_name="lightning_logs", tracking_uri="file:./mlruns"
    )

    # ~~~ Training ~~~
    trainer = Trainer(
        limit_train_batches=100,
        max_epochs=1,
        logger=mlf_logger,
    )

    logger.info("Entraînement du modèle...")
    trainer.fit(model, train_dataloader, val_dataloader)
    logger.info("Entraînement terminé.")


if __name__ == "__main__":

    logger.info("Welcome to the object detection training script.")

    main()
