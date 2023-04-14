#!/usr/bin/env python3

from dash import html, dash_table
import pandas as pd
from utils import createDataTable

def Hrv(frame : pd.DataFrame):
    """
    Renders the Hrv tab data.
    """
    return createDataTable(frame)
