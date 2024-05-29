from pathlib import Path
import lightning as L
import torch
import torch.nn.functional as F
from torchmetrics import Accuracy, ConfusionMatrix
import seaborn as sns
import matplotlib.pyplot as plt
from torchvision import models
from torch import nn, optim
from torchvision.models.resnet import ResNet18_Weights


class DocumentClassifier(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, 1)

        self.train_accuracy = Accuracy(task="binary")
        self.val_accuracy = Accuracy(task="binary")
        self.test_accuracy = Accuracy(task="binary")
        self.conf_matrix = ConfusionMatrix(task="binary", num_classes=2)

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        images, labels = batch
        outputs = self(images).squeeze(1)
        loss = F.binary_cross_entropy_with_logits(outputs, labels.squeeze(1))

        preds = torch.sigmoid(outputs) > 0.5
        self.train_accuracy.update(preds, labels.squeeze(1).int())

        self.log(
            "train_loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        self.log(
            "train_acc",
            self.train_accuracy.compute(),
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        return loss

    def validation_step(self, batch, batch_idx):
        images, labels = batch
        outputs = self(images).squeeze(1)
        loss = F.binary_cross_entropy_with_logits(outputs, labels.squeeze(1))

        preds = torch.sigmoid(outputs) > 0.5
        self.val_accuracy.update(preds, labels.squeeze(1).int())

        self.log(
            "val_loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        self.log(
            "val_acc",
            self.val_accuracy.compute(),
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )

    def test_step(self, batch, batch_idx):
        images, labels = batch
        outputs = self(images).squeeze(1)

        preds = torch.sigmoid(outputs) > 0.5
        self.test_accuracy.update(preds, labels.squeeze(1).int())

        self.log(
            "test_acc",
            self.test_accuracy.compute(),
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        self.conf_matrix.update(preds, labels.squeeze(1).int())

    def configure_optimizers(self):
        optimizer = optim.SGD(self.parameters(), lr=0.001, momentum=0.9)
        return optimizer

    def on_test_epoch_end(self):
        # ~~~ Confusion Matrix ~~~
        cm = self.conf_matrix.compute()
        fig, ax = plt.subplots(figsize=(10, 7))
        sns.heatmap(cm.cpu().numpy(), annot=True, fmt="d", cmap="Blues", ax=ax)
        ax.set_xlabel("Predicted Labels")
        ax.set_ylabel("True Labels")
        ax.set_title("Confusion Matrix")
        plt.show()

        # # ~~~ Save Artifact ~~~
        # fig_path = Path(self.logger.save_dir) / "confusion_matrix.png"
        # fig.savefig(fig_path)
        # plt.close(fig)
        # self.logger.experiment.log_artifact(fig_path)
        self.conf_matrix.reset()
        self.test_accuracy.reset()

    def on_train_epoch_end(self):
        self.train_accuracy.reset()

    def on_validation_epoch_end(self):
        self.val_accuracy.reset()

    def on_epoch_end(self):
        self.logger.experiment.add_scalars(
            "Loss",
            {
                "train": self.trainer.callback_metrics["train_loss"],
                "val": self.trainer.callback_metrics["val_loss"],
            },
            self.current_epoch,
        )
        self.logger.experiment.add_scalars(
            "Accuracy",
            {
                "train": self.trainer.callback_metrics["train_acc"],
                "val": self.trainer.callback_metrics["val_acc"],
            },
            self.current_epoch,
        )
