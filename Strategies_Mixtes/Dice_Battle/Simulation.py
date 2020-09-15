import dash
import dash_core_components as dcc
import dash_html_components as html
import os
import pandas as pd
import numpy as np
from PIL import Image
from random import randint
from dash.dependencies import Input, Output

slices = []
data = {}
score1, score2 = 0, 0
d1, d2 = 0, 0
N, D = 100, 10
endGame = False

app = dash.Dash(__name__)


def generateColspans():
    return html.Tr([html.Th(colSpan=1),
                    html.Th('Player', scope='col'),
                    html.Th('System', scope='col')])


def generateRowspans(pt1, pt2):
    global d1, d2, score1, score2, N, slices, endGame
    li = []
    if d1 > 0 and d2 > 0 and not endGame:
        d = min(d1, d2)
        for i in range(1, d + 1):
            subList = [html.Th(scope='row'),
                       html.Td(html.Img(src=slices[pt1[i] - 1], width=80, height=80)),
                       html.Td(html.Img(src=slices[pt2[i] - 1], width=80, height=80))]  # player1 & player2
            li.append(html.Tr(subList))
        if d1 < d2:
            for i in range(d + 1, d2 + 1):
                subList = [html.Th(scope='row'),
                           html.Td(''),
                           html.Td(html.Img(src=slices[pt2[i] - 1], width=80, height=80))]
                li.append(html.Tr(subList))
        elif d2 < d1:
            for i in range(d + 1, d1 + 1):
                subList = [html.Th(scope='row'),
                           html.Td(html.Img(src=slices[pt1[i] - 1], width=80, height=80)),
                           html.Td('')]
                li.append(html.Tr(subList))

        subList = [html.Th('Thrown Dices', scope='row', style={'font-size': 'x-large'}),
                   html.Td(d1, style={'font-size': 'x-large'}),
                   html.Td(d2, style={'font-size': 'x-large'})]  # score1 & score2
        li.append(html.Tr(subList))

        subList = [html.Th('Score', scope='row', style={'font-size': 'x-large'}),
                   html.Td(sum(pt1.values()), style={'font-size': 'x-large'}),
                   html.Td(sum(pt2.values()), style={'font-size': 'x-large'})]  # score1 & score2
        li.append(html.Tr(subList))

        if score1 > N or score2 > N:
            endGame = True

    subList = [html.Th('Collected Points', scope='row', style={'font-size': 'x-large'}),
               html.Td(score1, style={'font-size': 'x-large'}),
               html.Td(score2, style={'font-size': 'x-large'})]  # score1 & score2
    li.append(html.Tr(subList))

    return li


def throwOptimal():
    global D, score1, score2, data
    P = data[(str(score2), str(score1))]  # player & system
    P_Sum = np.zeros(D)
    r = np.random.rand()
    print(P)
    for i in P:
        j = int(i)
        if j == 0:
            P_Sum[j] = float(P[i])
        else:
            P_Sum[j] = P_Sum[j - 1] + int(P[i])
    print(P_Sum)
    for i in range(D):
        if r <= P_Sum[i]:
            return i + 1
    return D


app.layout = html.Div(
    children=[
        html.H1(children='Dice Battle'),
        html.Img(src=app.get_asset_url('diceFront.png'), className='center'),
        html.Pre('Let\'s see who reaches 100 points first !!'),
        html.Pre('Choose how many dices you wanna throw'),
        dcc.Slider(
            id='dice-number',
            min=1,
            max=10,
            step=1,
            marks={i: {'label': str(i), 'style': {'color': '#fff', 'font-size': 'x-large'}} for i in range(1, 11)},
            value=0,
            className='slider'
        ),
        html.Div(id='table'),
        html.Br(),
        html.Div(id='win'),
        html.Br(),
        html.Button('New Game ?', style={"margin-left": "10px"}, id='play', n_clicks=0),
    ])


@app.callback(
    [Output('table', 'children'),
     Output('win', 'children')],
    [Input('dice-number', 'value')]
)
def gameEngine(d):
    global N, d1, d2, score1, score2, slices, endGame

    if len(slices) == 0:
        loadSlices()
        loadData()

    elif d is not None and d > 0 and not endGame:
        d1 = d
        d2 = throwOptimal()
        pt1, pt2 = {}, {}
        for i in range(1, d1 + 1):
            pt1[i] = randint(1, 6)
        for i in range(1, d2 + 1):
            pt2[i] = randint(1, 6)
        print(pt1, pt2)
        score1 += sum(pt1.values())
        score2 += sum(pt2.values())

        if score1 > N or score2 > N:
            if score1 == score2:
                return html.Table([html.Thead(generateColspans()), html.Tbody(generateRowspans(pt1, pt2))]), \
                       html.Pre('You Are Tied !')
            if score1 > score2:
                return html.Table([html.Thead(generateColspans()), html.Tbody(generateRowspans(pt1, pt2))]), \
                   html.Pre('You Won ! Good Job')
            if score2 > score1:
                return html.Table([html.Thead(generateColspans()), html.Tbody(generateRowspans(pt1, pt2))]), \
                       html.Pre('You Lost, What a Bummer!')

        return html.Table([html.Thead(generateColspans()), html.Tbody(generateRowspans(pt1, pt2))]), html.Pre()

    return html.Table([html.Thead(generateColspans()), html.Tbody(generateRowspans([], []))]), html.Pre()


@app.callback(
    Output('dice-number', 'value'),
    [Input('play', 'n_clicks')]
)
def resetGame(n_clicks):
    global score1, score2, d1, d2, endGame

    score1, score2, d1, d2 = 0, 0, 0, 0
    endGame = False
    print('Game Reset.')
    return 0


# used this initially to crop the Image into 6 blocks and load em into a global table
def cropImg():
    print('Treating Resources...')
    path = 'assets/'
    k = 1
    im = Image.open(app.get_asset_url('dice.png'))
    imgWidth, imgHeight = im.size
    height = int(imgHeight / 2)
    width = int(imgWidth / 3)
    for i in range(0, imgHeight, height):
        for j in range(0, imgWidth, width):
            box = (j, i, j + width, i + height)
            img = im.crop(box)
            img.save(os.path.join(path, 'slice_' + str(k) + '.png'))
            k += 1

    print('All Resources Treated.')


def loadSlices():
    global slices
    print('Loading Resources...')
    for i in range(1, 7):
        url = app.get_asset_url('slice_' + str(i) + '.png')
        slices.append(url)
    print('All Resources Loaded.')


def loadData():
    global data
    print('Loading Calculated Optimal Strategies Data...')
    temp = pd.read_html('Strat_IJ.html')
    data = pd.DataFrame.to_dict(temp[0].iloc[:, 1:])
    print('Optimal Strategies Data Loaded.')


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

# cropImg()
