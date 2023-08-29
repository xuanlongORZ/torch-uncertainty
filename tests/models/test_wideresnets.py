import torch

from torch_uncertainty.models.wideresnet.batched import batched_wideresnet28x10
from torch_uncertainty.models.wideresnet.masked import masked_wideresnet28x10
from torch_uncertainty.models.wideresnet.mimo import mimo_wideresnet28x10
from torch_uncertainty.models.wideresnet.packed import packed_wideresnet28x10


class TestPackedResnet:
    """Testing the WideResNet packed class."""

    def test_main(self):
        packed_wideresnet28x10(1, 2, 2, 1, 1, 10, style="imagenet")


class TestMaskedWide:
    """Testing the WideResNet masked class."""

    def test_main(self):
        masked_wideresnet28x10(1, 2, 2, 1, 10, style="imagenet")


class TestBatchedWide:
    """Testing the WideResNet batched class."""

    def test_main(self):
        batched_wideresnet28x10(1, 2, 1, 10, style="imagenet")


class TestMIMOWide:
    """Testing the WideResNet mimo class."""

    def test_main(self):
        model = mimo_wideresnet28x10(1, 10, 2, style="cifar")
        model(torch.rand((2, 1, 28, 28)))
