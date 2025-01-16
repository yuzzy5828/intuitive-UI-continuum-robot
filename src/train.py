import time
import numpy as np
import matplotlib.pyplot as plt
import serial
import cv2

import torch as t
import torch.nn as nn
import torch.optim as optim

from src.main import Model, SerialBridge
from src.utils import cal_current_degree

L = 60
d = 35

# NN用のパラメタ定義
hyperparameters = dict(input_dim=2,
                        output_dim=4,
                        hidden_layers_size=[10, 10],
                        actication="linear",
                        learning_rate=0.05,
                        max_epoch=100)
    
# train用のクラス
class Train():
    def __init__(self, hyperparameters):
        super().__init__()

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
    device = t.device("cuda" if t.cuda.is_available() else "cpu")
    model = Model()
    network = Train(hyperparameters).to(device)
    scope = ScopeClassifier(network, hyperparameters)
    serial = SerialBridge(in_port='/dev/ttyACM0', out_port='/dev/ttyACM1', baudrate=9600)

    cap = cv2.VideoCapture(0)

    # 初期状態のロボットの状態を保存
    image_init = cap.read()[1]

    # 角度の分解能
    num = 100

    for epoch in range(hyperparameters["max_epoch"]):
        
        for n in range(num):
            rho_ref = 3.0 # 仮の値
            phi_ref = 2 * np.pi * n / num

            h_ref = rho_ref * (1 - np.cos(L / rho_ref))
            
            delta_l_model = model.cal_delta_l(rho_ref, phi_ref)
            delta_l_nn = network.forward(rho_ref, phi_ref)
            delta_l = delta_l_model + delta_l_nn

            serial.send(delta_l)

            # 画像処理をして現在の角度を取得
            _, image = cap.read()
            h_current, phi_current = cal_current_degree(image, image_init)
            
            current = t.tensor([h_current, phi_current]).to(device)
            ref = t.tensor(h_ref, phi_ref).to(device)

            # 誤差から重みを更新
            scope.optimizer.zero_grad()
            loss = scope.criterion(current, ref) 
            loss.backward()
            scope.optimizer.step()

if __name__ == "__main__":
    main()