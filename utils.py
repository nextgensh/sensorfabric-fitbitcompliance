#!/usr/bin/env python3
from dash import html, dash_table
import pandas as pd
import numpy

def dtrunc(num, d=1):
    num = str(num).split('.')
    if len(num) <= 1:
        return int(num[0])
    else:
        return float(num[0]) + float(num[1][:d]) / (10 ** d)

def formatName(name):
    words = name.split('_')
    str = ''
    for (i,w) in enumerate(words):
        str += ' ' if i > 0 else ''
        str += words[i][0].upper() + words[i][1:]

    return str

def createDataTable(frame):
    days_recorded = frame['days_recorded'].values
    calendar_days = frame['calendar_days'].values
    data_density = days_recorded / calendar_days
    for i in range(0, data_density.size):
        data_density[i] = dtrunc(data_density[i], d=2)
    frame['data_density'] = data_density

    # Sort the table by the data density metric.
    # The most compliant participants will show up at the top.
    frame = frame.sort_values(['data_density'], ascending=False)

    return html.Div([
        dash_table.DataTable(
            id='sleepTable',
            sort_action='native',
            filter_action='native',
            style_header={'font-weight':'bold'},
            columns=[
                {'name':formatName(i), 'id':i}
                for i in frame.columns
            ],
            data=frame.to_dict('records')
        )
    ])
