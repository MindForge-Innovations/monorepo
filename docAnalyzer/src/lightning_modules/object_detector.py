import lightning as L

from torchvision.models.detection import (
    fasterrcnn_resnet50_fpn_v2,
    FasterRCNN_ResNet50_FPN_V2_Weights,
)
import torch


class FasterRCNNModule(L.LightningModule):
    def __init__(self, weights):
        super().__init__()
        self.model = fasterrcnn_resnet50_fpn_v2(
            weights=FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
        )

    def forward(self, images, targets=None):
        return self.model(images, targets)

    def training_step(self, batch, batch_idx):
        images, targets = batch
        self.model.train()
        loss_dict = self.model(images, targets)
        loss = sum(loss for loss in loss_dict.values())
        self.log(
            "train_loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        return loss

    def validation_step(self, batch, batch_idx):
        images, targets = batch
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(images)
        num_detection = sum(len(output["boxes"]) for output in outputs)
        self.log(
            "val_num_detections",
            num_detection,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        return num_detection

    def configure_optimizers(self):
        optimizer = torch.optim.SGD(
            self.parameters(), lr=0.005, momentum=0.9, weight_decay=0.0005
        )
        return optimizer