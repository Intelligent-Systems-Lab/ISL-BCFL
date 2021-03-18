import torch
import copy
import math
from compressor import Compressor


class DGCCompressor(Compressor):
    def __init__(self, compress_ratio=0.5):
        super().__init__(average=True, tensors_size_are_same=False)
        self.compress_ratio = compress_ratio
        self.param_groups_c = None

    def clean(self):
        self.param_groups_c = None

    def compress_by_layer(self, param):
        pass

    def compress(self, mem, compress=True):
        gradient_list = copy.deepcopy(mem)
        agg_gradient = []
        for i in range(len(gradient_list[0])):
            result = torch.stack([j[i] for j in gradient_list]).sum(dim=0)
            agg_gradient.append(result / len(gradient_list))

        compressed_grad = []

        for tensor in agg_gradient:
            shape = list(tensor.size())
            tensor = tensor.flatten()
            numel = tensor.numel()

            tensor_a = tensor.abs()
            tensor_a = tensor_a[tensor_a > 0]

            idx = min(tensor_a.numel() - 1, max(0, math.floor(tensor_a.numel() * self.compress_ratio)))

            tensor_sort = sorted(range(len(tensor_a)), key=lambda k: tensor_a[k])
            tensor_sort.reverse()

            # print("len_tensor_a: {}, len_tensor_sort: {}, idx: {}".format(tensor_a.numel(), tensor_sort, idx))

            if not len(tensor_sort) == 0:
                thr = tensor_a[tensor_sort[idx]]
            else:
                thr = 1  # becauce all element are 0, set thr=1 make mask mask out everything

            mask = tensor.abs() >= thr
            selected = mask.sum()

            indices, = torch.where(mask)
            values = tensor[indices]

            tensor_compressed = values.tolist()  # , indices
            ctx = shape, mask.tolist(), numel
            # tensor boolean is to big

            compressed_grad.append((tensor_compressed, ctx))
        return compressed_grad

    def reformat_only(self, gradient):
        agg_gradient = copy.deepcopy(gradient)
        compressed_grad = []

        for tensor in agg_gradient:
            shape = list(tensor.size())
            tensor = tensor.flatten()
            numel = tensor.numel()

            mask = tensor.abs() > 0
            selected = mask.sum()

            indices, = torch.where(mask)
            values = tensor[indices]

            tensor_compressed = values.tolist()  # , indices
            ctx = shape, mask.tolist(), numel
            # tensor boolean is to big

            compressed_grad.append((tensor_compressed, ctx))
        return compressed_grad

    def decompress(self, mem):
        agg_gradient = copy.deepcopy(mem)
        decompressed_mem = []
        for j in agg_gradient:
            new_mem, ctx = j
            shape, mask, numel = ctx


            values = torch.tensor(new_mem)
            indices = torch.tensor([i for i in range(len(mask)) if mask[i]]).type(torch.long)
            mask = torch.tensor(mask)

            tensor_decompressed = torch.zeros(numel, dtype=values.dtype, layout=values.layout, device=values.device)
            tensor_decompressed.scatter_(0, indices, values)
            decompressed_mem.append(tensor_decompressed.view(shape))

        return decompressed_mem