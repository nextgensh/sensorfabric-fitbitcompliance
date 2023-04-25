#!/usr/bin/env python3

from dash import Dash, html, dcc
import random

def Loading(message):
    """
    Render loading view, to let the user know that the dashboard is loading.
    """

    return html.Div(children=[
        html.Center(children=[
            html.Img(src='assets/loading{}.png'.format(int((random.random()*10)%3)+1)),
            html.H1(message),
        ])
    ])
