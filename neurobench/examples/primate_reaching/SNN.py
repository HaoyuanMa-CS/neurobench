import torch
import torch.nn as nn
import snntorch as snn
from snntorch import surrogate


## Define model ##
class SNN(nn.Module):

    def __init__(self, window=250, input_size=96, hidden_size=50, tau=0.96, p=0.3, device='cpu'):
        super().__init__()

        self.window = window
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = 2
        self.surrogate = surrogate.fast_sigmoid(slope=20)

        self.fc1 = nn.Linear(self.input_size, self.hidden_size, bias=False, device=device)
        self.fc2 = nn.Linear(self.hidden_size, self.output_size, bias=False, device=device)

        self.lif1 = snn.Leaky(beta=tau, spike_grad=self.surrogate, threshold=1, learn_beta=False,
                              learn_threshold=False, reset_mechanism='zero')
        self.lif2 = snn.Leaky(beta=tau, spike_grad=self.surrogate, threshold=1, learn_beta=False,
                              learn_threshold=False, reset_mechanism='none')

        self.dropout = nn.Dropout(p)
        self.mem1, self.mem2 = None, None

    def reset(self):
        self.mem1 = self.lif1.init_leaky()
        self.mem2 = self.lif2.init_leaky()

    def forward(self, x):
        cur1 = self.dropout(self.fc1(x))
        spk1, mem1 = self.lif1(cur1, self.mem1)

        cur2 = self.fc2(spk1)
        spk2, mem2 = self.lif2(cur2, self.mem2)

        return mem2, None
