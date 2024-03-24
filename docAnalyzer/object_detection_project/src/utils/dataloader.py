from torch.utils.data import DataLoader
from src.utils.dataset import CustomCocoDetection
from src.utils.transforms import (
    get_object_detection_transform,
    get_basic_transform,
)
from torchvision import datasets
import torch

from pathlib import Path


def collate_fn(batch):
    """
    Custom collate function to handle batches of images and targets with
    varying number of objects.

    Parameters:
    batch (list): A list of tuples (image, target), where 'image' is a tensor
                  and 'target' is a dictionary.

    Returns:
    tuple: Batched images and targets.
    """
    images = [item[0] for item in batch]
    targets = [item[1] for item in batch]

    # Stack images as they should have the same dimensions
    images = torch.stack(images, 0)

    return images, targets


def create_dataloader(data_dir, phase, batch_size, num_workers=4, shuffle=True):
    """
    Crée un DataLoader pour une phase spécifique du dataset.

    Parameters
    ----------
    data_dir : str
        Le chemin du répertoire contenant le dataset.
    phase : str
        Phase du dataset ('train', 'val' ou 'test').
    batch_size : int
        Taille des batches de données.
    num_workers : int, optional
        Nombre de sous-processus à utiliser pour le chargement des données. Par défaut à 4.
    shuffle : bool, optional
        Si les données doivent être mélangées. Par défaut à True pour l'entraînement.

    Returns
    -------
    DataLoader
        Le DataLoader pour la phase spécifiée.
    """
    assert phase in [
        "train",
        "val",
        "test",
    ], "La phase doit être 'train', 'val' ou 'test'."

    # Chemin vers les images et fichier d'annotations
    root = f"{data_dir}/{phase}/images"
    annotation = f"{data_dir}/{phase}/{phase}.json"

    # Création de l'instance dataset
    dataset = CustomCocoDetection(
        root, annotation, transforms=get_basic_transform()
    )

    # Wrapping du dataset pour la transformation
    dataset = datasets.wrap_dataset_for_transforms_v2(
        dataset, target_keys=["boxes", "labels"]
    )

    # Créer le DataLoader
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn,
    )
