"""
Author: Andrew Harris
Python Version: Python3.8.3
"""
import sys

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# from pyfladesk import init_gui

from app import app
from apps import homepage, p_distance_tracer, tree_viewer
from apps import sandbox


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return homepage.layout
    elif pathname == '/apps/p_distance_tracer':
        return p_distance_tracer.layout
    elif pathname == '/apps/tree_viewer':
        return tree_viewer.layout
    elif pathname == '/apps/data_prep':
        return data_prep.layout
    # elif pathname == '/apps/sandbox':
    #     return sandbox.layout
    else:
        return '404 - Page not found'

if __name__ == '__main__':
    app.run_server(debug=False)
    # init_gui(app, window_tittle="Tree House Explorer")
    # if 'win' in sys.platform:
    #     print("Run Windows")
    #     webview.create_window("THEx", app.server)
    #     webview.start(gui='cef')
    # else:
    #     print("Run Other")
    #     webview.create_window("THEx", app.server)
    #     webview.start(gui='qt')