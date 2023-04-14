#!/usr/bin/env python3
import pandas as pd
from utils import createDataTable
from dash import html, dcc, dash_table

def Overview(frameset):
    sleep = frameset['sleep']
    activity = frameset['activity']
    restinghr = frameset['restinghr']
    hrv = frameset['hrv']
    participants = frameset['participants']

    # Stores complete panda frames.
    metrics = [sleep, activity, restinghr, hrv]

    pids = participants['participantidentifier']
    # Holds the boolean values for each type.
    flags = [[], [], [], []]

    for pid in pids:
        # Check to see if it is there in each of the frame.
        for m in range(0, len(metrics)):
            participants = metrics[m]['participantidentifier'].values
            if pid in participants:
                val = 'Yes'
            else:
                val = 'No'
            temp = flags[m]
            temp += [val]
            flags[m] = temp

    frame = pd.DataFrame({
        'participantidentifier': pids,
        'sleep' : flags[0],
        'activity' : flags[1],
        'restinghr' : flags[2],
        'hrv' : flags[3]
    })

    return html.Div([
        dash_table.DataTable(
            id='sleepTable',
            columns=[
                {'name':i, 'id':i}
                for i in frame.columns
            ],
            data=frame.to_dict('records'),
            style_data_conditional = [
            {
                'if': {
                    'filter_query': '{sleep} = Yes', # comparing columns to each other
                    'column_id': 'sleep'
                },
                'backgroundColor': '#3D9970',
                'color': '#FFFFFF'
            },
            {
                'if': {
                    'filter_query': '{sleep} = No', # comparing columns to each other
                    'column_id': 'sleep'
                },
                'backgroundColor': 'tomato',
                'color': '#FFFFFF'
            },
            {
                'if': {
                    'filter_query': '{activity} = Yes', # comparing columns to each other
                    'column_id': 'activity'
                },
                'backgroundColor': '#3D9970',
                'color': '#FFFFFF'
            },
            {
                'if': {
                    'filter_query': '{activity} = No', # comparing columns to each other
                    'column_id': 'activity'
                },
                'backgroundColor': 'tomato',
                'color': '#FFFFFF'
            },
             {
                'if': {
                    'filter_query': '{restinghr} = Yes', # comparing columns to each other
                    'column_id': 'restinghr'
                },
                'backgroundColor': '#3D9970',
                'color': '#FFFFFF'
            },
            {
                'if': {
                    'filter_query': '{restinghr} = No', # comparing columns to each other
                    'column_id': 'restinghr'
                },
                'backgroundColor': 'tomato',
                'color': '#FFFFFF'
            },
             {
                'if': {
                    'filter_query': '{hrv} = Yes', # comparing columns to each other
                    'column_id': 'hrv'
                },
                'backgroundColor': '#3D9970',
                'color': '#FFFFFF'
            },
            {
                'if': {
                    'filter_query': '{hrv} = No', # comparing columns to each other
                    'column_id': 'hrv'
                },
                'backgroundColor': 'tomato',
                'color': '#FFFFFF'
            },
            ]
        )
    ])
