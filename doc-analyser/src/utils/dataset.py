from pathlib import Path
from torchvision.datasets import CocoDetection


class CustomCocoDetection(CocoDetection):
    """
    Un dataset personnalisé pour la détection d'objets qui étend CocoDetection.

    Parameters
    ----------
    root : str ou Path
        Le chemin du dossier contenant les images.
    annFile : str ou Path
        Le chemin du fichier d'annotations JSON au format COCO.
    transforms : callable, optionnel
        A function/transform that takes input sample and its target as entry
                and returns a transformed version.
    """

    def __init__(self, root, annFile, transforms):
        super().__init__(root, str(annFile))
        self.transforms = transforms

    def __getitem__(self, index):
        """
        Récupère une image et ses annotations à l'index spécifié.

        Parameters
        ----------
        index : int
            L'index de l'élément à récupérer.

        Returns
        -------
        tuple
            Un tuple (image, target) où image est l'image transformée et target ses annotations.
        """
        img, target = super().__getitem__(index)

        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target


# Exemple d'utilisation
if __name__ == "__main__":
    # Chemins des dossiers et fichiers
    data_dir = "/home/olivier/projet/pi/monorepo/docAnalyzer/object_detection_project/data"
    phase = "train"  # ou 'val' ou 'test'

    images_dir = Path(data_dir) / f"{phase}/images"
    annotations_file = Path(data_dir) / f"{phase}/{phase}.json"

    # Création de l'instance du dataset
    from torchvision.transforms import v2
    from torchvision import tv_tensors, datasets
    import torch

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
    transforms = v2.Compose(
        [
            v2.ToImage(),
            v2.Resize((1024, 768)),
            v2.PILToTensor(),
        ]
    )
    dataset = CustomCocoDetection(
        root=images_dir, annFile=annotations_file, transforms=transforms
    )

    # # Itérer sur le dataset
    # for img, target in dataset:
    #     print(f"Image: {type(img)}")
    #     print(
    #         f"{type(img) = }\n{type(target) = }\n{type(target[0]) = }\n{target[0].keys() = }"
    #     )
    # dataset[0]
