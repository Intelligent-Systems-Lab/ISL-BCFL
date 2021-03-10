import torch



class DGCCompressor():
    def __init__(self,
                compress_ratio, 
                memory=None,
                sample_ratio=0.01, 
                strided_sample=True,
                compress_upper_bound=1.3,
                compress_lower_bound=0.8,
                max_adaptation_iters=10,
                resample=True,
                fp16_values=False,
                int32_indices=False,
                warmup_epochs=-1, 
                warmup_coeff=None):
            pass
        def initialize(self):
            pass

        def update_warmup_compress_ratio(self, epoch):
            pass

        def sparse_filter(self):
            pass

        pass