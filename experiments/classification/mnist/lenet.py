# fmt: off
from pathlib import Path

import torch.nn as nn
import torch.optim as optim

from torch_uncertainty import cls_main, init_args
from torch_uncertainty.datamodules import MNISTDataModule
from torch_uncertainty.models.lenet import lenet
from torch_uncertainty.routines.classification import ClassificationSingle

# fmt: on


def optim_lenet(model: nn.Module) -> dict:
    """Optimization procedure for LeNet.

    Uses Adam default hyperparameters.

    Args:
        model (nn.Module): LeNet model.
    """
    return {
        "optimizer": optim.Adam(
            model.parameters(),
        )
    }


if __name__ == "__main__":
    root = Path(__file__).parent.absolute().parents[2]

    args = init_args(datamodule=MNISTDataModule)

    net_name = "std-lenet-mnist"

    # datamodule
    args.root = str(root / "data")
    dm = MNISTDataModule(**vars(args))

    # model
    model = lenet(dm.num_channels, dm.num_classes)

    baseline = ClassificationSingle(
        model=model,
        num_classes=dm.num_classes,
        in_channels=dm.num_channels,
        loss=nn.CrossEntropyLoss,
        optimization_procedure=optim_lenet,
        **vars(args),
    )

    cls_main(baseline, dm, root, net_name, args)
