from torchvision.transforms import v2
from torchvision import tv_tensors, datasets
import torch


def get_object_detection_transform():
    """
    Retourne les transformations à appliquer sur les images.

    Returns
    -------
    torchvision.transforms.Compose
        Un objet Compose qui combine toutes les transformations à appliquer.
    """
    transforms = v2.Compose(
        [
            v2.ToImage(),
            v2.RandomPhotometricDistort(p=1),
            v2.RandomZoomOut(
                fill={tv_tensors.Image: (123, 117, 104), "others": 0}
            ),
            v2.RandomIoUCrop(),
            v2.RandomHorizontalFlip(p=1),
            v2.SanitizeBoundingBoxes(),
            v2.ToDtype(torch.float32, scale=True),
        ]
    )
    return transforms


def get_basic_transform():
    """
    Retourne les transformations à appliquer sur les images.

    Returns
    -------
    torchvision.transforms.Compose
        Un objet Compose qui combine toutes les transformations à appliquer.
    """
    transforms = v2.Compose(
        [
            v2.ToImage(),
            v2.Resize((1024, 768)),
            v2.PILToTensor(),
            v2.ToDtype(torch.float32, scale=True),
        ]
    )
    return transforms
