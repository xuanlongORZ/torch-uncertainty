# fmt: off
from typing import Any, Dict, List, Type, Union

import torch
from einops import rearrange
from torch import Tensor, nn

from ...layers.packed import PackedConv2d, PackedLinear
from ..utils import toggle_dropout


# fmt: on
class VGG(nn.Module):
    def __init__(
        self,
        vgg_cfg: List[Union[str, int]],
        in_channels: int,
        num_classes: int,
        linear_layer: Type[nn.Module],
        conv2d_layer: Type[nn.Module],
        norm: Type[nn.Module],
        groups: int,
        dropout_rate: float,
        style: str,
        **model_kwargs: Any,
    ) -> None:
        super().__init__()

        self.in_channels = in_channels
        self.linear_layer = linear_layer
        self.conv2d_layer = conv2d_layer
        self.norm = norm
        self.groups = groups

        if self.conv2d_layer == PackedConv2d:
            self.num_estimators = model_kwargs.get("num_estimators")
        else:
            self.num_estimators = model_kwargs.pop("num_estimators")
        self.last_layer_dropout = model_kwargs.pop("last_layer_dropout", False)
        self.model_kwargs = model_kwargs

        self.features = self._make_layers(vgg_cfg)

        if style == "imagenet":
            self.avgpool = nn.AdaptiveAvgPool2d((7, 7))
            kernel_surface = 7 * 7
        else:
            self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
            kernel_surface = 1

        if self.linear_layer == PackedLinear:
            last_linear = linear_layer(
                4096, num_classes, last=True, **model_kwargs
            )
        else:
            last_linear = linear_layer(4096, num_classes, **model_kwargs)

        self.cls_head_layers = [
            linear_layer(512 * kernel_surface, 4096, **model_kwargs),
            nn.ReLU(True),
            nn.Dropout(p=dropout_rate),
            linear_layer(4096, 4096, **model_kwargs),
            nn.ReLU(True),
            nn.Dropout(p=dropout_rate),
            last_linear,
        ]

        self.cls_head = nn.Sequential(*self.cls_head_layers)
        self._init_weights()

    def _init_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, PackedConv2d):
                nn.init.kaiming_normal_(
                    m.weight, mode="fan_out", nonlinearity="relu"
                )
                if m.bias is not None:  # coverage: ignore
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):  # coverage: ignore
                nn.init.constant_(m.weight, 1)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear) or isinstance(m, PackedLinear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None:  # coverage: ignore
                    nn.init.constant_(m.bias, 0)

    def _make_layers(self, cfg: List) -> nn.Sequential:
        layers: List[nn.Module] = []
        in_channels = self.in_channels
        for i, v in enumerate(cfg):
            if v == "M":
                layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
            else:
                if i == 0 and self.conv2d_layer == PackedConv2d:
                    conv2d = self.conv2d_layer(
                        in_channels,
                        v,
                        kernel_size=3,
                        padding=1,
                        groups=self.groups,
                        first=True,
                        **self.model_kwargs,
                    )
                else:
                    conv2d = self.conv2d_layer(
                        in_channels,
                        v,
                        kernel_size=3,
                        padding=1,
                        groups=self.groups if i != 0 else 1,
                        **self.model_kwargs,
                    )
                layers.extend([conv2d, self.norm(v), nn.ReLU(inplace=True)])
                in_channels = v
        return nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        if self.linear_layer != PackedLinear:
            x = self.handle_dropout(x)

        x = self.features(x)

        if self.linear_layer == PackedLinear:
            x = rearrange(
                x,
                "e (m c) h w -> (m e) c h w",
                m=self.model_kwargs["num_estimators"],
            )
        x = self.avgpool(x)
        x = torch.flatten(x, 1)

        x = self.cls_head(x)
        return x

    def handle_dropout(self, x: Tensor) -> Tensor:
        if self.num_estimators is not None:
            if not self.training:
                if self.last_layer_dropout is not None:
                    toggle_dropout(self, self.last_layer_dropout)
                x = x.repeat(self.num_estimators, 1, 1, 1)
        return x


def _vgg(
    vgg_cfg: Dict[str, List[Union[str, int]]],
    in_channels: int,
    num_classes: int,
    linear_layer: Type[nn.Module] = nn.Linear,
    conv2d_layer: Type[nn.Module] = nn.Conv2d,
    norm: Type[nn.Module] = nn.Identity,
    groups: int = 1,
    dropout_rate: float = 0.5,
    style: str = "imagenet",
    **model_kwargs: Any,
) -> VGG:
    return VGG(
        vgg_cfg,
        in_channels,
        num_classes,
        linear_layer,
        conv2d_layer,
        norm,
        groups,
        dropout_rate,
        style,
        **model_kwargs,
    )
