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
from error import Error
from loading import Loading
from DataLoader import DataLoader
import configparser
import flask
import json
from Secrets import get_secret
from pyathena.error import OperationalError
import os

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
username = None # Stores the RStudio Connect username

# Lay down the basic layout for the app.
app.layout = html.Div(id='main_container', children=[
    Loading('Loading data from server. Sit tight!')
])

frameset = {}

# This initial callback will load all the data into the dashboard.
@app.callback(
    Output('main_container', 'children'),
    Input('main_container', 'children')
)
def load_data(value):
    global username

    # Get the RStudio Connect username
    username = get_username()
    aws = config['uoa']
    if 'uoa' in sections:
        aws = config['uoa']

    if username is None:
        return Error('Oh no something went wrong. Could not find your RStudio username (902)')

    # Get the schema associated with this username from AWS SecretsManager
    secret = get_secret(
        username=username,
        aws_access_key_id=aws['aws_access_key_id'],
        aws_secret_access_key=aws['aws_secret_access_key']
    )
    if secret is None:
        return Error('Whopps! Looks like your RStudio username is not associated with any SensorFabric Study (903)')

    secret = json.loads(secret)
    profile = secret.get('profile')

    if profile == 'mdh':
        print('Using profile mdh')
        schema_name = secret.get('schema_name')
        aws = {
            'aws_access_key_id': secret.get('aws_access_key_id'),
            'aws_secret_access_key': secret.get('aws_secret_access_key'),
            'aws_session_token': secret.get('aws_session_token'),
            'region_name': secret.get('region_name'),
            's3_staging_dir': secret.get('s3_staging_dir'),
            'workgroup': secret.get('workgroup')
        }
    else:
        print('Using profile UOA AWS')
        # Get username from the Rstudio Connect Environment.
        schema_name = secret.get('schema_name')
        aws=config[profile]

    dataloader = DataLoader(aws_access_key_id=aws['aws_access_key_id'],
                            aws_secret_access_key=aws['aws_secret_access_key'],
                            aws_session_token=aws['aws_session_token'] if 'aws_session_token' in aws else None,
                            region_name=aws['region_name'],
                            schema_name=schema_name,
                            s3_staging_dir=aws['s3_staging_dir'],
                            work_group=aws['workgroup'] if 'workgroup' in aws else None,
                            cache=True if ('cache' in aws and aws['cache'] == 'true') else False)

    # Load all the dataset.
    try:
        frameset['sleep'] = dataloader.getSleep()
        frameset['activity'] = dataloader.getActivity()
        frameset['restinghr'] = dataloader.getRestingHR()
        frameset['hrv'] = dataloader.getHRV()
        frameset['participants'] = dataloader.getParticipants()
    except OperationalError as er:
        return Error('This is embarassing, but an error occurred when trying to fetch your dataset (904)')

    return html.Div([
        html.H1(children='Fitbit Compliance App'),

        dcc.Tabs(id='tabs-fitbit-sections', value='tab-overview', children=[
            dcc.Tab(label='Overview', value='tab-overview'),
            dcc.Tab(label='Sleep', value='tab-sleep'),
            dcc.Tab(label='Activity', value='tab-activity'),
            dcc.Tab(label='Resting HR', value='tab-rhr'),
            dcc.Tab(label='Heart Rate Variability', value='tab-hrv')
        ]),

        html.Div(id='tabs-content'),

        html.Hr(),
        html.Div(id='project', children=[
            html.P('Logged in as - {}'.format('local' if username is None else username)),
            html.P('Viewing project - {}'.format(schema_name))
        ])
     ])

def get_credentials(req):
    """
    Get credentials of the current user who is accessing the dashboard.
    """
    credential_header = req.headers.get('RStudio-Connect-Credentials')
    if not credential_header:
        return {}
    return json.loads(credential_header)

def get_username():
    user_metadata = get_credentials(flask.request)
    username = user_metadata.get('user')

    return username

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
    app.run_server(debug=False)
