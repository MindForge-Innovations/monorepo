from pathlib import Path
import lightning as L
from torch.utils.data import DataLoader, random_split, Dataset
from torch.utils.data.sampler import WeightedRandomSampler
from torchvision import transforms
from PIL import Image
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import torch


class CustomImageDataset(Dataset):
    def __init__(self, root_dir, transform=None, upsample=False):
        self.root_dir = root_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        self.label_counts = Counter()

        for subdir in ["Grotius-DG", "Puf-DNG", "Vattel-DG"]:
            full_subdir_path = Path(root_dir) / subdir
            for label, category in enumerate(
                ["page_with_content", "page_with_title"]
            ):
                category_path = full_subdir_path / category
                for image_path in category_path.glob("**/*.*"):
                    self.image_paths.append(image_path)
                    self.labels.append(label)
                    self.label_counts[label] += 1

        if upsample:
            self.upsample()

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        label = torch.tensor([label], dtype=torch.float32)

        return image, label

    def upsample(self):
        """Upsample the minority class."""
        class_counts = np.bincount(self.labels)
        max_count = max(class_counts)

        new_image_paths = []
        new_labels = []

        for label in np.unique(self.labels):
            indices = np.where(np.array(self.labels) == label)[0]
            sampled_indices = np.random.choice(indices, max_count, replace=True)
            new_image_paths.extend(
                [self.image_paths[i] for i in sampled_indices]
            )
            new_labels.extend([label] * max_count)

        self.image_paths = new_image_paths
        self.labels = new_labels

    def get_label_distribution(self):
        """Get the distribution of labels in the dataset."""
        return dict(Counter(self.labels))


class ClassificationDataModule(L.LightningDataModule):
    def __init__(
        self, data_dir, batch_size, num_workers=4, shuffle=True, upsample=False
    ):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.shuffle = shuffle
        self.upsample = upsample
        self.dataset_train = None
        self.dataset_val = None
        self.dataset_test = None

        # Define the transformations
        self.transform = transforms.Compose(
            [transforms.Resize((240, 240)), transforms.ToTensor()]
        )

    def set_logger(self, logger):
        self.logger = logger

    def set_mlflow_logger(self, mlflow_logger):
        self.mlflow_logger = mlflow_logger

    def setup(self, stage=None):
        """Setup data loaders. Stage can be {fit, validate, test, predict}."""

        #  ~~~ Load Dataset ~~~
        dataset = CustomImageDataset(
            root_dir=self.data_dir,
            transform=self.transform,
            upsample=self.upsample,
        )

        if len(dataset) == 0:
            raise ValueError(
                "The dataset is empty. Please check the data directory."
            )
        
        self.logger.info(f"Dataset loaded with {len(dataset)} samples.")
        # self.mlflow_logger.log_param("dataset_size",len(dataset))

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

        self.logger.info(f"Train size: {train_size}, Test size: {test_size}")
        # self.mlflow_logger.log_param("train_size",train_size)
        # self.mlflow_logger.log_param("test_size",test_size)
        self.mlflow_logger.log_hyperparams({"train_size":train_size,"test_size":test_size})
        if len(self.dataset_train) == 0:
            raise ValueError(
                "The training dataset is empty. Please check the data splitting."
            )
        if len(self.dataset_val) == 0:
            raise ValueError(
                "The validation dataset is empty. Please check the data splitting."
            )
        if len(self.dataset_test) == 0:
            raise ValueError(
                "The test dataset is empty. Please check the data splitting."
            )

    def train_dataloader(self):
        return DataLoader(
            self.dataset_train,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
        )

    def val_dataloader(self):
        return DataLoader(
            self.dataset_val,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )

    def test_dataloader(self):
        return DataLoader(
            self.dataset_test,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )

    def plot_label_distribution(self):
        """Plot the label distribution of the training dataset."""
        # Convert label tensors to integers
        train_labels = [int(label) for _, label in self.dataset_train]
        label_counts = dict(Counter(train_labels))
        fig, ax = plt.subplots()
        ax.bar(label_counts.keys(), label_counts.values())
        ax.set_xlabel("Label")
        ax.set_ylabel("Count")
        ax.set_title("Label Distribution in Training Dataset")
        #self.mlflow_logger.log_figure(fig, "label_distribution.png")
        plt.show()
