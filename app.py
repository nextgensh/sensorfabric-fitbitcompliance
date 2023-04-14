#!/usr/bin/env python3

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sleep import Sleep
from activity import Activity
from restinghr import Restinghr
from hrv import Hrv
from overview import Overview
from DataLoader import DataLoader
import configparser

# Create a new dash object.
app = Dash('Compliance Dashboard', suppress_callback_exceptions=True)

# Parse the configuration file.'
config = configparser.ConfigParser()
config.read('config.cfg')
sections=config.sections()
if len(sections) <= 0:
    # Add error handling because the configuration file is missing.
    # Cannot do anything without that.
    pass

dataloader = None

# Profile to use for the dash application.
profile = 'uoa'

# Set the correct dataloader.
if profile in sections:
    aws=config[profile]
    dataloader = DataLoader(aws_access_key_id=aws['aws_access_key_id'],
                            aws_secret_access_key=aws['aws_secret_access_key'],
                            aws_session_token=aws['aws_session_token'] if 'aws_session_token' in aws else None,
                            region_name=aws['region_name'],
                            schema_name=aws['schema_name'],
                            s3_staging_dir=aws['s3_staging_dir'],
                            work_group=aws['workgroup'] if 'workgroup' in aws else None,
                            cache=True if ('cache' in aws and aws['cache'] == 'true') else False)

if dataloader == None:
    # We don't have any data loader, need to do error handling
    # and display the correct error message.
    pass

# Lay down the basic layout for the app.
app.layout = html.Div(id='main_container', children=[
    html.Center('Loading data from server. Sit tight!')
])

frameset = {}

# This initial callback will load all the data into the dashboard.
@app.callback(
    Output('main_container', 'children'),
    Input('main_container', 'children')
)
def load_data(value):
    print('main container callback called')
    # Load all the dataset.
    frameset['sleep'] = dataloader.getSleep()
    frameset['activity'] = dataloader.getActivity()
    frameset['restinghr'] = dataloader.getRestingHR()
    frameset['hrv'] = dataloader.getHRV()
    frameset['participants'] = dataloader.getParticipants()

    return html.Div([
        html.H1(children='Compliance Dashboard for Fitbit'),

        dcc.Tabs(id='tabs-fitbit-sections', value='tab-overview', children=[
            dcc.Tab(label='Overview', value='tab-overview'),
            dcc.Tab(label='Sleep', value='tab-sleep'),
            dcc.Tab(label='Activity', value='tab-activity'),
            dcc.Tab(label='Resting HR', value='tab-rhr'),
            dcc.Tab(label='Heart Rate Variability', value='tab-hrv')
        ]),

        html.Div(id='tabs-content')
     ])


# Create a callback for the tabs.
@app.callback(Output('tabs-content', 'children'),
                Input('tabs-fitbit-sections', 'value'))
def render_tab_content(tab):
    if tab == 'tab-overview':
        return Overview(frameset)
    elif tab == 'tab-sleep':
        return Sleep(frameset['sleep'])
    elif tab == 'tab-activity':
        return Activity(frameset['activity'])
    elif tab == 'tab-rhr':
        return Restinghr(frameset['restinghr'])
    elif tab == 'tab-hrv':
        return Hrv(frameset['hrv'])
    else:
        return html.P('{tab} tab has been selected'.format(tab=tab))

if __name__ == '__main__':
    app.run_server()
