import os

class Config:

    def load_from_env(self):
        self.lsTargetBucket = os.getenv("LS_TARGET_BUCKET")
        self.lsSourceBucket = os.getenv("LS_SOURCE_BUCKET")
        self.datasetBucket = os.getenv("DATASET_BUCKET")

        with open(os.getenv("LS_TOKEN_PATH"), "r") as f:
            self.lsToken = f.read().strip()

        self.lsUrl = os.getenv("LS_URL")
        self.lsProjectId = os.getenv("LS_PROJECT_ID")
        
        if self.lsTargetBucket is None or self.lsSourceBucket is None or self.datasetBucket is None:
            raise Exception("Missing environment variables")