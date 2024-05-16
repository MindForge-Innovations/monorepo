import lightning as L

from torch.utils.data import DataLoader, random_split
from src.utils.dataloader import collate_fn
from src.utils.dataset import CustomCocoDetection
from src.utils.transforms import get_basic_transform
from torchvision import datasets


class GrotiusDataModule(L.LightningDataModule):
    def __init__(self, data_dir, batch_size, num_workers=4, shuffle=True):
        super().__init__()
        self.name = "GrotiusDataModule"
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.shuffle = shuffle
        self.dataset_train = None
        self.dataset_val = None
        self.dataset_test = None

    def setup(self, stage=None):
        """Setup data loaders.

        Stage can be {fit,validate,test,predict}
        """

        #  ~~~ Load Dataset ~~~
        dataset = CustomCocoDetection(
            f"{self.data_dir}/images",
            f"{self.data_dir}/result.json",
            transforms=get_basic_transform(),
        )
        dataset = datasets.wrap_dataset_for_transforms_v2(
            dataset, target_keys=["boxes", "labels"]
        )

        #  ~~~ Split Dataset ~~~
        train_size = int(0.8 * len(dataset))
        test_size = len(dataset) - train_size
        temp_dataset, self.dataset_test = random_split(
            dataset, [train_size, test_size]
        )

        train_size = int(0.8 * len(temp_dataset))
        val_size = len(temp_dataset) - train_size
        self.dataset_train, self.dataset_val = random_split(
            temp_dataset, [train_size, val_size]
        )

    def train_dataloader(self):
        return DataLoader(
            self.dataset_train,
            batch_size=self.batch_size,
            shuffle=True,
            collate_fn=collate_fn,
            num_workers=self.num_workers,
        )

    def val_dataloader(self):
        return DataLoader(
            self.dataset_val,
            batch_size=self.batch_size,
            shuffle=False,
            collate_fn=collate_fn,
            num_workers=self.num_workers,
        )

    def test_dataloader(self):
        return DataLoader(
            self.dataset_test,
            batch_size=self.batch_size,
            shuffle=False,
            collate_fn=collate_fn,
            num_workers=self.num_workers,
        )
