from Strategies_Pures.DinerDilemma.GameConcepts import GameConcepts
from Strategies_Pures.DinerDilemma.Utility import GameSettings
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from Strategies_Pures.DinerDilemma.Strategy import Strategy

gs = GameSettings(2, 10, 7, 9, 1)
g = GameConcepts(gs)


def data(g):
    array = g.allPlayers
    globalData = list()
    for i in range(array.shape[1]):
        globalData.append([])
        for j in range(array.shape[2]):
            li = array[:, i, j].tolist()
            globalData[i].append(html.Td('(' + ', '.join(str(item) for item in li) + ')'))

    return globalData


def generate_colspans(N, impair, c, count, li):
    subList1 = []
    subList2 = []
    if N == 2:
        subList1.append(html.Th('', colSpan=str(impair * 2), scope='colgroup'))
        subList2.append(html.Th('', scope='col', colSpan=str(impair * 2)))
        for i in range(int(c / 2)):
            subList1.append(html.Th('Joueur 2', colSpan=2, scope='colgroup', className='borderLeft'))
            subList2.append(html.Th('Pas Cher', scope='col', className='borderLeft'))
            subList2.append(html.Th('Cher', scope='col', className='borderLeft'))
        li.append(html.Tr(subList1))
        li.append(html.Tr(subList2))
        return li

    else:
        subList1.append(html.Th('', colSpan=str(impair * 2), scope='colgroup'))
        subList2.append(html.Th('', colSpan=str(impair * 2), scope='colgroup'))
        for i in range(int(c / count)):
            subList1.append(html.Th('Joueur ' + str(N), colSpan=count, scope='colgroup', className='borderLeft'))
            subList2.append(html.Th('Pas Cher', colSpan=int(count / 2), scope='colgroup', className='borderLeft'))
            subList2.append(html.Th('Cher', colSpan=int(count / 2), scope='colgroup', className='borderLeft'))
        li.append(html.Tr(subList1))
        li.append(html.Tr(subList2))
        return generate_colspans(N - 2, impair, c, count / 2, li)


def generate_rowspans(N, l, g, count, li):
    if count == l * 2:
        for i in range(len(li)):
            li[i].reverse()
            li[i] = html.Tr(li[i])
        return li
    elif N == 1:
        allData = data(g)
        for i in range(int(l / count)):
            allData[2 * i].reverse()
            subList = allData[2 * i] + [html.Th('Pas Cher', scope='row', className='borderTop'),
                                        html.Th('Joueur 1', rowSpan=2, scope='rowgroup', className='borderTop')]
            li.append(subList)
            allData[2 * i + 1].reverse()
            subList = allData[2 * i + 1] + [html.Th('Cher', scope='row', className='borderTop')]
            li.append(subList)

        return generate_rowspans(N + 1, l, g, count * 2, li)

    else:
        cheap = True
        for i in range(0, len(li), int(count / 2)):

            if cheap:
                li[i].append(html.Th('Pas Cher', rowSpan=int(count / 2), scope='rowgroup', className='borderTop'))
                cheap = False
            else:
                li[i].append(html.Th('Cher', rowSpan=int(count / 2), scope='rowgroup', className='borderTop'))
                cheap = True

            if i == 0 or i % count == 0:
                li[i].append(
                    html.Th('Joueur ' + str(2 * N - 1), rowSpan=count, scope='rowgroup', className='borderTop'))

        return generate_rowspans(N + 1, l, g, count * 2, li)


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1(children='Dilemme du Dîner'),
        'Le dilemme sans scrupule du dîner est un dilemme à n-player.'
        ' La situation imaginée est que plusieurs personnes vont manger et, avant de commander, '
        'elles acceptent de partager les coûts à parts égales. Chaque convive doit maintenant choisir de '
        'commander le plat coûteux ou bon marché. Il est présupposé que le plat le plus coûteux est meilleur que '
        'le moins cher, mais pas assez pour justifier de payer la différence lorsque vous mangez seul. '
        'Chaque convive justifie le fait que, en commandant le plat plus onéreux, le coût supplémentaire de '
        'leur note sera minime et que, par conséquent, le meilleur dîner en vaut la peine.',
        html.H2(children='Matrice de Gain'),
        html.Label('Choisissez le nombre de joueurs'),
        dcc.Slider(
            id='player-number',
            min=2,
            max=10,
            marks={i: {'label': str(i), 'style': {'color': '#fff', 'font-size': 'x-large'}} for i in range(2, 11)},
            value=2,
            className='slider'
        ),
        html.Div(id='matrix'),
        html.Br(),
        html.Label('Vous voulez découvrir les fameuses notions théoriques des jeux ?'),
        html.Button('Allons-y !', style={"margin-left": "10px"}, id='concepts', n_clicks=0),
        html.Br(),
        html.Pre('- Stratégie strictement dominante ou faiblement dominante ?'),
        html.Pre(id='dominantOutput', style={"margin-left": "40px"}),
        html.Pre('- L\'issue du jeu par élimination des stratégies faiblement où fortement dominées ?!'),
        html.Pre(id='eliminationOutput', style={"margin-left": "40px"}),
        html.Pre('- Equilibre de Nash ?'),
        html.Pre(id='nashOutput', style={"margin-left": "40px"}),
        html.Pre('- Optimum de Pareto ?'),
        html.Pre(id='paretoOutput', style={"margin-left": "40px"}),
        html.Pre('- Niveau de sécurité de chaque stratégie ?'),
        html.Pre(id='securityStratOutput', style={"margin-left": "40px"}),
        html.Pre('- Niveau de sécurité d\'un joueur ?'),
        html.Pre(id='securityPlayerOutput', style={"margin-left": "40px"}),
    ])


@app.callback(
    Output('matrix', 'children'),
    [Input('player-number', 'value')]
)
def generate_table(N):
    global gs, g
    gs = GameSettings(N, 10, 7, 9, 4)
    g = GameConcepts(gs)

    for i in range(gs.N):
        print("Player ", i)
        gs.players[i].generate_payoff_matrix(gs.N, g.df)

    l = g.allPlayers.shape[1]
    c = g.allPlayers.shape[2]

    if gs.N % 2 == 0:
        pair = gs.N
        impair = gs.N / 2
    else:
        pair = gs.N - 1
        impair = int(gs.N / 2) + 1

    return html.Table(
        [html.Thead(generate_colspans(pair, impair, c, c, [])),
         html.Tbody(generate_rowspans(1, l, g, 2, []))]
    )


@app.callback(
    [Output('dominantOutput', 'children'),
     Output('eliminationOutput', 'children'),
     Output('nashOutput', 'children'),
     Output('paretoOutput', 'children'),
     Output('securityStratOutput', 'children'),
     Output('securityPlayerOutput', 'children')],
    [Input('concepts', 'n_clicks')]
)
def printResults(n_clicks):
    global g
    if n_clicks >= 1:
        nash = 'Les équilibres de Nash sont : '
        for el in g.find_nash_equilibrium():
            nash += '     ' + str(g.allPlayers[:, el[0], el[1]]) + ' situé dans la case [ ' + str(el[0]) + ', ' \
                    + str(el[1]) + ' ]\n'

        issue = 'L\'issue du jeu par élimination est située dans la case : '
        issue += str(g.elimination_dominant_strategy())

        pareto = 'L\'optimum de Pareto est : '
        for el in g.find_pareto_optimum():
            pareto += '     ' + str(g.allPlayers[:, el[0], el[1]]) + ' situé dans la case [ ' + str(el[0]) + ', ' \
                      + str(el[1]) + ' ]\n'

        security = g.find_security_level_strategy()
        securityStart = 'Le niveau de sécurité de la stratégie "' + Strategy.CHEAP.value + '" est : ' \
                        + str(security[0]) + '\n'
        securityStart += 'Le niveau de sécurité de la stratégie "' + Strategy.EXPENSIVE.value + '" est : ' \
                         + str(security[1])

        securityPlayer = 'Le niveau de sécurité d\'un joueur est : ' + str(g.find_security_level_player())

    return g.dominant_strategy().value, issue, nash, pareto, securityStart, securityPlayer


# gs = GameSettings(4, 10, 7, 9, 1)
if __name__ == '__main__':
    app.run_server(debug=False)
