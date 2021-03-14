import torch
import copy
from compressor import Compressor


class DGCCompressor(Compressor):
    def __init__(self, compress_ratio):
        super().__init__(average=True, tensors_size_are_same=False)
        self.compress_ratio = compress_ratio
        self.param_groups_c = None

    def clean(self):
        self.param_groups_c = None

    def compress_by_layer(self, param):
        pass

    def compress(self, mem):
        memory = copy.deepcopy(mem)
        compressed_mem = []
        for tensor in memory:
            shape = tensor.size()
            tensor = tensor.flatten()
            numel = tensor.numel()

            sample_shape = [max(1, int(numel * 0.01))]
            sample_index = torch.empty(sample_shape).uniform_(0, numel).type(torch.long)
            sample_tensor = tensor[sample_index]

            k = max(1, int(numel * self.compress_ratio * 0.01))
            vals, indices = torch.topk(sample_tensor.abs(), k)

            thr = vals.min()
            mask = tensor.abs() >= thr
            selected = mask.sum()

            for _ in range(10):
                if selected > 1.3 * numel * self.compress_ratio:
                    thr = 1.3 * thr
                elif selected < 0.7 * numel * self.compress_ratio:
                    thr = 0.7 * thr
                else:
                    break
                mask = tensor.abs() >= thr
                selected = mask.sum()

            indices, = torch.where(mask)
            values = tensor[indices]

            tensor_compressed = values, indices
            ctx = shape, mask, numel

            compressed_mem.append((tensor_compressed, ctx))
        return compressed_mem

    def decompress(self, new_mem, ctx):
        decompressed_mem = []
        for i in new_mem:
            values, indices = i
            shape, _, numel = ctx
            tensor_decompressed = torch.zeros(numel, dtype=values.dtype, layout=values.layout, device=values.device)
            tensor_decompressed.scatter_(0, indices, values)
            decompressed_mem.append(tensor_decompressed.view(shape))
        return decompressed_mem
