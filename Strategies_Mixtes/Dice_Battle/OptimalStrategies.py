import numpy as np
from gurobipy import *


# Player 2 knows Pl 1's prob vector, so here we look for Pl 2's optimal pure strategy
# in other words, we minimize his loss
def find_pure_strategy(P1, G):
    if G.shape and P1 is not None:
        G = G[1:, 1:]
        res = np.array([(G[:, j] * P1).sum() for j in range(0, G.shape[1])])
        print(res)
        return res.argmin() + 1


# Finding pl1's mixed strategy using MaxiMin
def solve_linear_pl1(G):
    variables_model = {}
    model = Model(name='Pl1_Prob')
    model.setParam(GRB.Param.OutputFlag, 0)
    variables_model['alpha'] = model.addVar(name='alpha', lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)

    G = G[1:, 1:]
    for i in range(G.shape[0]):
        variables_model[f'p_{i + 1}'] = model.addVar(name=f'p_{i + 1}', lb=0, ub=1, vtype=GRB.CONTINUOUS)

    for j in range(G.shape[1]):
        model.addConstr(variables_model['alpha'] <= np.array([(G[i, j] * variables_model[f'p_{i + 1}'])
                                                              for i in range(G.shape[0])]).sum())

    model.addConstr(np.array([variables_model[f'p_{i + 1}'] for i in range(G.shape[0])]).sum() == 1)

    # add the objective
    model.setObjective(variables_model['alpha'], sense=GRB.MAXIMIZE)
    # print(model)
    model.optimize()

    return model.getVarByName('alpha').x, [model.getVarByName(varName).x for varName in variables_model]
