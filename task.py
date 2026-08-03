### [学生练习 1] PyTorch 张量操作与简单网络搭建
# [PyTorch 简介 | 菜鸟教程](https://www.runoob.com/pytorch/pytorch-intro.html)

# **练习目标:** 掌握 PyTorch 核心 API，能够独立完成 "数据构建 -> 模型定义 -> 训练循环" 的全流程。

# **任务说明:**

# 1. **数据准备**: 使用 `torch.randn` 生成 1000 个样本的二维特征 $X$ (shape: 1000x2)，真实标签 $Y = 3X_1 - 2X_2 + 1 + \epsilon$ ($\epsilon$ 为极小噪声，可以用 `torch.randn` 生成)。
# 2. **数据加载**: 使用 `TensorDataset` 和 `DataLoader` 将数据按 `batch_size=32` 进行封装。
# 3. **模型搭建**: 继承 `nn.Module`，定义一个包含单层 `nn.Linear` 的线性回归模型。
# 4. **训练循环**: 选择 `SGD` 优化器和 `MSELoss`，编写完整的训练循环，训练 20 个 epoch，并打印每轮的 Loss。最后检查模型学习到的权重是否接近真实值 (3, -2) 和偏置 1。

# ```python
# 学生代码框架提示
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

def demo_linear_regression():
    print("\n" + "=" * 50)
    print("线性回归完整训练流程")
    print("=" * 50)
    torch.manual_seed(42)
    
    # 1. 生成数据集
    X = torch.randn(1000, 2)
    x1 = X[:, 0]
    x2 = X[:, 1]
    epsilon = torch.randn_like(x1) * 0.01
    Y = 3 * x1 - 2 * x2 + 1 + epsilon
    Y = Y.unsqueeze(1)
    
    # 2. 封装DataLoader
    dataset = TensorDataset(X, Y)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # 3. 定义线性回归模型
    class LinearRegression(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = nn.Linear(2, 1)
        def forward(self, x):
            return self.linear(x)
    model = LinearRegression()

    # 4. 损失函数、优化器配置
    criterion = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    total_epochs = 20
    print(f"训练轮数: {total_epochs}, batch_size=32")
    print("-" * 40)

    # 训练循环
    for epoch in range(total_epochs):
        model.train()
        epoch_total_loss = 0.0
        for batch_x, batch_y in dataloader:
            pred = model(batch_x)
            loss = criterion(pred, batch_y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_total_loss += loss.item() * batch_x.shape[0]
        avg_loss = epoch_total_loss / len(dataset)
        print(f"第 {epoch+1:2d} / {total_epochs} Epoch，本轮平均Loss：{avg_loss:.6f}")
    
    # 输出模型学习参数
    print("-" * 40)
    weight = model.linear.weight.detach()
    bias = model.linear.bias.detach()
    w1 = weight[0][0].item()
    w2 = weight[0][1].item()
    b = bias.item()
    print(f"真实参数：w1=3.0, w2=-2.0, bias=1.0")
    print(f"训练得到：w1={w1:.4f}, w2={w2:.4f}, bias={b:.4f}")
    return model

if __name__ == '__main__':
    print("PyTorch版本:", torch.__version__)
    print("是否可用GPU:", torch.cuda.is_available())
    model = demo_linear_regression()
    print("线性回归训练完成!")