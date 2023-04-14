#!/usr/bin/env python3

from dash import html, dash_table
import pandas as pd
from utils import createDataTable

def Restinghr(frame : pd.DataFrame):
    """
    Renders the sleep tab data.
    """

    return createDataTable(frame)
