import torch
import copy
from dgc.dgc import DGCCompressor
"""
Original usage:

optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
optimizer.zero_grad()
output = model(input)
loss = loss_fn(output, target)
loss.backward()
optimizer.step()
"""

"""
DGCSGD usage:

optimizer = DGCSGD(model.parameters(), lr=0.1, compress_ratio=0.5)

optimizer.memory.clean()

for input,target in dataloader:
    optimizer.zero_grad()
    output = model(input)
    loss = loss_fn(output, target)
    loss.backward()
    # gradient accumulation
    optimizer.gradient_collect()

optimizer.compress()
cg = optimizer.get_compressed_gradient()
<send gradient>

if <receive aggregated gradient>:
    dg = optimizer.decompress(new_gradient)
    optimizer.set_gradient(dg)
    optimizer.step()
"""


# copy from torch/optim/sgd.py
class DGCSGD(torch.optim.Optimizer):
    def __init__(self, params, lr=None, momentum=0, dampening=0,
                 weight_decay=0, nesterov=False, compress_ratio=0.5):
        if lr is None and lr < 0.0:
            raise ValueError("Invalid learning rate: {}".format(lr))
        if momentum < 0.0:
            raise ValueError("Invalid momentum value: {}".format(momentum))
        if weight_decay < 0.0:
            raise ValueError("Invalid weight_decay value: {}".format(weight_decay))

        self.memory = DGCMemory()
        self.compressor = DGCCompressor(compress_ratio = compress_ratio)

        defaults = dict(lr=lr, momentum=momentum, dampening=dampening,
                        weight_decay=weight_decay, nesterov=nesterov)
        if nesterov and (momentum <= 0 or dampening != 0):
            raise ValueError("Nesterov momentum requires a momentum and zero dampening")
        super(DGCSGD, self).__init__(params, defaults)

    def __setstate__(self, state):
        super(DGCSGD, self).__setstate__(state)
        for group in self.param_groups:
            group.setdefault('nesterov', False)

    def gradient_collect(self):
        self.memory.add(self.param_groups)

    def compress(self, compress=True):
        r = self.compressor.compress(self.memory.get_mem(), compress=compress)
        self.memory.set_compressed_mem(r)

    def decompress(self, d):
        d = self.compressor.decompress(d)
        self.memory.set_decompressed_mem(d)
        return d

    def get_compressed_gradient(self):
        return self.memory.compressed_mem

    def set_gradient(self, cg):
        agged_grad = copy.deepcopy(cg)
        for group in self.param_groups:
            for p in range(len(group['params'])):
                #print("group: {}".format(type(group['params'][p].grad)))
                #print("agged: {}".format(type(agged_grad[p])))
                if group['params'][p].is_cuda:
                    group['params'][p].grad = copy.deepcopy(agged_grad[p]).cuda()
                else:
                    group['params'][p].grad = copy.deepcopy(agged_grad[p]).cpu()

        # for group in len(self.param_groups):
        #     for p in len(self.param_groups[group]['params']):
        #         if self.param_groups[group]['params'][p].grad.size() == data[group]['params'][p].grad.size():
        #             self.param_groups[group]['params'][p].grad = copy.deepcopy(data[group]['params'][p].grad)

    @torch.no_grad()
    def step(self, closure=None):
        """Performs a single optimization step.

        Arguments:
            closure (callable, optional): A closure that reevaluates the model
                and returns the loss.
        """
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()
                
#         self.gradient_collect()
#         self.zero_grad()
#         self.compress(compress=False)
#         cg = self.decompress(self.get_compressed_gradient())
#         #optimizer.set_gradient(cg)
#         #m = self.memory.get_mem()[0]
#         self.set_gradient(cg)

        for group in self.param_groups:
            weight_decay = group['weight_decay']
            momentum = group['momentum']
            dampening = group['dampening']
            nesterov = group['nesterov']

            for p in group['params']:
                if p.grad is None:
                    continue
                d_p = p.grad
                if weight_decay != 0:
                    d_p = d_p.add(p, alpha=weight_decay)
                if momentum != 0:
                    param_state = self.state[p]
                    if 'momentum_buffer' not in param_state:
                        buf = param_state['momentum_buffer'] = torch.clone(d_p).detach()
                    else:
                        buf = param_state['momentum_buffer']
                        buf.mul_(momentum).add_(d_p, alpha=1 - dampening)
                    if nesterov:
                        d_p = d_p.add(buf, alpha=momentum)
                    else:
                        d_p = buf

                p.add_(d_p, alpha=-group['lr'])

        #self.memory.clean()
        return loss


class DGCMemory:
    def __init__(self):
        self.mem = []
        self.compressed_mem = None
        self.decompressed_mem = None
        self.can_add = True

    def set_compressed_mem(self, d):
        # self.can_add = False
        self.compressed_mem = d
        pass

    def set_decompressed_mem(self, d):
        self.decompressed_mem = d
        pass

    def add(self, d):
        if self.can_add:
            g = []
            for group in d:
                for p in group['params']:
                    g.append(copy.deepcopy(p.grad))
            self.mem.append(g)

    def get_mem(self):
        self.can_add = False
        return self.mem

    def get_compressed_mem(self):
        return self.compressed_mem

    def clean(self):
        self.mem = []
        self.compressed_mem = None
        self.decompressed_mem = None
        self.can_add = True
