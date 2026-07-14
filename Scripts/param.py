import torch

class Param:
    def __init__(self,shape,random=True):
        device = "cuda" if torch.cuda.is_available() else "cpu"

        if random:
            self.value = torch.randn(shape,device=device) * 0.01
        else:
            self.value = torch.zeros(shape,device=device)

        self.grad = None
        self.t = 0
        self.m = torch.zeros(shape,device=device)
        self.v = torch.zeros(shape,device=device)

    def step(self,beta1=0.9,beta2=0.99,eps=1e-8,decay_rate=0.01,lr = 3e-4):
        self.t += 1

        self.m = beta1 * self.m + (1 - beta1) * self.grad
        self.v = beta2 * self.v + (1 - beta2) * self.grad ** 2

        m_hat = self.m / (1 - beta1 ** self.t)
        v_hat = self.v / (1 - beta2 ** self.t)

        adam_update = m_hat / (torch.sqrt(v_hat) + eps)

        self.value = self.value - lr * adam_update - decay_rate * lr * self.value

    def zero_grad(self):
        self.grad = None
