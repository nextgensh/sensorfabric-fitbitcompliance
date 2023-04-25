#!/usr/bin/env python3

from dash import Dash, html, dcc

def Error(message):
    """
    Render loading view, to let the user know that the dashboard is loading.
    """

    return html.Div(children=[
        html.Center(children=[
            html.Img(src='assets/ohno.png'),
            html.H1(message)
        ])
    ])
