# fmt:off
import pytest

from torch_uncertainty.datasets.classification import CIFAR10H


# fmt:on
class TestCIFAR10_H:
    """Testing the CIFAR10H dataset class."""

    def test_nodataset_nodownload(self):
        with pytest.raises(RuntimeError):
            _ = CIFAR10H("./.data", download=False)
