import os

class warmup:
    def __init__(self, max_lr=0.001, min_lr=0.0001, base_step=10, end_step=50):
        self.max_lr = max_lr
        self.min_lr = min_lr
        self.base_step = base_step
        self.end_step = end_step
    
    def get_lr_from_step(self, step):
        if step < self.base_step:
            return self.min_lr + step*(self.max_lr - self.min_lr)/self.base_step
        elif step == self.base_step:
            return self.max_lr
        elif step > self.base_step and step < self.end_step:
            return self.max_lr - step*(self.max_lr - self.min_lr)/self.end_step
        elif step >= self.end_step:
            return self.min_lr