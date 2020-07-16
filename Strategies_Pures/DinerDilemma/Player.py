import math
from typing import Any

import numpy as np


class Player:
    identifier = 0
    df = []

    def __new__(cls, gs, num) -> Any:
        instance = super().__new__(cls)
        instance.identifier = num
        return instance

    def __str__(self) -> str:
        return 'Player\'s Identifier = ' + self.identifier

    def generate_payoff_matrix(self, N, df):
        step = pow(2, self.identifier - 1)

        if N % 2 == 0:
            sizeElem = pow(2, N)
            data = np.zeros((int(math.sqrt(sizeElem)), int(math.sqrt(sizeElem))))
        else:
            sizeElem = pow(2, N - 1)
            data = np.zeros((2 * int(math.sqrt(sizeElem)), int(math.sqrt(sizeElem))))

        row = 0
        col = 0
        if step == 1:
            for i in range(0, df.shape[1], 2):
                if row == data.shape[0]:
                    row = 0
                    col += 2
                data[row:row + 2, col:col + 2] = df.iloc[:, i:i + 2]
                row += 2
        else:
            row = 0
            col = 0
            for i in range(0, df.shape[1], step):
                preI = i
                if row == data.shape[0]:
                    row = 0
                    col += 2
                if step == 2:
                    data[row:row + 2, col:col + 2] = df.iloc[:, i:i + 2].T
                    row += 2
                else:
                    n = 1
                    if int(step / (2 * data.shape[0])) > 1:
                        n = int(step / (2 * data.shape[0]))
                    newStep = int(step / n)
                    for j in range(n):
                        if row == data.shape[0]:
                            row = 0
                            col += 2
                        data[row:row + int(newStep / 2), col:col + 2] = \
                            np.reshape(np.split(df.iloc[0, i:i + newStep], 2), (int(newStep / 2), 2))
                        row += int(newStep / 2)
                        i += newStep

                    i = preI
                    for j in range(n):
                        if row == data.shape[0]:
                            row = 0
                            col += 2
                        data[row:row + int(newStep / 2), col:col + 2] = \
                            np.reshape(np.split(df.iloc[1, i:i + newStep], 2), (int(newStep / 2), 2))
                        row += int(newStep / 2)
                        i += newStep

        self.df = data
        print(data)
