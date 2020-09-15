from typing import Any
from Strategies_Mixtes.Dice_Battle.OptimalStrategies import solve_linear_pl1, find_pure_strategy
import numpy as np
import pandas as pd
import time


class Utility:
    D = 10
    N = 100
    data = []
    probTable = None
    EG = None
    E_ij = {}
    strat_ij = {}

    # Memoization
    memoQ = {}
    memoE = {}

    def __new__(cls) -> Any:
        instance = super().__new__(cls)
        return instance

    '''
        General Part : Probability
    '''

    def calculate_q(self, d, k):
        if (d, k) in self.memoQ:
            return self.memoQ[(d, k)]
        if d == 1 and 2 <= k <= 6:
            return 1 / 5

        elif d >= 1 and 2 * d <= k <= 6 * d:
            val = sum([self.calculate_q(d - 1, k - 2),
                       self.calculate_q(d - 1, k - 3),
                       self.calculate_q(d - 1, k - 4),
                       self.calculate_q(d - 1, k - 5),
                       self.calculate_q(d - 1, k - 6)]) / 5
            self.memoQ[(d, k)] = val
            return val

        return 0

    def calculate_prob(self, d, k):
        if k == 1:
            return 1 - pow((5 / 6), d)
        elif 2 <= k <= 2 * d - 1 or k > 6 * d:
            return 0
        else:
            return pow((5 / 6), d) * self.calculate_q(d, k)

    def generate_prob_table(self, D, K):
        dict_prob = np.zeros((D + 1, K + 1), dtype=np.float64)
        # useless
        dict_prob[0, 0] = 1
        for i in range(1, D + 1):
            for j in range(1, K + 1):
                dict_prob[i, j] = self.calculate_prob(i, j)

        '''
        df = pd.DataFrame(dict_prob)
        print('Generating HTML Probability Table...')
        f = open("table.html", "w")
        f.write(df.to_html())
        print('HTML Probability Table Generated.')
        '''

        return dict_prob

    '''
        First Part : One Tour Game
    '''

    def calculate_EG_d1_d2(self, d1, d2):
        p1 = 0
        p2 = 0

        print('Calculating Gain For Case (', d1, ',', d2, ')...')
        for i in range(1, 6 * d1 + 1):
            for j in range(1, 6 * d2 + 1):
                if j < i:
                    p1 += self.probTable[d1, i] * self.probTable[d2, j]
                elif j > i:
                    p2 += self.probTable[d1, i] * self.probTable[d2, j]

        print('Gain For Case (', d1, ',', d2, ') Estimated With ', p1 - p2)
        return round(p1 - p2, 5)

    def generate_EG(self):
        print('Generating Probability Table...')
        self.probTable = self.generate_prob_table(self.D, 6 * self.D)
        print('Probability Table Generated.')

        for i in range(self.D + 1):
            data = []
            for j in range(self.D + 1):
                data.append(self.calculate_EG_d1_d2(i, j))
            self.data.append(data)

        print('Generating Gain Matrix...')
        arr = np.array(self.data)
        print('Gain Matrix Generated.')
        print(arr)

        return arr

    '''
        Second Part : Repetitive Game
    '''

    def init_EG(self):
        D = self.D
        N = self.N
        EG = np.zeros((N + 6 * D, N + 6 * D), dtype=np.float64)
        print('Generating Probability Table...')
        U.probTable = U.generate_prob_table(D, N + 6 * D)
        print('Probability Table Generated.')

        for i in range(N, N + 6 * D):
            for a in range(0, N):
                EG[i, a] = 1
                EG[a, i] = -1
        for i in range(N, N + 6 * D):
            for j in range(N, N + 6 * D):
                if i > j:
                    EG[i, j] = 1
                    EG[j, i] = -1
                elif j > i:
                    EG[j, i] = 1
                    EG[i, j] = -1
                else:
                    EG[i, j] = 0

        return EG

    def calculate_E_ij_d1_d2(self, d1, d2, i, j):
        N = self.N

        if (i, j, d1, d2) in self.memoE.keys():
            return self.memoE[(i, j, d1, d2)]
        if i >= N or j >= N:
            return self.EG[i, j]

        if i < N and j < N:
            P1 = 0
            P2 = 0
            P3 = 0
            # Chances that score 1 might be bigger than the objective N and score 2
            for k in range(N - i, N + 6 * d1):
                for l in range(1, k):
                    if k <= 6 * d1 and l <= 6 * d2:
                        P1 += self.probTable[d1, k] * self.probTable[d2, l]

            # Chances that score 2 might be bigger than the objective N and score 1
            for k in range(N - j, N + 6 * d2):
                for l in range(1, k):
                    if k <= 6 * d2 and l <= 6 * d1:
                        P2 += self.probTable[d1, l] * self.probTable[d2, k]

            # Chances that score 1 and score 2 are smaller then the objective SO we attach the next tour's gain
            for k in range(1, N - i):
                for l in range(1, N - j):
                    if k <= 6 * d1 and l <= 6 * d2:
                        P3 += self.probTable[d1, k] * self.probTable[d2, l] + \
                              self.calculate_EG_k_l(i + k, j + l)

            val = P1 - P2 + P3
            self.memoE[(i, j, d1, d2)] = val
            return val

    def calculate_EG_k_l(self, k, l):
        N = self.N

        if k >= N or l >= N:
            return self.EG[k, l]
        if (k, l) in self.E_ij.keys():
            return self.EG[k, l]

        self.calculate_E_ij(k, l)
        # print('state [' + str(k) + ', ' + str(l) + '] len dict ' + str(len(self.E_ij)))
        x, y = solve_linear_pl1(self.E_ij[(k, l)])
        self.EG[k, l] = x
        self.strat_ij[(k, l)] = y[1:]

        return self.EG[k, l]

    def calculate_E_ij(self, i, j):

        E = np.zeros((self.D + 1, self.D + 1), dtype=np.float64)
        for d1 in range(1, self.D + 1):
            for d2 in range(1, self.D + 1):
                E[d1, d2] = self.calculate_E_ij_d1_d2(d1, d2, i, j)

        self.E_ij[(i, j)] = E

    def generate_full_EG(self):
        self.EG = self.init_EG()
        self.calculate_EG_k_l(0, 0)


U = Utility()

# FIRST PART

# gainM = U.generate_EG()
# p = solve_linear_pl1(gainM)
# print(p)
# print(find_pure_strategy(p, gainM))

# SECOND PART

startTime = time.time()
U.generate_full_EG()
print('Execution Time ' + str((time.time() - startTime)) + ' seconds')
df = pd.DataFrame(U.strat_ij)
print('Generating HTML Strategies Table...')
f = open("Strat_IJ.html", "w")
f.write(df.to_html())
print('HTML Strategies Table Generated.')
