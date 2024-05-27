import os


class TrainConfig:

    def __init__(self):
        self.data_dir = os.getenv("DATA_DIR")
        self.batch_size = 16
        self.num_workers = 4
        self.shuffle = True
        self.experiment_name = os.getenv("EXPERIMENT_NAME")
        self.max_epochs = 5
        self.limit_train_batches = 100

        if self.data_dir is None or self.experiment_name is None :
            raise Exception("Missing environment variables")

class MLFlowUri:

    def __init__(self):

        if os.getenv("MLFLOW_TRACKING_URI") is None or os.getenv("MLFLOW_USER") is None or os.getenv("MLFLOW_PASSWORD") is None:
            raise Exception("Missing environment variables")

        base_logger_uri = os.getenv("MLFLOW_TRACKING_URI")
        basic_auth = os.getenv("MLFLOW_USER") + ":" + os.getenv("MLFLOW_PASSWORD")
        self.logger_uri = f"http://{basic_auth}@{base_logger_uri}"