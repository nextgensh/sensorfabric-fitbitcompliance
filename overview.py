#!/usr/bin/env python3
import pandas as pd
from utils import createDataTable
from dash import html, dcc, dash_table
from datetime import datetime

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

    # Check to see which users need to resync (open the fitbit app and sync)
    # If we have not gotten their data for 2 or more days then they need to open the
    # app and sync.
    today = datetime.now()
    sync = []   # 1 - Syncing is required, 0 - Syncing is not required.
    for pid in pids:
        prow = activity[activity['participantidentifier'] == pid]['end_date']
        if prow.shape[0] > 0:
            act_end_date = activity[activity['participantidentifier'] == pid]['end_date'].iloc[0]
            act_end_date = datetime.strptime(act_end_date, '%Y-%m-%d')
            delta = (today - act_end_date)
            if delta.days >= 2:
                # This needs to be marked as syncing required.
                sync += [1]
            else:
                sync += [0]
        else:
            sync += [0]

    # Method which checks if we have less than 80% sleep data as compared to activity data.
    # These participants might be taking off their device at night, or there might be an issue
    # auto-detecting their sleep.
    modified_pid = []
    for pid in pids:
        # Check if this participant was inside sleep.
        sleeprow = sleep[sleep['participantidentifier']==pid]
        actrow = activity[activity['participantidentifier']==pid]
        if sleeprow.shape[0] > 0 and actrow.shape[0] > 0:
            sleepdays = sleeprow['days_recorded'].iloc[0]
            actdays = actrow['days_recorded'].iloc[0]
            if sleepdays < 0.8*actdays:
                modified_pid += ['🌙 {}'.format(pid)]
            else:
                modified_pid += [pid]
        else:
            modified_pid += [pid]

    # NOTE: The frame now has the modified participant id, with unicode emoji indicating
    # if sleep days recorded < 80% of activity days recorded. No analysis after this point.

    frame = pd.DataFrame({
        'participantidentifier': modified_pid,
        'sleep' : flags[0],
        'activity' : flags[1],
        'restinghr' : flags[2],
        'hrv' : flags[3],
        'sync' : sync
    })

    return html.Div([
        dash_table.DataTable(
            id='sleepTable',
            sort_action='native',
            filter_action='native',
            style_header={'font-weight':'bold'},
            columns=[
                {'name':'Participant', 'id':'participantidentifier'},
                {'name':'Sleep', 'id':'sleep'},
                {'name':'Activity', 'id':'activity'},
                {'name':'Resting HR', 'id':'restinghr'},
                {'name':'HRV', 'id':'hrv'}
            ],
            data=frame.to_dict('records'),
            style_data_conditional = [
            {
                'if': {
                    'filter_query': '{sync} = 1',
                    'column_id': 'participantidentifier'
                },
                'backgroundColor': '#6666ff',
                'color': '#FFFFFF'
            },
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
        ),
        renderSummary(frame),
        renderLegends()
    ])

def renderSummary(frame : pd.DataFrame):
    """
    Method which renders the summary section.
    Takes the overview dataframe as the input.
    """
    return html.Div(id='summary', children=[
        html.H2('Number of participants who have - '),
        html.Ul(children=[
            html.Li('Fitbit connected - {}'.format(frame.shape[0])),
            html.Li('Sleep data - {}'.format(frame[frame['sleep'] == 'Yes'].shape[0])),
            html.Li('Activity data - {}'.format(frame[frame['activity'] == 'Yes'].shape[0])),
            html.Li('Resting HR data - {}'.format(frame[frame['restinghr'] == 'Yes'].shape[0])),
            html.Li('HRV data - {}'.format(frame[frame['hrv'] == 'Yes'].shape[0])),
            html.Li('Not synced in the last 2 days or more - {}'.format(frame[frame['sync'] == 1].shape[0])),
        ])
    ])

def renderLegends():
    """
    Method which Gives and explaination of the various legends used in the overview dash.
    """
    return html.Div(id='legends', children=[
        html.H2('Legends'),
        html.Ul(children=[
            html.Li(style={'color':'#3D9970'},
                    children=['Green - Data for this metric exists. Refer to the individual tab to learn more about this metric']),
            html.Li(style={'color':'tomato'},
                    children=["""Orange - Data for this metric doed NOT exists. Resting HR requires a minimum of 3 hours continuous (staged) sleep
                    to data on a day to be calculated. If you are not seeing HRV data, then the participants have not enabled their Health Metric card
                    inside the Fitbit application """]),
            html.Li(style={'color':'#6666ff'},
                    children=["""Purple - Participants have not open the Fitbit app and synced with their wearable in over 2 days.
                    We check this by filtering days when participant steps are more than 0. In most situations when we get steps=0
                    it is because participants have not opened their Fitbit app to sync. It is a good practice for participants to
                    open their Fitbit app and also their MyDataHelps at least once every 2 days, to sync with their device. This data is not
                    lost but needs to be synced before the study ends."""]),
            html.Li(style={'color':'#000000'},
                    children=["""🌙 - It is common for participants to have a few missing days when they take the device off
                    or forget to charge. However we mark participants who have less than 80% sleep data as compared to their daily data.
                    These participants could be taking their device off at night more often than required. """]),
        ])
    ])
