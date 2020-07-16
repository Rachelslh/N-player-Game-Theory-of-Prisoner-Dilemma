import itertools
import numpy as np
import pandas as pd

from Strategies_Pures.DinerDilemma.Strategy import Strategy
from Strategies_Pures.DinerDilemma.Player import Player


class Utility:
    df = []
    gs = None

    def __init__(self, gs) -> None:
        super().__init__()
        self.gs = gs

    def calculate_others_utility(self):
        data = np.zeros((1, pow(2, self.gs.N - 1)))
        allOtherPlayers = [self.gs.players[i - 1].identifier for i in range(1, self.gs.N + 1)
                           if self.gs.players[i - 1].identifier != 1]
        allPlayersStrat = list(itertools.product([0, 1], repeat=self.gs.N - 1))

        for i in range(len(allPlayersStrat)):
            for j in allOtherPlayers:
                if j * allPlayersStrat[i][j - 2] == j:
                    data[0][i] += self.gs.K
                else:
                    data[0][i] += self.gs.L

        self.df = pd.DataFrame([], index=[Strategy.CHEAP.value, Strategy.EXPENSIVE.value], columns=allPlayersStrat)

        return data

    def calculate_utility(self):
        print('Generating Player 1\'s Gain Matrix...')
        data = self.calculate_others_utility()

        self.df.iloc[0] = np.round(self.gs.B - (data + self.gs.L) / self.gs.N, 2)
        self.df.iloc[1] = np.round(self.gs.A - (data + self.gs.K) / self.gs.N, 2)

        print('Each Player\'s Gain Matrix Generated.')
        print(self.df)


class GameSettings(object):
    players = []
    N = A = B = K = L = 0

    def __init__(self, N, A, B, K, L) -> None:
        super().__init__()
        self.N = N
        self.A = A
        self.B = B
        self.K = K
        self.L = L
        self.players = [Player(self, i) for i in range(1, N + 1)]
