import lightning as L

from torchvision.models.detection import (
    fasterrcnn_resnet50_fpn_v2,
    FasterRCNN_ResNet50_FPN_V2_Weights,
)
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import torch
import seaborn as sns
import matplotlib.pyplot as plt

from torchmetrics.detection import IntersectionOverUnion
from torchmetrics.functional.classification import multiclass_confusion_matrix


def replace_keys(metrics_dict, key_mapping):
    new_metrics = {}
    for key, value in metrics_dict.items():
        # Use the new key from the mapping if it exists, otherwise use the old key
        new_key = key_mapping.get(key, key)
        new_metrics[new_key] = value
    return new_metrics


class FasterRCNNModule(L.LightningModule):
    def __init__(self, weights=FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT):
        super().__init__()
        self.model = fasterrcnn_resnet50_fpn_v2(
            weights=weights,
        )

        # Get number of input features for the classifier
        in_features = self.model.roi_heads.box_predictor.cls_score.in_features

        # Replace the pre-trained head with a new one (note we need num_classes+1 for background)
        self.model.roi_heads.box_predictor = FastRCNNPredictor(
            in_features, num_classes=3 + 1
        )

        self.iou = IntersectionOverUnion(
            class_metrics=True, respect_labels=True
        )

    def forward(self, images, targets=None):
        return self.model(images, targets)

    def training_step(self, batch, batch_idx):
        images, targets = batch

        # ~~~ Training loss ~~~
        self.model.train()
        loss_dict = self.model(images, targets)
        loss = sum(loss for loss in loss_dict.values())

        # ~~~ Training IoU ~~~
        self.model.eval()
        outputs = self.model(images)
        self.iou.update(outputs, targets)
        train_iou = self.iou.compute()
        self.iou.reset()

        train_mapping = {
            "iou": "train_iou",
            "iou/cl_0": "iou_train_figure",
            "iou/cl_1": "iou_train_text",
            "iou/cl_2": "iou_train_title",
        }
        self.log_dict(
            replace_keys(train_iou, train_mapping),
            on_step=False,
            on_epoch=True,
            logger=True,
            batch_size=len(batch),
        )
        self.log(
            "train_loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
            batch_size=len(batch),
        )
        return loss

    def validation_step(self, batch, batch_idx):
        images, targets = batch

        # ~~~ Val loss ~~~
        self.model.train()
        loss_dict = self.model(images, targets)
        loss = sum(loss for loss in loss_dict.values())
        self.log(
            "val_loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
            batch_size=len(batch),
        )

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(images)

            # ~~~ Val IoU ~~~
            self.iou.update(outputs, targets)
            val_iou = self.iou.compute()
            self.iou.reset()

            val_mapping = {
                "iou": "val_iou",
                "iou/cl_0": "iou_val_figure",
                "iou/cl_1": "iou_val_text",
                "iou/cl_2": "iou_val_title",
            }
            self.log_dict(
                replace_keys(val_iou, val_mapping),
                on_step=False,
                on_epoch=True,
                logger=True,
                batch_size=len(batch),
            )

    def test_step(self, batch, batch_idx):

        images, targets = batch
        predictions = self(images)
        preds = torch.cat(predictions)
        labels = torch.cat(targets)

        # ~~~ Confusion Matrix ~~~
        # https://github.com/Lightning-AI/pytorch-lightning/discussions/18274
        # cm = multiclass_confusion_matrix(
        #     labels.cpu(), preds.cpu(), num_classes=3
        # )
        # fig = plt.figure(figsize=(10, 10))
        # sns.heatmap(cm, annot=True, fmt="g", cmap="Blues")
        # plt.xlabel("Predicted labels")
        # plt.ylabel("True labels")
        # plt.title("Confusion Matrix")

        # mlf_logger = self.logger.experiment
        # mlf_logger.add_figure("Confusion Matrix", fig, self.current_epoch)
        # ~~~ IoU ~~~
        metric = IntersectionOverUnion(class_metrics=True)
        iou = metric(predictions, targets)

        self.log("test_iou", iou, logger=True, batch_size=len(batch))
        self.iou.reset()

    def configure_optimizers(self):
        optimizer = torch.optim.SGD(
            self.parameters(), lr=0.005, momentum=0.9, weight_decay=0.0005
        )
        return optimizer
