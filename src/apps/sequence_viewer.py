# # Imports
# import time
# import importlib
# import glob
# from pathlib import Path

# import numpy as np
# import pandas as pd

# import dash_bio as dashbio
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output, State
# import dash_bootstrap_components as dbc

# import plotly
# import plotly.graph_objects as go
# import plotly.express as px
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# import plotly.express as px


# from app import app
# from apps import homepage, navbar

# navbar = navbar.Navbar()


# AVAILABLE_PROJECTS = [Path(name) for name in glob.glob("./data/sequence_viewer_data/*")]
# AVAILABLE_DATA = [Path(fname) for fname in AVAILABLE_PROJECTS[0].iterdir() if fname.name[0] != "."]
# GRAPH_TEMPLATES = ["plotly", "plotly_white", "plotly_dark",
#                    "ggplot2", "seaborn", "simple_white", "none"]
# SNAPSHOT_FILE_OPTIONS = ["jpeg", "png", "svg"]  # pdf is not supported :(

# ############################################ Initial data #############################################
# intial_data = Path("./data/sequence_viewer_data/") / str(AVAILABLE_PROJECTS[0].parts[-1]) / str(AVAILABLE_DATA[0].parts[-1])
# with open(intial_data, 'r') as intital_data_open:
#     initial_seq_data = intital_data_open.read()

# # Write a funtion that will limit the amount of data to be read in at a given time.

# ############################################ BODY #############################################

# body = dbc.Container(
#     id='container',
#     children=[
#         dcc.Loading(
#                     id="loading-2",
#                     children=[html.Div([html.Div(id="subplot")])],
#                     type="circle",
#                 ),
#         dcc.Store(id='fasta-sequence-store'),
#         dbc.Row(
#             id="top-margin",
#             style={
#                 "margin-bottom": "10px"
#             }
#         ),
#         dbc.Row(
#             children=[
#                 dbc.Col(
#                     children=[
#                         dashbio.AlignmentChart(
#                             id='my-alignment-viewer',
#                             data=initial_seq_data
#                         ),
#                         html.Div(id='alignment-viewer-output')
#                     ]
#                 ),

#                 dbc.Col(
#                     id='control-panel-tabs',
#                     children=[
#                         dcc.Tabs(
#                             id='info-tabs',
#                             value='settings',
#                             children=[
#                                 # Data Options Tab
#                                 dcc.Tab(
#                                     label='Data Controls',
#                                     value='settings',
#                                     children=html.Div(
#                                         id='control-panel-div',
#                                         children=[
#                                             html.P(),
#                                             html.H6(
#                                                 children=['Project:'],
#                                                 style={
#                                                     "color": "black"
#                                                 }
#                                             ),
#                                             dcc.Dropdown(
#                                                 id='project-options',
#                                                 options=[
#                                                     {'label': i.parts[-1], 'value': i.parts[-1]} for i in AVAILABLE_PROJECTS],
#                                                 value=AVAILABLE_PROJECTS[0].parts[-1],
#                                                 style={
#                                                     "color": "black",
#                                                 },
#                                                 persistence=True,
#                                                 persistence_type='local'
#                                             ),
#                                             html.P(),
#                                             html.H6(
#                                                 children=['Data:'],
#                                                 style={
#                                                     "color": "black"
#                                                 }
#                                             ),
#                                             dcc.Dropdown(
#                                                 id='file-options',
#                                                 options=[
#                                                     {'label': i.parts[-1], 'value': i.parts[-1]} for i in AVAILABLE_DATA
#                                                 ],
#                                                 value=AVAILABLE_DATA[0].parts[-1],
#                                                 style={
#                                                     "color": "black",
#                                                 },
#                                                 persistence=True,
#                                                 persistence_type='local'
#                                             ),
#                                             # # Drop down to set how many chromosomes to show at once
#                                             # html.P(),
#                                             # html.H6(
#                                             #     children=[
#                                             #         'How many chromosomes to show:'],
#                                             #     style={
#                                             #         "color": "black"
#                                             #     }
#                                             # ),
#                                             # dcc.Dropdown(
#                                             #     id='chromosome-quantity',
#                                             #     options=[
#                                             #         {'label': 'Single Chromosome',
#                                             #             'value': 'single-chrom'},
#                                             #         {'label': 'All Chromosomes',
#                                             #             'value': 'all-chroms'},
#                                             #     ],
#                                             #     value='single-chrom',
#                                             #     style={
#                                             #         "color": "black",
#                                             #     },
#                                             #     persistence=True,
#                                             #     persistence_type='local'
#                                             # ),

#                                             # html.Div(
#                                             #     id='chromosome-choice-div',
#                                             #     children=[
#                                             #         # Drop down to show chromosome viewing choices
#                                             #         html.P(),
#                                             #         html.H6(
#                                             #             children=[
#                                             #                 'Chromosome Choice(s):'],
#                                             #             style={
#                                             #                 "color": "black"
#                                             #             }
#                                             #         ),
#                                             #         dcc.Dropdown(
#                                             #             id='chromosome-options',
#                                             #             style={
#                                             #                 "color": "black",
#                                             #             },
#                                             #             persistence=True,
#                                             #             persistence_type='local'
#                                             #             # Callback will set data
#                                             #         ),
#                                             #     ],
#                                             #     style={
#                                             #         'display': 'none'
#                                             #     }
#                                             # ),
#                                             # html.Div(
#                                             #     id='sample-selection-div',
#                                             #     children=[
#                                             #         # Drop down to show sample choices
#                                             #         html.P(),
#                                             #         html.H6(
#                                             #             children=[
#                                             #                 'Sample Choice(s):'],
#                                             #             style={
#                                             #                 "color": "black"
#                                             #             }
#                                             #         ),
#                                             #         dcc.Dropdown(
#                                             #             id='sample-options',
#                                             #             style={
#                                             #                 "color": "black",
#                                             #                 "height": "75px"
#                                             #             },
#                                             #             multi=True,
#                                             #             # Callback will set data
#                                             #         ),
#                                             #     ],
#                                             # ),
#                                         ],
#                                     ),
#                                     style={
#                                         "color": "black",
#                                         # "width": "100%",
#                                     }
#                                 ),
#                                 # Graph Options Tab
#                                 dcc.Tab(
#                                     label="Graph Options",
#                                     value="graph-options",
#                                     children=html.Div(
#                                         id="graphing_options-div",
#                                         children=[
#                                             html.P(),
#                                             html.H6(
#                                                 children=[
#                                                     'Graph Color Theme:'],
#                                                 style={
#                                                     "color": "black"
#                                                 }
#                                             ),
#                                             dcc.Dropdown(
#                                                 id="template-option",
#                                                 options=[{'label': i, 'value': i}
#                                                          for i in GRAPH_TEMPLATES],
#                                                 value="plotly_dark",
#                                                 style={
#                                                     "color": "black"
#                                                 }
#                                             ),

#                                             html.P(),
#                                             html.H6(
#                                                 children=[
#                                                     'Snapshot File Type:'],
#                                                 style={
#                                                     "color": "black"
#                                                 }
#                                             ),
#                                             dcc.Dropdown(
#                                                 id="snapshot-file-option",
#                                                 options=[{'label': i, 'value': i}
#                                                          for i in SNAPSHOT_FILE_OPTIONS],
#                                                 value="jpeg",
#                                                 style={
#                                                     "color": "black"
#                                                 }
#                                             ),
#                                         ]
#                                     ),
#                                     style={
#                                         "color": "black"
#                                     }
#                                 ),
#                                 # About Info Tab
#                                 dcc.Tab(
#                                     label='Help',
#                                     value='info-page',
#                                     children=html.Div(),
#                                     style={
#                                         "color": "black",
#                                         "text-align": "center",
#                                         "vertical-align": "middle",
#                                     }
#                                 )
#                             ]
#                         ),
#                     ],
#                     # Control pannel CSS elements
#                     width=3,
#                     style={
#                         "border": "2px black solid",
#                         "border-radius": "5px",
#                         "padding-top": "25px",
#                         "padding-bottom": "25px",
#                         "padding-left": "25px",
#                         "padding-right": "25px",
#                         "background": "#ffcc99"
#                     }
#                 ),
#             ]
#         )
#     ],
#     style={
#         'height': '100vh',
#         'margin-right': 0,
#         'margin-left': 0,
#         'max_width': 50000,
#         # 'background-color': 'lightblue'
#     },
#     fluid=True,
# )

# layout = html.Div(
#     children=[
#         navbar,
#         body
#     ]
# )



# @app.callback(
#     dash.dependencies.Output('my-alignment-viewer', 'data'),
#     [dash.dependencies.Input('file-options', 'value'),
#     dash.dependencies.Input('project-options', 'value')]
# )
# def store_fasta(file, project):
#     file_path = Path("./data/sequence_viewer_data/") / project / str(file)
#     with open(file_path, encoding='utf-8') as read:
#         read_file = read.read()
#         return read_file

# # @app.callback(
# #     dash.dependencies.Output('alignment-viewer-output', 'children'),
# #     [dash.dependencies.Input('my-alignment-viewer', 'eventDatum')]
# # )
# # def update_output(value):
# #     if value is None:
# #         return 'No data.'
# #     return str(value)
