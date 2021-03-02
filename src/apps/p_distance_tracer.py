"""
Author: Andrew Harris
Date: 1/28/2021
Python Version 3.8
This Dash tool visualizes p-distance data created by p-distance-calculator.py
It shows data by single or multiple-samples, single or multi-chromosomes.
"""
import time
import importlib
import glob
from pathlib import Path

import numpy as np
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# from flask_caching import Cache

import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


from app import app
from apps import homepage, navbar
from apps.utils import p_dist_utils, graph_options, data_utils

navbar = navbar.Navbar("p-Distance Tracer")


def get_max_range(file_path):
    read_csv = pd.read_csv(
        file_path, sep=',',
        index_col=["Chromosome"],
        dtype={'Start': np.int32, "Stop": np.int32},
    )
    return read_csv['Stop'].max()



############################### Data Collection ###############################
# AVAILABLE_PROJECTS = [Path(name) for name in glob.glob("./src/data/p_distance_data/*")]
PROJECT_NAMES = [{'label': f.stem, 'value': f.as_posix()} for f in Path("src/data/p_distance_data/").iterdir() if f.stem[0] != '.']
INPUT_DF_PATH = PROJECT_NAMES[0]['value']
INPUT_FILE_PATHS = [f for f in Path(INPUT_DF_PATH).iterdir() if f.stem[0] != '.']
INPUT_FILE_OPTIONS = [{'label': t.stem, 'value': t.name} for t in INPUT_FILE_PATHS]
INIT_PROJECT_NAME = PROJECT_NAMES[0]['value']
INIT_DATA_FILE = INPUT_FILE_PATHS[0]
INIT_INPUT_DF = data_utils.build_file_dataframe(INIT_DATA_FILE)
COLUMNS = INIT_INPUT_DF.columns.to_list()


GRAPH_TEMPLATES = graph_options.graph_templates()
SNAPSHOT_FILE_OPTIONS = graph_options.snapshot_file_type()
COLOR_SWATCHES = graph_options.color_swatches()
OUTPUT_PIXEL_SIZES = graph_options.pixel_sizes()
SCALE_OPTIONS = graph_options.figure_output_scales()
FONT_SIZE = '15px'
############################################ BODY #############################################

body = dbc.Container(
    id='container',
    children=[
        dcc.Store(id='reference-name-store'),
        # Control Panel
        dbc.Row(
            children=[
                dbc.Col(
                    id='control-panel',
                    children=[
                        dbc.Tabs(
                            id="control-tabs",
                            children=[
                                # Data
                                dbc.Tab(
                                    label='Data',
                                    label_style={
                                        'color': 'white',
                                        'border': '2px orange solid',
                                        'border-radius': '5px',
                                    },
                                    style={'margin-left': '10px', 'margin-right': '10px'},
                                    children=[
                                        dbc.Row(
                                            children=[
                                                # Project ID
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=['Project ID:'], 
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id='project-options',
                                                            options=PROJECT_NAMES,
                                                            value=INIT_PROJECT_NAME,
                                                            style={
                                                                "color": "black",
                                                                # "width": "75%",
                                                            },
                                                            persistence=True,
                                                            persistence_type='session'
                                                        ),
                                                    ],
                                                    style={
                                                        'margin': '5px',
                                                    },
                                                ),
                                                # Data file
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=['Data File:'], 
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id='pdist_file_options',                                                
                                                            style={
                                                                "color": "black",
                                                                # "width": "75%",
                                                            },
                                                            persistence=True,
                                                            persistence_type='session'
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                                # Chromosome View
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=['Chromosome View:'],
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id='chromosome-quantity',
                                                            options=[
                                                                {'label': 'Single Chromosome',
                                                                    'value': 'single-chrom'},
                                                                {'label': 'All Chromosomes',
                                                                    'value': 'all-chroms'},
                                                            ],
                                                            value='single-chrom',
                                                            style={
                                                                "color": "black",
                                                            },
                                                            persistence=True,
                                                            persistence_type='session'
                                                        ),
                                                    ],
                                                    style={'margin': '5px'}, 
                                                ),
                                                # Chromosome Choice
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            id='chromosome-choice-div',
                                                            children=[
                                                                # Drop down to show chromosome viewing choices
                                                                html.Div(
                                                                    children=[
                                                                        'Chromosome Choice(s):'],
                                                                    className='title',
                                                                ),
                                                                dcc.Dropdown(
                                                                    id='chromosome-options',
                                                                    style={"color": "black"},
                                                                    persistence=True,
                                                                    persistence_type='session'
                                                                ),
                                                            ],
                                                            style={'display': 'none'}
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                                # # Sample Selection
                                                # dbc.Col(
                                                #     id='sample-selection-div',
                                                #     children=[
                                                #         html.Div(
                                                #             children=[
                                                #                 'Sample Choice(s):'],
                                                #             className='title',
                                                #         ),
                                                #         dcc.Dropdown(
                                                #             id='sample-options',
                                                #             style={'color': 'black'},
                                                #             multi=True,
                                                #         ),                                                                                                                                                                 
                                                #     ],
                                                # ),
                                            ],
                                            style={'background': 'orange', 'border-radius': '5px', 'margin-bottom': '10px'},
                                            no_gutters=True,
                                        ),
                                    ],
                                ),
                                # Graph Toggles
                                dbc.Tab(
                                    label="Graph Toggles",
                                    label_style={
                                        'border': '2px orange solid',
                                        'border-radius': '5px',
                                    },
                                    style={'margin-left': '10px', 'margin-right': '10px'},
                                    children=[
                                        dbc.Row(
                                            children=[
                                                dbc.Col(
                                                    # id="single_chrom_collapse_div",
                                                    children=[
                                                        html.Div(
                                                            children=['Collapsed Sample View:'],
                                                            className='title',
                                                        ),
                                                        html.Div(
                                                            dbc.Checklist(
                                                                id="collapse-single-chrom",
                                                                options=[
                                                                    {"label": "On", "value": "collapse_view"},
                                                                ],
                                                                value=["collapse_view"],
                                                                switch=True,
                                                                style={'color': 'black', 'margin': '5px'},
                                                            ),
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                    width=2,
                                                ), 
                                                # Sample Selection
                                                dbc.Col(
                                                    id='sample-selection-div',
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                'Sample Choice(s):'],
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id='sample-options',
                                                            style={'color': 'black'},
                                                            multi=True,
                                                        ),                                                                                                                                                                 
                                                    ],
                                                    style={'margin': '5px'},
                                                    width=5,
                                                ),
                                            ],
                                            style={'background': 'orange', 'border-radius': '5px', 'margin-bottom': '10px'},
                                            no_gutters=True,
                                        ),
                                    ],
                                ),
                                # Graph Options
                                dbc.Tab(
                                    label="Graph Optons",
                                    label_style={
                                        'border': '2px orange solid',
                                        'border-radius': '5px',
                                    },
                                    style={'margin-left': '10px', 'margin-right': '10px'},
                                    children=[
                                        dbc.Row(
                                            children=[
                                                # Graph Theme
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                'Graph Color Theme:'],
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id="template-option",
                                                            options=[{'label': i, 'value': i}
                                                                    for i in GRAPH_TEMPLATES],
                                                            value="plotly_dark",
                                                            persistence=True,
                                                            persistence_type='session',
                                                            style={
                                                                "color": "black"
                                                            }
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                                # Line Colors
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                'Line Colors (Discrete):'],
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id="line-color-option",
                                                            options=[{'label': "{} - {} colors".format(i, len(COLOR_SWATCHES[i])), 'value': i}
                                                                    for i in COLOR_SWATCHES],
                                                            value="Plotly",
                                                            persistence=True,
                                                            persistence_type='session',
                                                            style={
                                                                "color": "black"
                                                            }
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                                # Snapshot fileType
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=['Snapshot File Type:'],
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id="snapshot-file-option",
                                                            options=[{'label': i, 'value': i}
                                                                    for i in SNAPSHOT_FILE_OPTIONS],
                                                            value="jpeg",
                                                            persistence=True,
                                                            persistence_type='session',
                                                            style={
                                                                "color": "black"
                                                            }
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                                # Snapshot Pixel Dimensions
                                                # NOTE: Update this to have two input boxes
                                                # ['length'] x ['width']
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=['Snapshot Pixel Size:'],
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id="snapshot-pixel-size",
                                                            options=[{'label': i, 'value': i}
                                                                    for i in OUTPUT_PIXEL_SIZES],
                                                            persistence=True,
                                                            persistence_type='session',
                                                            value="1250x800",
                                                            style={
                                                                "color": "black"
                                                            }
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                                # Snapshot Scale
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=['Snapshot Output Scale:'],
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id="snapshot-scale",
                                                            options=[{'label': i, 'value': i}
                                                                    for i in SCALE_OPTIONS],
                                                            value=1,
                                                            persistence=True,
                                                            persistence_type='session',
                                                            style={
                                                                "color": "black"
                                                            }
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                            ],
                                            style={'background': 'orange', 'border-radius': '5px 5px 0px 0px'},
                                            no_gutters=True,
                                        ),
                                        dbc.Row(
                                            children=[
                                                # Line Width
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=['Line Width:'],
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id='line_width_options',
                                                            options=graph_options.line_width_options(),
                                                            value=graph_options.line_width_options()[0]['value'],
                                                            style={
                                                                "color": "black",
                                                                # "width": "75%",
                                                            },
                                                            persistence=True,
                                                            persistence_type='session'
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                                # Font Size
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=['Graph Font Size:'],
                                                            className='title',
                                                        ),
                                                        dcc.Dropdown(
                                                            id='font_size_options',
                                                            options=graph_options.font_size_options(),
                                                            value=15,
                                                            style={'color': 'black'},
                                                            persistence=True,
                                                            persistence_type='session'
                                                        ),
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                                dbc.Col(
                                                    children=[
                                                        html.Div(
                                                            children=['Number of Columns:'],
                                                            className='title',
                                                        ),
                                                        # dcc.Dropdown(
                                                        #     id='font_size_options',
                                                        #     options=graph_options.font_size_options(),
                                                        #     value=15,
                                                        #     style={'color': 'black'},
                                                        #     persistence=True,
                                                        #     persistence_type='session'
                                                        # ),
                                                        dcc.RadioItems(
                                                            id='facet_col_num',
                                                            options=[
                                                                {'label': '1', 'value': 1},
                                                                {'label': '2', 'value': 2},
                                                            ],
                                                            value=1,
                                                        )
                                                    ],
                                                    style={'margin': '5px'},
                                                ),
                                            ],
                                            style={'background': 'orange', 'border-radius': '0px 0px 5px 5px', 'margin-bottom': '10px'},
                                            no_gutters=True,
                                        ),
                                    ],
                                ),
                                # Help
                                dbc.Tab(
                                    label="Help",
                                    label_style={
                                        'border': '2px orange solid',
                                        'border-radius': '5px',
                                    },
                                    style={'margin-left': '10px', 'margin-right': '10px'},
                                    children=[dbc.Row(
                                        children=[
                                            dbc.Col(),
                                        ],
                                    )],
                                ),
                            ],
                            style={'margin': '10px'}
                        ),
                    ],
                    width=12,
                ),
            ],
            style={
                'border': '2px orange solid',
                'border-radius': '5px',
                'padding-left': '5px',
                'padding-right': '5px',
                'margin-top': '5px',
                'margin-bottom': '5px',
            },
            no_gutters=True,
        ),
        # Graph
        dbc.Row(
            id='body',
            children=[
                # Graphs
                dbc.Col(
                    id='graph-column',
                    children=[
                        dcc.Loading(
                            id="loading-1",
                            children=[html.Div([
                                html.Div(
                                    id='graphs',
                                    children=[
                                        dcc.Graph(
                                            figure=(px.bar(template='plotly_dark')),
                                            loading_state={"is_loading": True},                                    
                                        )
                                    ],
                                    loading_state={'is_loading':True},                            
                                ),
                            ])],
                            type="cube",
                        ),
                    ],
                    width=12,
                    align="stretch",
                    style={
                        "border": "2px orange solid",
                        "border-radius": "5px",
                        "background": "primary",
                    }
                ),
            ],
            style={"margin-top": "10px"},
            no_gutters=True
        ),
    ],
    style={
        'height': '100vh',
        # 'margin-right': 0,
        # 'margin-left': 0,
        # 'max_width': 50000,
    },
    fluid=True,
)

layout = html.Div(
    children=[
        navbar,
        body
    ]
)

# -----------------------------------------------------------------------------------------------
################################# Set display options ################################
@app.callback(Output(component_id='chromosome-choice-div', component_property='style'),
             [Input(component_id='chromosome-quantity', component_property='value')]
)
def display_chromosome_selection(chromosome_quantity):
    if chromosome_quantity == 'all-chroms':
        return dict(display='none')
    else:
        return dict(display=True)


@app.callback(Output(component_id='sample-selection-div', component_property='style'),
             [Input(component_id='chromosome-quantity', component_property='value'),
             Input(component_id="collapse-single-chrom", component_property="value"),]
)
def display_sample_selection(chromosome_quantity, collapse_switch):
    if chromosome_quantity == 'all-chroms':
        return dict(display='none')
    elif (len(collapse_switch) == 1) and (collapse_switch[0] == 'collapse_view'):
        return dict(display='none')
    else:
        return dict(display=True)


@app.callback(
    Output(component_id="single_chrom_collapse_div", component_property="style"),
    [Input(component_id='chromosome-quantity', component_property='value')]
)
def display_collapse_single_chrom_switch(chromosome_quantity):
    if chromosome_quantity == 'all-chroms':
        return dict(display='none')
    else:
        return dict(display=True)

# -----------------------------------------------------------------------------------------------
################################# set option dropdown menu selections ################################
@app.callback(
    Output('chromosome-options', 'options'),
    [Input('chromosome-quantity', 'value'),
     Input('pdist_file_options', 'value'),
     Input('project-options', 'value')]
)
def set_chromosome_choice(chrom_quantity, current_file, current_project):
    if chrom_quantity == 'all-chroms':
        return [dict(label='All chromosomes selected', value='All chromosomes selected')]
    else:
        options = []
        read_file = pd.read_csv(
            current_file,
            sep=',',
            engine='python',
            usecols=["Chromosome"],
        )

        for chrom in read_file['Chromosome'].unique():
            options.append(
                dict(label=chrom, value=chrom)
            )
        return options


@app.callback(
    [Output('sample-options', 'options'),
    Output('reference-name-store', 'data')],
    [Input('chromosome-quantity', 'value'),
     Input('pdist_file_options', 'value'),
     Input('project-options', 'value')]
)
def set_sample_choice(chrom_quantity, current_file, current_project):
    read_csv = pd.read_csv(current_file, sep=',')
    ref_sample_name = ""
    # Find Reference Sample and remove from dataset -------------------------------------------------
    for sample in read_csv.columns[2:]:
        if read_csv[sample].unique()[0] == 0:
            read_csv.drop(columns=[sample], inplace=True)
            ref_sample_name = str(sample)
            break
        else:
            continue
    sample_names = [name for name in read_csv.columns[3:]]
    sample_names.sort()  # Sort names alphabetically
    return [{'label': i, 'value': i} for i in sample_names], ref_sample_name


@app.callback(
    Output(component_id='sample-options', component_property='value'),
    [Input(component_id='sample-options', component_property='options')]
)
def set_sample_option_value(options):
    return [options[0]['value']]


@app.callback(
    Output(component_id='chromosome-options', component_property='value'),
    [Input(component_id='chromosome-options', component_property='options')]
)
def set_chrom_value(options):
    return options[0]['value']


@app.callback(
    Output('pdist_file_options', 'options'),
    [Input('project-options', 'value')]
)
def set_file_options(current_project):
    files = [{'label': f.stem, 'value': f.as_posix()} for f in Path(current_project).iterdir() if (f.is_file()) and (f.stem[0] != ".")]
    return files

@app.callback(
    Output('pdist_file_options', 'value'),
    [Input('pdist_file_options', 'options')]
)
def set_file_value(file_options):
    return file_options[0]['value']


# -----------------------------------------------------------------------------------------------
################################# Handle accordians for control panel ################################

@app.callback(
    [
        Output("data-options-collapse", "is_open"),
        Output("graph-options-collapse", "is_open"),
    ],
    [
        Input("data-options-toggle", "n_clicks"),
        Input("graph-options-toggle", "n_clicks")
    ],
    [
        State("data-options-collapse", "is_open"),
        State("graph-options-collapse", "is_open"),
    ],
)
def toggle_accordion(data_options_n, graph_options_n, data_options_is_open, graph_options_is_open):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Open data control collapse
    if button_id == "data-options-toggle" and data_options_n:
        return not data_options_is_open, False
    # Open graph control collapse
    elif button_id == "graph-options-toggle" and graph_options_n:
        return False, not graph_options_is_open
    return False, False


#----------------------------------------------------------------------------------------------------
### Graphing CB's ###
@app.callback(
    Output(component_id='graphs', component_property='children'),
    [Input(component_id="sample-options", component_property='value'),
     Input(component_id='chromosome-options', component_property='value'),
     Input(component_id='pdist_file_options', component_property='value'),
     Input(component_id='template-option', component_property='value'),
     Input(component_id='reference-name-store', component_property='data'),
     Input(component_id='project-options', component_property='value'),
     Input(component_id="snapshot-file-option", component_property="value"),
     Input(component_id="line_width_options", component_property="value"),
     Input(component_id="line-color-option", component_property='value'),
     Input(component_id="collapse-single-chrom", component_property="value"),
     Input(component_id="snapshot-pixel-size", component_property="value"),
     Input(component_id="snapshot-scale", component_property="value"),
     Input(component_id="font_size_options", component_property="value"),
     Input(component_id="facet_col_num", component_property="value"),]
)
def update_main_graph(
    chosen_samples, 
    chromosome, 
    current_file, 
    chosen_template,
    reference_name,
    current_project,
    snapshot_file_value,
    line_width,
    line_color,
    collapse_single_chrom,
    snapshot_pixel_size,
    snapshot_scale,
    font_size,
    facet_col_num,
):
    # if single sample given, this will put it into a list. ------------------------------------------
    if type(chosen_samples) != list:
        chosen_samples = [chosen_samples]
        pass

    # if user de-selects all samples, it will throw error so return None------------------------------
    if len(chosen_samples) == 0:
        return None

    # Load in data and clean data --------------------------------------------------------------------
    read_csv = pd.read_csv(current_file, dtype={'Start': np.int32, "Stop": np.int32})
    read_csv = read_csv.melt(id_vars=["Chromosome", "Start", "Stop"])
    read_csv.columns = ["Chromosome", "Start", "Stop", "Sample", "p_distance"]
    read_csv.sort_values(by=["Chromosome", "Start", "Stop"], inplace=True)

    # Clean out unwanted samples
    read_csv = read_csv[read_csv["Sample"] != reference_name]

    # Get sample and chromosome data ----------------------------------------------------------------
    chromosomes = [i for i in read_csv['Chromosome'].unique()]
    samples = [i for i in read_csv['Sample'].unique()]
    samples.sort(reverse=True)

    # Get overall max p_distance value to set y-axis ranges for all plots ---------------------------
    y_max = float(read_csv["p_distance"].max() * 1.1)  # increase 10% above max
    x_max = read_csv["Stop"].max() * 1.01  # increase 10% above max

    colors = COLOR_SWATCHES[line_color]

    base_graph_height = 150

    if chromosome == 'All chromosomes selected':
        graphs = []
        # --------------------------------------------------------------------------------------------------------------     
        
        fig = make_subplots(
            rows=len(chromosomes),
            cols=1,
            x_title="Position",
            y_title="p-distance",
            row_titles=chromosomes,
            vertical_spacing=0.01,
            row_heights=[base_graph_height] * len(chromosomes),
        )
        for placeholder, sample in enumerate(samples):
            legend_flag = True
            for row, current_chromosome in enumerate(chromosomes, start=1):
                filt = (read_csv['Chromosome'] == current_chromosome) & (
                    read_csv["Sample"] == sample)
                sample_chromosome_data = read_csv[filt]
                # Make figure
                fig.add_trace(
                    go.Scatter(
                        x=sample_chromosome_data['Stop'],
                        y=sample_chromosome_data['p_distance'],
                        mode='lines',
                        legendgroup=str(sample),
                        name=sample,
                        line=dict(
                            color=colors[placeholder],
                            width=float(line_width)
                        ),

                        showlegend=legend_flag,
                    ),
                    row=row,
                    col=1
                )
                legend_flag = False
                continue
        # --- Update Figure ---
        fig.update_layout(
            height=base_graph_height*len(chromosomes),
            template=chosen_template,
            margin=dict(
                l=60,
                r=10,
                b=60,
                t=0,
                pad=5
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1,
                xanchor="left",
                x=0,
                itemsizing='trace',
                title="",
            ),
            font=dict(
                family="Arial, monospace",
                size=font_size,
            ),
            annotations=[{
                "font": dict(
                        family="Arial, monospace",
                        size=12,
                        ),
            }]
        )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig.update_yaxes(
            range=[0.0, y_max],
            fixedrange=True,
        )
        # fig.update_xaxes(range=[0, x_max])
        graphs.append(
            html.Div(
                dcc.Graph(
                    id='subplot',
                    figure=fig,
                    config=dict(
                        # dragmode='zoom',
                        responsive=True,
                        displayModeBar=True,
                        toImageButtonOptions=dict(
                            format=snapshot_file_value,
                            filename="Graph_Name",
                            height=int(snapshot_pixel_size.split("x")[0]),
                            width=int(snapshot_pixel_size.split("x")[1]),
                            scale=snapshot_scale,
                        ),                
                    ),
                    style={
                        "height": "{}px".format(base_graph_height*len(chromosomes)),
                        "border": "2px black solid",
                        "border-radius": "5px",
                        "text-decoration": "bold"
                    }
                ),
            ),
        )
        return graphs
    # --- Single Chromosome Graph ---
    else:
        if collapse_single_chrom == []:
            graphs = p_dist_utils.single_chrom_expanded(
                chosen_samples,
                chromosome,
                current_file,
                chosen_template,
                reference_name,
                current_project,
                snapshot_file_value,
                line_width,
                collapse_single_chrom,
                colors,
                base_graph_height,
                samples,
                read_csv,
                snapshot_pixel_size,
                snapshot_scale,
                font_size,
            )
            return graphs
        else:
            assert len(collapse_single_chrom) >= 1
            graphs = p_dist_utils.single_chrom_condensed(
                    chosen_samples,
                    chromosome,
                    current_file,
                    chosen_template,
                    reference_name,
                    current_project,
                    snapshot_file_value,
                    line_width,
                    collapse_single_chrom,
                    colors,
                    base_graph_height,
                    samples,
                    read_csv,
                    snapshot_pixel_size,
                    snapshot_scale,
                    font_size,
            )
            return graphs


