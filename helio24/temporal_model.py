"""Small causal convolution candidate; optional torch dependency."""
import torch
from torch import nn
from torch.nn import functional as F


class CausalBlock(nn.Module):
    def __init__(self, inputs, width, dilation):
        super().__init__()
        self.padding = 2*dilation
        self.conv = nn.Conv1d(inputs,width,3,dilation=dilation)
        self.skip = nn.Identity() if inputs==width else nn.Conv1d(inputs,width,1)
        self.dropout = nn.Dropout(.1)

    def forward(self,x):
        return F.relu(self.skip(x)+self.dropout(F.relu(self.conv(F.pad(x,(self.padding,0))))))


class TemporalClassifier(nn.Module):
    """48 channels: scaled magnetic values, then missingness indicators.

    No time IDs, normalization over time, or right padding. The final step has
    a receptive field of 63 slots, covering all 60 input steps.
    """
    def __init__(self):
        super().__init__()
        self.blocks=nn.Sequential(*[CausalBlock(48 if i==0 else 32,32,d) for i,d in enumerate([1,2,4,8,16])])
        self.head=nn.Conv1d(32,1,1)

    def temporal_logits(self,x):
        return self.head(self.blocks(x.transpose(1,2))).squeeze(1)

    def forward(self,x):
        return self.temporal_logits(x)[:,-1]
