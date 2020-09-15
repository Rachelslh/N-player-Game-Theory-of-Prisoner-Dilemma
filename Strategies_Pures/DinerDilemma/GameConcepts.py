from Strategies_Pures.DinerDilemma.Utility import Utility, GameSettings
from Strategies_Pures.DinerDilemma.Strategy import Strategy
import numpy as np


class GameConcepts:
    utility = None
    gs = None
    df = []
    allPlayers = []
    nash = []

    def __init__(self, gs) -> None:
        super().__init__()
        if gs is not None:
            self.gs = gs
            self.utility = Utility(gs)
            self.utility.calculate_utility()
            self.df = self.utility.df
            for i in range(gs.N):
                print("Player ", i)
                gs.players[i].generate_payoff_matrix(gs.N, self.df)
            self.all_players()

    def dominant_strategy(self):
        diff = self.df.diff(periods=1)
        diff = diff.dropna()
        print(diff)
        dominantStrat = (diff < 0).all()

        if sum(dominantStrat) > 0:
            diff = self.df.diff(periods=-1)
            diff = diff.dropna()
            dominantStrat = (diff > 0).all()
            if sum(dominantStrat) == diff.shape[1]:
                return Strategy.STRICTLY_DOMINANT_CHEAP

            return Strategy.LAX_DOMINANT_CHEAP
        else:
            dominantStrat = (diff > 0).all()
            if sum(dominantStrat) == diff.shape[1]:
                return Strategy.STRICTLY_DOMINANT_EXPENSIVE

            return Strategy.LAX_DOMINANT_EXPENSIVE

    def all_players(self):
        df = self.gs.players[0].df
        array = np.empty((self.gs.N, df.shape[0], df.shape[1]))
        for i in range(self.gs.N):
            array[i, :, :] = self.gs.players[i].df

        self.allPlayers = array

    def elimination_dominant_strategy(self):
        strategy = self.dominant_strategy()
        indices = []
        if strategy == Strategy.STRICTLY_DOMINANT_CHEAP:
            indices = np.where(self.allPlayers == self.utility.df.iloc[0, 0])
        elif strategy == Strategy.STRICTLY_DOMINANT_EXPENSIVE:
            indices = np.where(self.allPlayers == self.utility.df.iloc[self.utility.df.shape[0] - 1,
                                                                       self.utility.df.shape[1] - 1])

        return indices[1][0], indices[2][0]

    def best_response(self):
        return self.df.max(axis=0).drop_duplicates()

    def find_nash_equilibrium(self):
        values = self.best_response()
        df = self.gs.players[0].df
        array = self.allPlayers

        nash = []
        for value in values:
            indices = np.where(df == value)
            print(value)
            print('indices : ', indices)
            for i in range(np.size(indices[0])):
                print('in : ', np.where(array[:, indices[0][i], indices[1][i]] == value))
                if len(np.where(array[:, indices[0][i], indices[1][i]] == value)[0]) == self.gs.N:
                    print("Nash Equilibrium is ", array[:, indices[0][i], indices[1][i]])
                    nash.append((indices[0][i], indices[1][i]))

        self.nash = nash
        print(nash)
        return nash

    def find_pareto_optimum(self):
        array = self.allPlayers
        for i in self.nash:
            value = array[0, i[0], i[1]]
            indices = np.where(array[0, :, :] > value)
            pareto = [array[:, indices[0][x], indices[1][x]] for x in range(np.size(indices[0]))
                      if np.all(array[:, indices[0][x], indices[1][x]] > value)]

            if len(pareto) > 0 and not (np.diff(np.vstack(pareto).reshape(len(pareto), -1), axis=0) > 0).all():
                return [(indices[0][x], indices[1][x]) for x in range(np.size(indices[0]))
                        if np.all(array[:, indices[0][x], indices[1][x]] == pareto[0])]

        return self.nash

    def find_security_level_strategy(self):
        df = self.df
        security = []

        for strategy in range(df.shape[0]):
            security.append(np.min(df.iloc[strategy]))

        return security

    def find_security_level_player(self):
        security = self.find_security_level_strategy()
        return np.max(security)


gs = GameSettings(3, 10, 7, 9, 1)
g = GameConcepts(gs)
print(g.dominant_strategy())
print(g.elimination_dominant_strategy())
for i in range(gs.N):
    print("Player ", i)
    gs.players[i].generate_payoff_matrix(gs.N, g.df)
g.find_nash_equilibrium()
print('Pareto Optimum is at : ', g.find_pareto_optimum())
print("Security level of both strategies: ", g.find_security_level_strategy())
print("Security level of each player: ", g.find_security_level_player())
