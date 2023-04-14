#!/usr/bin/env python3

from dash import html, dash_table
import pandas as pd
from utils import createDataTable

def Activity(frame : pd.DataFrame):
    """
    Renders the activity tab data.
    """
    return createDataTable(frame)
