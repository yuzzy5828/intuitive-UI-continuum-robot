# 実機のrhoとphiを予測するように学習する
# 正則化項をつけて学習

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch as t
import torch.nn as nn
import torch.optim as optim

class RealToSim(nn.Module):
    def __init__(self):
        super(RealToSim, self).__init__()

        self.hyperparameters = hyperparameters
        self.hidden_layers_size = hyperparameters["hidden_layers_size"]
        self.activation = hyperparameters["activation"]
        self.input_dim = hyperparameters["input_dim"]
        self.output_dim = hyperparameters["output_dim"]

        self.n_dense_layers = len(self.hidden_layers_size)

        self.layers = nn.ModuleList()

        # layerをつけていく
        layer = nn.Flatten()
        self.layers.append(layer)

        in_size_flatten = np.prod(self.input_dim)

        layers_dimensions = [in_size_flatten]
        layers_dimensions.extend(self.hidden_layers_size)

        for i in range(len(layers_dimensions) - 1):

          layer = nn.Linear(layers_dimensions[i], layers_dimensions[i + 1])

          if self.activation == "relu":
            activation = nn.ReLU()
          else:
            activation = None

          self.layers.append(layer)
          self.layers.append(activation)

        layer = nn.Linear(layers_dimensions[-1], self.output_dim)
        self.layers.append(layer)

        self.classifier = nn.Sequential(*self.layers)

    def forward(self, x):
        y_pred = self.classifier(x)
        return y_pred

class ScopeClassifier:
    def __init__(self, model, hyperparameters):
        self.hyperparameters = hyperparameters
        self.optimizer = optim.SGD(model.parameters(), lr=self.hyperparameters["learning_rate"])
        self.criterion = nn.MSELoss()
        
def main():
    # dataset読み込み
    x_train = 
    y_train = 
    x_valid = 
    y_valid = 

    # NN用のパラメタ定義
    hyperparameters = dict(input_dim=2,
                        output_dim=4,
                        hidden_layers_size=[10, 10],
                        actication="linear",
                        learning_rate=0.05,
                        max_epoch=100)
    
    device = t.device("cuda" if t.cuda.is_available() else "cpu")
    model = RealToSim(hyperparameters).to(device)
    scope = ScopeClassifier(model, hyperparameters)

    # train
    for epoch in range(hyperparameters["max_epoch"]):
        
        model.train()

        n_batch = len(x_train)

        for n in range(n_batch):
            x = x_train[n].to(device)
            y = y_train[n].to(device)

            # forward pass
            y_pred = model(x)
            loss = scope.criterion(y_pred, y)

            # backward and optimize
            scope.optimizer.zero_grad()
            loss.backward()
            scope.optimizer.step()

        

if __name__ == "__main__":
    main()