# fmt:off
import torch
from torch import nn
from torchinfo import summary

from torch_uncertainty.baselines import VGG, ResNet, WideResNet
from torch_uncertainty.optimization_procedures import (
    optim_cifar10_resnet18,
    optim_cifar10_wideresnet,
)


# fmt:on
class TestStandardBaseline:
    """Testing the ResNet baseline class."""

    def test_standard(self):
        net = ResNet(
            num_classes=10,
            in_channels=3,
            loss=nn.CrossEntropyLoss,
            optimization_procedure=optim_cifar10_resnet18,
            version="mc-dropout",
            num_estimators=4,
            arch=18,
            style="cifar",
            groups=1,
        )
        summary(net)

        _ = net.criterion
        _ = net.configure_optimizers()
        _ = net(torch.rand(1, 3, 32, 32))


class TestStandardWideBaseline:
    """Testing the WideResNet baseline class."""

    def test_standard(self):
        net = WideResNet(
            num_classes=10,
            in_channels=3,
            loss=nn.CrossEntropyLoss,
            optimization_procedure=optim_cifar10_wideresnet,
            version="mc-dropout",
            num_estimators=4,
            style="cifar",
            groups=1,
        )
        summary(net)

        _ = net.criterion
        _ = net.configure_optimizers()
        _ = net(torch.rand(1, 3, 32, 32))


class TestStandardVGGBaseline:
    """Testing the VGG baseline class."""

    def test_standard(self):
        net = VGG(
            num_classes=10,
            in_channels=3,
            loss=nn.CrossEntropyLoss,
            optimization_procedure=optim_cifar10_resnet18,
            version="mc-dropout",
            num_estimators=4,
            arch=11,
            groups=1,
        )
        summary(net)

        _ = net.criterion
        _ = net.configure_optimizers()
        _ = net(torch.rand(1, 3, 32, 32))
