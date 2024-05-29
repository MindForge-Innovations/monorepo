import lightning as L
import matplotlib.pyplot as plt
from pathlib import Path


class MetricsPlotCallback(L.Callback):
    def __init__(self, save_path):
        super().__init__()
        self.save_path = Path(save_path)
        self.save_path.mkdir(parents=True, exist_ok=True)

    def on_train_end(self, trainer, pl_module):
        metrics = trainer.callback_metrics

        # # Plot Loss
        # plt.figure()
        # plt.plot(metrics["step"], metrics["train_loss"], label="Train Loss")
        # plt.plot(metrics["step"], metrics["val_loss"], label="Val Loss")
        # plt.xlabel("Steps")
        # plt.ylabel("Loss")
        # plt.title("Train vs Val Loss")
        # plt.legend()
        # plt.savefig(self.save_path / "train_vs_val_loss.png")
        # plt.close()

        # # Plot Accuracy
        # plt.figure()
        # plt.plot(metrics["step"], metrics["train_acc"], label="Train Accuracy")
        # plt.plot(metrics["step"], metrics["val_acc"], label="Val Accuracy")
        # plt.xlabel("Steps")
        # plt.ylabel("Accuracy")
        # plt.title("Train vs Val Accuracy")
        # plt.legend()
        # plt.savefig(self.save_path / "train_vs_val_accuracy.png")
        # plt.close()
