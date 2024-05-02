import os

class Config:

    def load_from_env(self):
        self.lsTargetBucket = os.getenv("LS_TARGET_BUCKET")
        self.lsSourceBucket = os.getenv("LS_SOURCE_BUCKET")
        self.datasetBucket = os.getenv("DATASET_BUCKET")

        if self.lsTargetBucket is None or self.lsSourceBucket is None or self.datasetBucket is None:
            raise Exception("Missing environment variables")