# fmt: off
import math

import pytest
import torch
from torch import nn

from torch_uncertainty.layers.bayesian import BayesLinear
from torch_uncertainty.losses import DECLoss, ELBOLoss, NIGLoss


# fmt: on
class TestELBOLoss:
    """Testing the ELBOLoss class."""

    def test_main(self):
        model = BayesLinear(1, 1)
        criterion = nn.BCEWithLogitsLoss()

        loss = ELBOLoss(model, criterion, kl_weight=1e-5, num_samples=1)

        loss(model(torch.randn(1, 1)), torch.randn(1, 1))

    def test_failures(self):
        model = BayesLinear(1, 1)
        criterion = nn.BCEWithLogitsLoss()

        with pytest.raises(ValueError):
            ELBOLoss(model, nn.BCEWithLogitsLoss, kl_weight=1, num_samples=1)

        with pytest.raises(ValueError):
            ELBOLoss(model, criterion, kl_weight=-1, num_samples=1)

        with pytest.raises(ValueError):
            ELBOLoss(model, criterion, kl_weight=1, num_samples=-1)

        with pytest.raises(TypeError):
            ELBOLoss(model, criterion, kl_weight=1e-5, num_samples=1.5)

    def test_no_bayes(self):
        model = nn.Linear(1, 1)
        criterion = nn.BCEWithLogitsLoss()

        loss = ELBOLoss(model, criterion, kl_weight=1e-5, num_samples=1)
        loss(model(torch.randn(1, 1)), torch.randn(1, 1))


# fmt: on
class TestNIGLoss:
    def test_main(self):
        loss = NIGLoss(reg_weight=1e-2)

        inputs = torch.tensor([[1.0, 1.0, 1.0, 1.0]], dtype=torch.float32)
        targets = torch.tensor([[1.0]], dtype=torch.float32)

        assert loss(*inputs.split(1, dim=-1), targets) == pytest.approx(
            2 * math.log(2)
        )

        loss = NIGLoss(
            reg_weight=1e-2,
            reduction="sum",
        )

        assert loss(
            *inputs.repeat(2, 1).split(1, dim=-1),
            targets.repeat(2, 1),
        ) == pytest.approx(4 * math.log(2))

        loss = NIGLoss(
            reg_weight=1e-2,
            reduction="none",
        )

        assert loss(
            *inputs.repeat(2, 1).split(1, dim=-1),
            targets.repeat(2, 1),
        ) == pytest.approx([2 * math.log(2), 2 * math.log(2)])

    def test_failures(self):
        with pytest.raises(ValueError):
            NIGLoss(reg_weight=-1)

        with pytest.raises(ValueError):
            NIGLoss(reg_weight=1.0, reduction="median")


class TestDECLoss:
    def test_main(self):
        loss = DECLoss(loss_type="mse", reg_weight=1e-2, annealing_step=1)
        loss(torch.tensor([[0.0, 0.0]]), torch.tensor([0]), epoch_num=1)
        loss = DECLoss(loss_type="mse", reg_weight=1e-2, annealing_step=1)
        loss(torch.tensor([[0.0, 0.0]]), torch.tensor([0]), epoch_num=0)
        loss(torch.tensor([[0.0, 0.0]]), torch.tensor([0]), epoch_num=None)
        loss = DECLoss(loss_type="log", reg_weight=1e-2)
        loss(torch.tensor([[0.0, 0.0]]), torch.tensor([0]))
        loss = DECLoss(loss_type="digamma")
        loss(torch.tensor([[0.0, 0.0]]), torch.tensor([0]))

    def test_failures(self):
        with pytest.raises(ValueError):
            DECLoss(reg_weight=-1)

        with pytest.raises(ValueError):
            DECLoss(annealing_step=0)

        with pytest.raises(ValueError):
            DECLoss(reduction="median")

        with pytest.raises(ValueError):
            DECLoss(loss_type="regression")
