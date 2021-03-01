from pathlib import Path
from io import StringIO

from Bio import Phylo
from ete3.coretype.tree import TreeError
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table as dt
import numpy as np
import pandas as pd
import plotly.express as px

from flask_caching import Cache

from apps import navbar
from app import app
from apps.utils import tree_utils, data_utils, graph_options

# from tree_utils import DrawTree

# --- Initial directory collection ---
TREE_DATA_DIR = Path('src/data/tree_viewer_data/')

# collect project names in tree_viewer_data
PROJECT_NAMES = [{'label': f.stem, 'value': f.stem} for f in TREE_DATA_DIR.iterdir() if f.stem[0] != '.']
# PROJECT_NAMES = [{'label': i, 'value': i} for i in DATA_DROPDOWN_OPTIONS]

INPUT_DF_PATH = TREE_DATA_DIR / PROJECT_NAMES[0]['value'] / 'topology_files'
INPUT_FILE_PATHS = [f for f in INPUT_DF_PATH.iterdir()]
INPUT_FILE_OPTIONS = [{'label': t.stem, 'value': t.name} for t in INPUT_FILE_PATHS]
# First project data
INIT_PROJECT_NAME = PROJECT_NAMES[0]['value']
INIT_DATA_FILE = INPUT_FILE_PATHS[0]
INIT_INPUT_DF = data_utils.build_file_dataframe(INIT_DATA_FILE)
COLUMNS = INIT_INPUT_DF.columns.to_list()
INIT_CHROMS = [{'label': c, 'value': c} for c in INIT_INPUT_DF[COLUMNS[0]].unique()]
INIT_TOPS = [{'label': t, 'value': t} for t in INIT_INPUT_DF[COLUMNS[3]].unique()]

# --- Graph options ---
GRAPH_TEMPLATES = graph_options.graph_templates()
COLOR_OPTIONS = [c for c in px.colors.named_colorscales()]
COLOR_SWATCHES = graph_options.color_swatches()
OUTPUT_PIXEL_SIZES = graph_options.pixel_sizes()
SCALE_OPTIONS = graph_options.figure_output_scales()

# Set options for output image format
SNAPSHOT_FILE_OPTIONS = graph_options.snapshot_file_type()

FONT_SIZE = '20px'

# ------------------------------- Helper Functions ----------------------------------
def write_windowsize_file(window_size, window_size_filepath):
    # ensure output metadata folder is made
    window_size_filepath.parents[0].mkdir(parents=True, exist_ok=True)
    with open(window_size_filepath, 'w') as fh:
        fh.write(window_size)
        return


# ------------------------------- Body Structure ----------------------------------
body = dbc.Container(
    id='tree-viewer-container',
    children=[
        # Data storage
        dcc.Store(id='current-file-memory', storage_type='memory'),
        # dcc.Store(id='input-file-memory'),
        dcc.Store(id='chromosome-length-memory-color-chart'),
        dcc.Store(id='topology-color-chart'),
        dcc.Store(id='window-size'),

        # Modals
        dbc.Modal(
            [
                dbc.ModalHeader("Window Size Required"),
                dbc.ModalBody(
                    children=[
                        dcc.Input(placeholder="Window Size", id='windSize-input'),
                        html.P("Provide Window Size as integer.")
                    ],
                ),
                dbc.ModalFooter(
                    dbc.Button("Submit", id="winsize-submit-button", className="ml-auto")
                ),
            ],
            id="winSize-modal",
            size="xl",
        ),
        dbc.Modal(
            [
                dbc.ModalHeader("New Project"),
                dbc.ModalBody(
                    children=[
                        dbc.Label("Password", html_for="example-password"),
                        dbc.Input(
                            type="password",
                            id="example-password",
                            placeholder="Enter password",
                        ),
                        dbc.FormText(
                            "A password stops mean people taking your stuff", color="secondary"
                        ),
                    ],
                ),
                dbc.ModalFooter(
                    dbc.Button("Submit", id="new-project-submit-button", className="ml-auto")
                ),
            ],
            id="new-project-modal",
            size="xl",
        ),

        # Input File DataFrame
        html.Div(id="input_df", className='hidden-div'),

        # Control Panel
        dbc.Row(
            id='control_panel',
            children=[
                dbc.Col(
                    dbc.Tabs(
                        id='control-tabs',
                        children=[
                            # Data Options
                            dbc.Tab(
                                children=[
                                    # Data options
                                    dbc.Row(
                                        children=[
                                            dbc.Col(
                                                children=[
                                                    dbc.Button(
                                                        id='new-project',
                                                        children=["New Project",]

                                                    )
                                                ],
                                                style={'margin': '5px'},
                                                width=0.5,
                                            ),
                                            # Project ID
                                            dbc.Col(
                                                children=[
                                                    html.Div(
                                                        children=['Project ID:'], 
                                                        style={'color': 'black', 'font-size': FONT_SIZE}
                                                    ),
                                                    dcc.Dropdown(
                                                        id='project-id',
                                                        options=PROJECT_NAMES,
                                                        value=INIT_PROJECT_NAME,
                                                        style={'color': 'black'},
                                                    ),
                                                ],
                                                style={'margin': '5px'},
                                            ),
                                            # Data file
                                            dbc.Col(
                                                children=[
                                                    html.Div(
                                                        children=['Data File:'], 
                                                        style={'color': 'black', 'font-size': FONT_SIZE}
                                                    ),
                                                    dcc.Dropdown(
                                                        id='data_file',
                                                        style={'color': 'black'},
                                                    ),
                                                ],
                                                style={'margin': '5px'},
                                            ),
                                            # Chromosomes
                                            dbc.Col(
                                                children=[
                                                    html.Div(
                                                        children=['Chromosome:'], 
                                                        style={'color': 'black', 'font-size': FONT_SIZE}
                                                    ),
                                                    dcc.Dropdown(
                                                        id='chromosome_options',
                                                        style={'color': 'black'},
                                                    ),
                                                ],
                                                style={'margin': '5px'},
                                            ),
                                            # Topologies
                                            dbc.Col(
                                                children=[
                                                    html.Div(
                                                        children=['Topology:'], 
                                                        style={'color': 'black', 'font-size': FONT_SIZE}
                                                    ),
                                                    dcc.Dropdown(
                                                        id='topology_options',
                                                        style={'color': 'black'},
                                                        multi=True,
                                                    ),
                                                ],
                                                style={'margin': '5px'},
                                            ),
                                            # Alt. Data
                                            dbc.Col(
                                                children=[
                                                    html.Div(
                                                        children=['Additional Data:'], 
                                                        style={'color': 'black', 'font-size': FONT_SIZE}
                                                    ),
                                                    dcc.Dropdown(
                                                        id='alt_data',
                                                        style={'color': 'black'},
                                                        multi=True,
                                                    ),
                                                ],
                                                style={'margin': '5px'},
                                            ),
                                        ],
                                        style={'background': 'orange', 'border-radius': '5px', 'margin-bottom': '10px'},
                                        no_gutters=True,
                                    ),
                                ],
                                label='Data',
                                label_style={
                                    'color': 'white',
                                    'border': '2px orange solid',
                                    'border-radius': '5px',
                                },
                                style={'margin-left': '10px', 'margin-right': '10px'},
                            ),
                            dbc.Tab(
                                children=[
                                    # Graph Toggle Switches
                                    dbc.Row(
                                        children=[
                                            dbc.FormGroup(
                                                [
                                                    html.Div('Main Graphs:', style={'color': 'black', 'font-size': FONT_SIZE}),
                                                    dbc.Checklist(
                                                        id='graph-switches',
                                                        options=[
                                                            {'label': 'Topology Distribution', 'value': 'topo_g'},
                                                            {'label': 'Additional Data', 'value': 'alt_d'},
                                                            {'label': 'Trees', 'value': 'tree_g'}
                                                        ],
                                                        value=['topo_g'],
                                                        switch=True,
                                                        style={'color': 'black', 'display': 'inline'},
                                                        inline=True,
                                                    ),
                                                ],
                                                inline=True,
                                            )
                                        ],
                                        style={
                                            'background': 'orange', 
                                            'padding': '5px',
                                        },
                                        no_gutters=True,
                                    ),
                                    dbc.Row(
                                        children=[
                                            dbc.FormGroup(
                                                [
                                                    html.Div('Topology Distribution Additional Features:', style={'color': 'black', 'font-size': FONT_SIZE}),
                                                    dbc.Checklist(
                                                        id='graph_secondary_options',
                                                        options=[
                                                            {'label': 'Rug Plot Only', 'value': 'topo_gc',},
                                                            {'label': 'Normalized RF-distance', 'value': 'rf_dist',},
                                                            {'label': 'Topology Frequencies', 'value': 'topo_freq',},
                                                        ],
                                                        value=[],
                                                        switch=True,
                                                        style={'color': 'black', 'display': 'inline'},
                                                        inline=True,
                                                    ),
                                                ],
                                                inline=True,
                                            )
                                        ],
                                        style={
                                            'background': 'orange',
                                            'margin-bottom': '10px',
                                            'padding-left': '5px',
                                            'border-radius': '0px 0px 5px 5px',
                                        },
                                        no_gutters=True,
                                    ),
                                ],
                                label='Graph Toggles',
                                label_style={
                                    'color': 'white',
                                    'border': '2px orange solid',
                                    'border-radius': '5px',
                                },
                                style={'margin-left': '10px', 'margin-right': '10px'},
                            ),
                            # Graph Options
                            dbc.Tab(
                                children=[
                                    dbc.Row(
                                        children=[
                                            dbc.Col(
                                                children=[
                                                    html.H6(
                                                        children=[
                                                            'Graph Color Theme:'],
                                                        style={
                                                            'color': 'black',
                                                            'font-size': FONT_SIZE
                                                        }
                                                    ),
                                                    dcc.Dropdown(
                                                        id='template-option',
                                                        options=[{'label': i, 'value': i}
                                                                    for i in GRAPH_TEMPLATES],
                                                        value='plotly_dark',
                                                        style={
                                                            'color': 'black'
                                                        }
                                                    ),
                                                ],
                                                style={
                                                    'margin': '5px',
                                                },
                                            ),
                                            # -----------
                                            dbc.Col(
                                                children=[
                                                    html.H6(
                                                        children=[
                                                            'Tree Style:'],
                                                        style={
                                                            'color': 'black',
                                                            'font-size': FONT_SIZE
                                                        }
                                                    ),
                                                    dcc.Dropdown(
                                                        id='tree-shape-option',
                                                        options=[
                                                            {'label': 'Rectangular', 'value': 'box'},
                                                            {'label': 'Angular', 'value': 'angular'},
                                                                    ],
                                                        value='box',
                                                        style={
                                                            'color': 'black'
                                                        }
                                                    ),
                                                ],
                                                style={
                                                    'margin': '5px',
                                                },
                                            ),
                                            # --- Line Colors ---
                                            dbc.Col(
                                                children=[
                                                    html.H6(
                                                        children=[
                                                            'Line Colors:'],
                                                        style={
                                                            'color': 'black',
                                                            'font-size': FONT_SIZE
                                                        }
                                                    ),
                                                    dcc.Dropdown(
                                                        id='line_color',
                                                        options=[{'label': f'{i} - {len(COLOR_SWATCHES[i])} colors', 'value': i} for i in COLOR_SWATCHES],
                                                        value='Plotly',
                                                        style={
                                                            'color': 'black'
                                                        }
                                                    ),
                                                ],
                                                style={
                                                    'margin': '5px',
                                                },
                                            ),
                                            # -----------
                                            dbc.Col(
                                                children=[
                                                    html.H6(
                                                        children=[
                                                            'Snapshot File Type:'],
                                                        style={
                                                            'color': 'black',
                                                            'font-size': FONT_SIZE
                                                        }
                                                    ),
                                                    dcc.Dropdown(
                                                        id='snapshot-file-option',
                                                        options=[{'label': i, 'value': i}
                                                                    for i in SNAPSHOT_FILE_OPTIONS],
                                                        value='jpeg',
                                                        style={
                                                            'color': 'black'
                                                        }
                                                    ),
                                                ],
                                                style={
                                                    'margin': '5px',
                                                },
                                            ),
                                        ],
                                        style={'background': 'orange', 'margin-bottom': '5px', 'border-radius': '5px'},
                                        no_gutters=True,
                                    ),
                                ],
                                label='Graph Options',
                                label_style={
                                    'border': '2px orange solid',
                                    'border-radius': '5px',
                                },
                                style={'margin-left': '10px', 'margin-right': '10px'},
                            ),
                        ],
                        style={'margin': '10px'}
                    ),
                ),
            ],
            className='control-panel',
            no_gutters=True,
        ),
        # Graphs
        dbc.Row(
            id='graph_row',
            children=[
                # --- Main Topology Graph + RF Graph ---
                dbc.Col(
                    children=[
                        html.Div(
                            id='topology_graph_div',
                            children=[
                                dcc.Graph(
                                    id='topology_graph',
                                    figure=tree_utils.init_data_graph('plotly_dark'),
                                    style={
                                        'height': '30vh',
                                        'margin-right': '50wv',
                                        'margin-left': '50wv',
                                        'margin-top': '50wv',
                                    },
                                    loading_state={
                                        'is_loading': True
                                    },
                                    config=dict(responsive=False, displayModeBar=False),
                                )
                            ],
                        ),
                        html.Div(id='rfdist_div'),
                        html.Div(id='topoFreq_div'),
                    ],
                    width=12,
                ),
                # --- Alt. Data Graph ---
                dbc.Col(
                    html.Div(
                        id='alt_data_div',
                        style={
                            'height': '20vh',
                            'display': 'none',
                            # 'margin-bottom': '5px'
                            # 'padding-left': '10px',
                            # 'padding-right': '10px',
                            # 'margin': '10px',
                        },
                    ),
                    width=12,
                ),
                # --- Trees ---
                dbc.Col(
                    html.Div(
                        id='tree_div',
                        children=[],
                        style={
                            # 'padding': '5px',
                        },
                    ),
                    width=12,
                ),
            ],
            className='div-boxes',
            no_gutters=True,
        ),
    ],
    className='container-div',
    fluid=True,
)

nav = navbar.Navbar('Tree Viewer')
layout = html.Div([nav, body])

##################################### Callbacks #####################################
# ----------------------- All graph display and style controls -----------------------
@app.callback(
    [Output(component_id='topology_graph_div', component_property='style'),
    Output(component_id='alt_data_div', component_property='style'),
    Output(component_id='tree_div', component_property='style'),
    Output(component_id='rfdist_div', component_property='style'),
    Output(component_id='topoFreq_div', component_property='style'),],
    [Input(component_id='graph-switches', component_property='value'),
    Input(component_id='topology_options', component_property='value'),
    Input(component_id='alt_data', component_property='value'),
    Input(component_id='graph_secondary_options', component_property='value'),])
def hide_graph_divs(open_graphs, topos, alt_data_vals, secondary_options):
    '''This callback controls the graphs display and styling'''
    
    if type(alt_data_vals) == str:
        alt_data_vals = [alt_data_vals]

    # Topology Graph + NormRF graph if turned on
    if ('topo_g' in open_graphs) and ('rf_dist' in secondary_options):
        topology_graph_style = {
            'display': True, 
            'height': '30vh', 
            'margin-bottom': '2px',
        }
        rfdist_style = {
            'display': True,
            'height': '25vh', 
            'margin-bottom': '5px',
        }
        topoFreq_style={'display': 'none'}
    elif ('topo_g' in open_graphs) and ('topo_freq' in secondary_options):
        topology_graph_style = {
            'display': True, 
            'height': '30vh', 
            'margin-bottom': '2px',
        }
        rfdist_style={'display': 'none'}
        topoFreq_style = {
            'display': True,
            'height': '25vh', 
            'margin-bottom': '5px',
        }
    elif ('topo_g' in open_graphs) and ('topo_freq' in secondary_options) and ('rf_dist' in secondary_options):
        topology_graph_style = {
            'display': True, 
            'height': '30vh', 
            'margin-bottom': '2px',
        }
        rfdist_style = {
            'display': True,
            'height': '25vh', 
            'margin-bottom': '5px',
        }
        topoFreq_style = {
            'display': True,
            'height': '25vh', 
            'margin-bottom': '5px',
        }
    elif ('topo_g' in open_graphs):
        topology_graph_style = {
            'display': True, 
            'height': '30vh', 
            'margin-bottom': '2px',
        }
        rfdist_style={'display': 'none'}
        topoFreq_style={'display': 'none'}
    else:
        topology_graph_style = {'display': 'none'}
        rfdist_style={'display': 'none'}
        topoFreq_style={'display': 'none'}

    # Alternative Data Graph style
    if 'alt_d' in open_graphs:
        alt_data_graph_style = {
            'display': True, 
            'height': f'{20*len(alt_data_vals)}vh',
            'margin-bottom': '5px',
        }
    else:
        alt_data_graph_style = {'display': 'none'}
    
    # Tree Graph Style
    if 'tree_g' in open_graphs:
        tree_graph_style = {
            'display': True, 
            'height': f'{50*(len(topos)//3)}vh',
        }
    else:
        tree_graph_style = {'display': 'none'}
    
    return topology_graph_style, alt_data_graph_style, tree_graph_style, rfdist_style, topoFreq_style
    

# 1. Set data file options with init project ID
@app.callback([Output(component_id='data_file', component_property='options'),
              Output(component_id='data_file', component_property='value')],
              [Input(component_id='project-id', component_property='value')])
def set_data_file_dropdown_options(p):
    proj_path = TREE_DATA_DIR / str(p) / 'topology_files/'
    files = [{'label': t.stem, 'value': t.name} for t in proj_path.iterdir()]
    init_value = files[0]['value']
    return files, init_value



# 1. Set data file options with init project ID
@app.callback(Output(component_id='current-file-memory', component_property='data'),
              [Input(component_id='project-id', component_property='value'),
              Input(component_id='data_file', component_property='value')])
def set_data_file_dropdown_options(project_id, datafile):
    tree_file = Path('src/data/tree_viewer_data') / str(project_id) /'topology_files' / str(datafile)
    df = pd.read_excel(tree_file)
    df[['TopologyID']] = df[['TopologyID']].fillna(value="NoData")
    # print(df)
    return df.to_json()



# 2. Use data file value to set all other options
@app.callback(Output(component_id='topology-color-chart', component_property='data'),
              [Input(component_id='data_file', component_property='value'),
              Input(component_id='project-id', component_property='value'),
              Input(component_id='line_color', component_property='value'),])
def set_topology_colors(datafile_value, project_id, line_color):
    tree_file = Path('src/data/tree_viewer_data') / str(project_id) /'topology_files' / str(datafile_value)
    color_set = COLOR_SWATCHES[line_color]
    topo_colors = tree_utils.set_topology_colors(tree_file, color_set)
    return topo_colors


# 3. Set chromosome dropdown options + value 
@app.callback(Output(component_id='chromosome_options', component_property='options'),
              [Input(component_id='current-file-memory', component_property='data')])
def set_chromosome_options(df):
    df = pd.read_json(df)
    unique_chroms = df["Chromosome"].unique()
    chromosome_options = [{'label': i, 'value': i} for i in sorted(unique_chroms)]
    return chromosome_options


@app.callback(Output(component_id='chromosome_options', component_property='value'),
              [Input(component_id='chromosome_options', component_property='options'),])
def set_chromosome_value(chromOptions):
    return chromOptions[0]['value']


# 4. Set topology dropdown options + value 
@app.callback(Output(component_id='topology_options', component_property='options'),
              [Input(component_id='current-file-memory', component_property='data'),
              Input(component_id='chromosome_options', component_property='value')])
def set_topology_options(df, chromValue):
    df = pd.read_json(df)
    df = df[df['Chromosome'] == chromValue]
    sorted_topologies = df.assign(freq=df.groupby("TopologyID")["TopologyID"].transform('count')).sort_values(by=['freq',"TopologyID"],ascending=[False,True]).loc[:,["TopologyID"]]
    topologyOptions = [{'label': i, 'value': i} for i in sorted_topologies["TopologyID"].unique() if i]
    return topologyOptions


@app.callback(Output(component_id='topology_options', component_property='value'),
              [Input(component_id='topology_options', component_property='options'),])
def set_topology_values(topoOptions):
    return [c['value'] for c in topoOptions[:3]]


# 5. Set alt data dropdown options + value 
@app.callback(Output(component_id='alt_data', component_property='options'),
              [Input(component_id='current-file-memory', component_property='data'),
              Input(component_id='chromosome_options', component_property='value')])
def set_alt_data_options(df, chromValue):
    df = pd.read_json(df)
    alt_data_cols = [col for col in df.columns][4:]
    alt_data_options = [{'label': i, 'value': i} for i in alt_data_cols]
    return alt_data_options


@app.callback(Output(component_id='alt_data', component_property='value'),
              [Input(component_id='alt_data', component_property='options'),])
def set_alt_data_values(alt_data_options):
    return alt_data_options[0]['value']


# 6. Set chromosome bed_file into data Store 
@app.callback(Output(component_id='chromosome-length-memory-color-chart', component_property='data'),
             [Input(component_id='project-id', component_property='value')])
def set_chromosome_data(project_file):
    tree_path = Path('src/data/tree_viewer_data') / str(project_file) / 'metadata'
    full_file_list = [f for f in tree_path.iterdir() if f.is_file()]
    clean_file_list = []
    # Remove any hidden dot files
    for file in full_file_list:
        if file.name[0] == '.':
            continue
        elif file.suffix == '.bed':
            clean_file_list.append(file)
        else:
            continue
    # There should only be one bed file in the metadata folder
    assert len(clean_file_list) == 1
    file_dataframe = data_utils.build_file_json(file=clean_file_list[0])
    return file_dataframe


@app.callback([Output(component_id='window-size', component_property='data'),
               Output(component_id='winSize-modal', component_property='is_open')],
               [Input(component_id='project-id', component_property='value'),
               Input(component_id='winsize-submit-button', component_property='n_clicks'),
               Input(component_id='windSize-input', component_property='value')],)
def set_window_size(project_file, submit_button, window_size_input):
    '''Expects there to be a windowSize.txt file, if not raise modal asking for window size + write file'''
    window_size_filepath = Path(f'src/data/tree_viewer_data/{str(project_file)}/metadata/windowSize.txt')
    # If windowSize file is not found, raise modal asking for window size 
    # and write to windowSize.txt in the current projects metadata directory
    ctx = dash.callback_context  
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'winsize-submit-button':
        write_windowsize_file(window_size_input, window_size_filepath)
        return window_size_input, False
    try:
        with open(window_size_filepath, 'r') as fh:
            for l in fh:
                window_size = int(l.strip())
                break
            return window_size, False
    except FileNotFoundError:
        # This return will fire this callback again and will open modal to input window size
        return 0, True


# ---------------------- Make Graphs + Plot ----------------------
@app.callback(
    # Outputs
    [Output(component_id='topology_graph_div', component_property='children'),
    Output(component_id='alt_data_div', component_property='children'),
    Output(component_id='tree_div', component_property='children'),],
    # Inputs
    [Input(component_id='graph-switches', component_property='value'),
    Input(component_id='graph_secondary_options', component_property='value'),
    Input(component_id='alt_data', component_property='value'),
    Input(component_id='data_file', component_property='value'),
    Input(component_id='project-id', component_property='value'),
    Input(component_id='chromosome-length-memory-color-chart', component_property='data'),
    Input(component_id='chromosome_options', component_property='value'),
    Input(component_id='topology_options', component_property='value'),
    Input(component_id='template-option', component_property='value'),
    Input(component_id='snapshot-file-option', component_property='value'),
    Input(component_id='tree-shape-option', component_property='value'),
    Input(component_id='topology-color-chart', component_property='data'),],
    # States
    [State("winSize-modal", "is_open")],)
def plot_graphs(
    graph_switches,
    graph_switch_options,
    alt_dropdown_options,
    datafile_val,
    project_id,
    chromosome_length_data,
    chromosome,
    topology,
    template,
    snapshot_file_type,
    tree_shape,
    color_mapping,
    windSize_modal,
):
    # If window size modal is open, prevent update of graph
    if windSize_modal:
        raise PreventUpdate

    # Read in topology data
    tree_file = Path('src/data/tree_viewer_data') / str(project_id) /'topology_files' / str(datafile_val)
    topology_df = pd.read_excel(tree_file)
    topology_df[['TopologyID']] = topology_df[['TopologyID']].fillna(value="NoData")

    # Put alt data option into list if only one selected.
    if type(alt_dropdown_options) == str:
        alt_dropdown_options = [alt_dropdown_options]

    num_of_graphs_to_plot = len(graph_switches)

    topology_graph = [tree_utils.no_data_graph(template)]
    alt_graphs = []
    tree_graphs = []

    for graph in graph_switches:
        if graph == 'topo_g':
            if not topology:
                pass
            else:
                if 'topo_gc' not in graph_switch_options:
                    # Build histogram + Heatmap Figures
                    combined_histogram = tree_utils.build_combined_topology_graph(
                        topology_df,
                        chromosome_length_data,
                        chromosome,
                        template,
                        topology,
                        num_of_graphs_to_plot,
                        color_mapping,
                    )
                    topology_graph = [
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id='topology_graph',
                                    figure=combined_histogram,
                                    config=dict(
                                        toImageButtonOptions=dict(
                                            format=snapshot_file_type,
                                            filename="Graph_Name",
                                        ),
                                    ),
                                    # style={'height': '30vh', 'width': '100%'}
                                    className='topograph'
                                ),
                            ],
                        )
                    ]
                else:
                    # Build histogram + Heatmap Figures
                    single_histogram = tree_utils.build_singular_topology_graph(
                        topology_df,
                        chromosome_length_data,
                        chromosome,
                        template,
                        topology,
                        num_of_graphs_to_plot,
                        color_mapping,
                    )
                    topology_graph = [
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id='topology_graph',
                                    figure=single_histogram,
                                    config=dict(
                                        toImageButtonOptions=dict(
                                            format=snapshot_file_type,
                                            filename="Graph_Name",
                                        ),
                                    ),
                                    # style={'height': '30vh', 'width': '100%'},
                                    className='topograph'
                                )
                            ],
                        )
                    ]
        elif graph == 'alt_d':
            for alt_data in alt_dropdown_options:
                alt_graph = tree_utils.build_alt_data_graph(
                    alt_data,
                    topology_df,
                    chromosome_length_data,
                    chromosome,
                    template,
                    topology,
                    num_of_graphs_to_plot,
                )
                alt_graphs.append(
                    html.Div(
                        dcc.Graph(
                            figure=alt_graph,
                            config=dict(
                                editable=True,
                                toImageButtonOptions=dict(
                                    format=snapshot_file_type,
                                    filename="Graph_Name",
                                ),
                            ),
                            style={
                                'height':'20vh',
                            },
                        )
                    )
                )
        elif graph == 'tree_g':
            tree_cols = topology_df.columns.to_list()

            if type(topology) == str:
                topologies = [topology]
            elif type(topology) == int:
                topologies = [topology]
            else:
                topologies = topology

            tree_divs = []

            for tops in topologies:
                # Filter data
                wanted_chroms = topology_df[topology_df["Chromosome"] == chromosome]
                wanted_rows = wanted_chroms[wanted_chroms["TopologyID"] == tops]

                # Grab tree (Should only be one possible tree to use!!!)
                try:
                    first_tree = wanted_rows["NewickTree"].unique()[0]
                except IndexError:
                    first_tree = '();'

                tree = tree_utils.DrawTree(StringIO(data_utils.newick_semicolon_check(first_tree.strip())))

                if tree_shape == 'box':
                    fig = tree.create_square_tree()

                elif tree_shape == 'angular':
                    # Build nodes and edges of graph
                    fig = tree.create_angular_tree()

                tree_divs.append(
                    
                    dbc.Col(
                        children=[
                            html.H6(f' {tops}',
                                    style={
                                        'color': 'black',
                                        'font-size': FONT_SIZE,
                                    }
                            ),
                            html.Div(
                                children=[
                                    dcc.Graph(
                                        figure=fig,
                                        style={'width': '100%', 'background-color': 'black'},
                                        config=dict(
                                            toImageButtonOptions=dict(
                                                format=snapshot_file_type,
                                                filename="Graph_Name",
                                            ),
                                        ),
                                    )
                                ],
                                style={
                                    'width': '100%',
                                }
                            ),
                        ],
                        width=4
                    ),
                    # dbc.Col(
                    #     children=[
                    #         html.Div(
                    #             'HELLO PLEASE WORK!',
                    #             style={
                    #                 'background-color': 'black',
                    #                 'height': '100%',
                    #                 'width': '100%',
                    #                 'padding': '5px',
                    #                 'border': '2px orange solid',
                    #             },
                    #         )
                    #     ],
                    #     width=4
                    # )
                   
                )
                
                continue 
            tree_graphs.append(
                    dbc.Row(
                        children=tree_divs,
                        style={
                            'border': '2px black solid',
                            'background': 'white',
                        },
                        no_gutters=True
                    )
                )
    return topology_graph, alt_graphs, tree_graphs

# ---------------------- Topology Distribution Alt Calculations ---------------------
@app.callback(
    Output(component_id='rfdist_div', component_property='children'),
    [Input(component_id='graph_secondary_options', component_property='value'),
    Input(component_id='topology_graph', component_property='hoverData'),
    Input(component_id='data_file', component_property='value'),
    Input(component_id='project-id', component_property='value'),
    Input(component_id='chromosome_options', component_property='value'),
    Input(component_id='template-option', component_property='value'),
    Input(component_id='snapshot-file-option', component_property='value'),
    Input(component_id='window-size', component_property='data'),
    Input(component_id='topology-color-chart', component_property='data'),
    Input(component_id='topology_options', component_property='value'),
    Input(component_id='current-file-memory', component_property='data'),])
def calc_rf_distance(
    graph_options,
    hoverdata,
    datafile_val,
    project_id,
    curr_chrom,
    template,
    snapshot_file_type,
    window_size,
    color_mapping,
    topoology_options,
    df
):
    rf_plot = []
    if 'rf_dist' not in graph_options:
        return None
    elif not hoverdata:
        rf_plot.append(
            dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            html.Div(
                                children=[
                                    dcc.Graph(
                                        figure=tree_utils.init_RF_graph(template),
                                        style={'height': '25vh', 'width': '100%', 'background-color': 'black'},
                                        config=dict(
                                            toImageButtonOptions=dict(
                                                format=snapshot_file_type,
                                                filename="Graph_Name",
                                            ),
                                        ),
                                    )
                                ],
                                style={
                                    'width': '100%',
                                }
                            ),
                        ],
                        width=12
                    ),
                ],
                style={
                    # 'border': '2px black solid',
                    # 'margin': '5px',
                },
                no_gutters=True
            )
        )
        return rf_plot
    else:
        try:
            print('start lookup')
            # Collect window pos based on hoverdata
            x_pos = tree_utils.get_RFxpos(hoverdata, window_size)
            print('got xpos')
            print(x_pos)
            # Read in topology data
            # tree_file = Path('src/data/tree_viewer_data') / str(project_id) /'topology_files' / str(datafile_val)
            # input_data = query_data(tree_file)
            # input_data = pd.read_excel(tree_file)
            input_data = pd.read_json(df)
            input_data[['TopologyID']] = input_data[['TopologyID']].fillna(value="NoData")
            print('get chrom info')
            chrom_info = input_data[(input_data['Chromosome'] == curr_chrom)]
            chrom_info.sort_values(by='Window', inplace=True)
            chrom_info.reset_index(drop=True, inplace=True)
            print('get poi info')
            poi_info = chrom_info[chrom_info['Window'] == x_pos]
            print(poi_info)
            poi = poi_info.index.to_list()[0]
            
            print('reduce df')
            rfdist_df = chrom_info[(chrom_info.index >= poi - 10) & (chrom_info.index <= poi + 10) & (chrom_info.index != poi)]
            rfdist_df = pd.concat([poi_info, rfdist_df])
            rfdist_df.sort_values(by='Window', inplace=True)
            rfdist_df.reset_index(drop=True, inplace=True)
            t1 = poi_info['NewickTree'].to_list()[0]
            rf_dist_collect = []
            for t2 in rfdist_df['NewickTree']:
                try:
                    rfd = tree_utils.RFDistance(t1, t2).NormRF()
                except TreeError:
                    # raise modal
                    raise PreventUpdate
                
                if type(rfd) == str:
                    rfd = np.nan
                    # rfd = -1
                rf_dist_collect.append(rfd)
                continue
            rfdist_df['NormRF'] = rf_dist_collect
            print("building graphs")
            heatmap = tree_utils.build_RF_heatmap(
                rfdist_df,
                template,
                color_mapping,
            )
            rf_plot.append(
                dbc.Row(
                    children=[
                        dbc.Col(
                            children=[
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            figure=heatmap,
                                            style={'height': '25vh', 'width': '100%', 'background-color': 'black'},
                                            config=dict(
                                                toImageButtonOptions=dict(
                                                    format=snapshot_file_type,
                                                    filename="Graph_Name",
                                                ),
                                            ),
                                        )
                                    ],
                                    style={
                                        'width': '100%',
                                    }
                                ),
                            ],
                            width=12
                        ),
                    ],
                    style={'border': '2px black solid'},
                    no_gutters=True
                )
            )
            print('end lookup')
            return rf_plot
        except IndexError:
            return None
    
@app.callback(
    Output(component_id='topoFreq_div', component_property='children'),
    [Input(component_id='graph_secondary_options', component_property='value'),
    Input(component_id='data_file', component_property='value'),
    Input(component_id='project-id', component_property='value'),
    Input(component_id='chromosome_options', component_property='value'),])
def calc_topology_frequencies(
    graph_options,
    datafile,
    project_id,
    curr_chrom,
):
    topoFreq_plot = []
    if 'topo_freq' not in graph_options:
        return None
    else:
        # --- Collect topop frequency data
        tree_file = Path('src/data/tree_viewer_data') / str(project_id) /'topology_files' / str(datafile)
        # df = query_data(tree_file)
        df = pd.read_excel(tree_file)
        chrom_df = df[df["Chromosome"] == curr_chrom]
        topoCounts = chrom_df["TopologyID"].value_counts()
        totalTopologies = sum([c for c in topoCounts])
        frequencies = {t: round((f/totalTopologies), 4) for t, f in zip(topoCounts.index, topoCounts)}
        # --- Ouput data into DataTable
        topoFreq_plot.append(
            dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            html.Div(
                                children=[
                                    html.Div('Topology Frequency', style={'align': 'center'}),
                                    dt.DataTable(
                                        id='topoFreq_DT',
                                        columns=[{"name": i, "id": i} for i in frequencies.keys()],
                                        data=[frequencies],
                                        style_cell={
                                            'color': 'black',
                                            'textAlign': 'center',
                                        },
                                    ),
                                ],
                                style={
                                    'width': '100%',
                                }
                            ),
                        ],
                        width=12
                    ),
                ],
                style={'border': '2px black solid'},
                no_gutters=True
            )
        )
        return topoFreq_plot

    