from pathlib import Path
import lightning as L
import torch
import torch.nn.functional as F
from torchmetrics import Accuracy, ConfusionMatrix
import seaborn as sns
import matplotlib.pyplot as plt
from torchvision import models
from torch import nn, optim


class DocumentClassifier(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = models.resnet18(pretrained=True)
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
        outputs = self(images).squeeze(1)  # Ajustez la forme de sortie
        loss = F.binary_cross_entropy_with_logits(outputs, labels.squeeze(1))

        preds = torch.sigmoid(outputs) > 0.5
        self.train_accuracy.update(preds, labels.squeeze(1).int())

        self.log(
            "train_loss",
            loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        self.log(
            "train_acc",
            self.train_accuracy,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        return loss

    def validation_step(self, batch, batch_idx):
        images, labels = batch
        outputs = self(images).squeeze(1)  # Ajustez la forme de sortie
        loss = F.binary_cross_entropy_with_logits(outputs, labels.squeeze(1))

        preds = torch.sigmoid(outputs) > 0.5
        self.val_accuracy.update(preds, labels.squeeze(1).int())

        self.log(
            "val_loss",
            loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        self.log(
            "val_acc",
            self.val_accuracy,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )

    def test_step(self, batch, batch_idx):
        images, labels = batch
        outputs = self(images).squeeze(1)  # Ajustez la forme de sortie

        preds = torch.sigmoid(outputs) > 0.5
        self.test_accuracy.update(preds, labels.squeeze(1).int())

        self.log(
            "test_acc",
            self.test_accuracy,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )

        # ~~~ Confusion Matrix ~~~
        cm = self.conf_matrix(preds, labels.squeeze(1).int())
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.heatmap(cm.cpu().numpy(), annot=True, fmt="d", cmap="Blues", ax=ax)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title("Confusion Matrix")

        # ~~~ Save Artifact ~~~
        fig_path = Path(self.logger.save_dir) / "confusion_matrix.png"
        fig.savefig(fig_path)
        plt.close(fig)
        self.logger.experiment.log_artifact(fig_path)

    def configure_optimizers(self):
        optimizer = optim.SGD(self.parameters(), lr=0.001, momentum=0.9)
        return optimizer

    def on_train_epoch_end(self):
        self.train_accuracy.reset()

    def on_validation_epoch_end(self):
        self.val_accuracy.reset()

    def on_test_epoch_end(self):
        self.test_accuracy.reset()

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
