from apps.tree_viewer import FONT_SIZE
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from apps import navbar
from app import app

nav = navbar.Navbar()

body = dbc.Container(
        children=[
            dbc.Row(
                id="updates-row",
                className="ml-12",
                children=[
                    dbc.Col(
                        id="update-display",
                        children=[
                            dcc.Markdown(
                                children=[
                                    """
                                        # Welcome to Tree House Explorer!
                                    """
                                ],
                                style={
                                    "text-align": "center",
                                    "text-decoration": "underline",
                                },
                            ),
                            dcc.Markdown(
                                children=[
                                    """
                                        _Tree House Explorer is a novel genome browser for comparative phylogenomics._
                                    """
                                ],
                                style={
                                    "text-align": "center",
                                    "font-size": "25px",
                                    # "text-decoration": "underline",
                                },
                            ),
                            dbc.CardDeck(
                                children=[
                                    dbc.Card(
                                        children=[
                                            dbc.CardBody(
                                                children=[
                                                    html.Div(
                                                        children=[
                                                            html.H5(
                                                                "Tree Viewer",
                                                                className="card-title",
                                                                style={
                                                                    "text-decoration": "underline",
                                                                    "font-size": "25px",
                                                                },
                                                            ),
                                                            dbc.CardLink("Go!", href="/apps/tree_viewer", style={'margin': '2px 4px 4px 10px', 'font-size': FONT_SIZE}),
                                                        ],
                                                        style={'display': 'flex'},
                                                    ),
                                                    dcc.Markdown(
                                                        children=[
                                                            """
                                                                * Ideal for analyzing topological variation across genomes and visually inspecting tree stucture simultaneously.
                                                                * Can include recombination data, G-C content across chromosomes, and more!
                                                            """
                                                        ],
                                                        style={
                                                            # "text-align": "center",
                                                            "font-size": "15px",
                                                            "align": "inline-block",
                                                        },
                                                    ),
                                                    
                                                ],
                                            ),
                                        ],
                                        color="warning",
                                        outline=True,
                                        style={
                                            "height": "20vh",
                                            "width": "50vw",
                                            "margin": "10px",
                                            # "margin-left": "15px",
                                            # "margin-right": "15px",
                                        },
                                    ),
                                    dbc.Card(
                                        children=[
                                            dbc.CardBody(
                                                children=[
                                                    html.Div(
                                                        children=[
                                                            
                                                            html.H5(
                                                                "p-Distance Tracer",
                                                                className="card-title",
                                                                style={
                                                                    "text-decoration": "underline",
                                                                    "font-size": "25px",
                                                                },
                                                            ),
                                                            dbc.CardLink("Go!", href="/apps/p_distance_viewer", style={'margin': '2px 4px 4px 10px', 'font-size': FONT_SIZE}),
                                                        ],
                                                        style={'display': 'flex'},
                                                    ),
                                                    dcc.Markdown(
                                                        children=[
                                                            """
                                                                * Easily explore p-distance data per-chromosome or across all chromosomes.
                                                                * Plotting is dynamic, customizable, and features several tools to highlight regions of interest and output as-is plots to your local machine.
                                                            """
                                                        ],
                                                        style={
                                                            "font-size": "15px",
                                                            "align": "inline-block",
                                                        },
                                                    ),
                                                    
                                                ],
                                            ),
                                        ],
                                        color="warning",
                                        outline=True,
                                        style={
                                            "height": "20vh",
                                            "width": "50vw",
                                            "margin": "10px",
                                        },
                                    ),
                                ],
                            ),
                        ],
                        width=12,
                        style={
                            "height": "100%",
                            "border":"2px #F39C12 solid",
                            "border-radius": "5px",
                            "margin": "10px",
                            "background": "primary",
                        },
                    ),
                ],
                justify="center",
                align="center",
                # form=True,
                key='updates-row',
                style={
                    "height": "70vh",
                    # "border":"2px #F39C12 solid",
                    # "border-radius": "5px",
                    # "margin": "10px",
                    # "background": "primary",
                },
            ),
            # Card deck of programs
            # dbc.Row(
            #     children=[
            #         dbc.CardDeck(
            #             id='card-deck',
            #             children=[
            #                 # Tree Viewer Card
            #                 dbc.Card(
            #                     children=[
            #                         dbc.CardBody(
            #                             children=[
            #                                 html.Div(
            #                                     children=[
            #                                         html.H5(
            #                                             "Tree Viewer: ",
            #                                             className="card-title",
            #                                             style={
            #                                                 "text-decoration": "underline",
            #                                                 'margin-right': '10px'
            #                                             },
            #                                         ),
            #                                         dbc.CardLink("Go!", href="/apps/tree_viewer"),
            #                                     ],
            #                                     style={'display': 'flex'}
            #                                 ),
            #                                 html.P(
            #                                     "Prior to using the Tree Viewer tool, load in your tree information and metadata files in the Tree Viewer Data Preparation Tool."
            #                                 ),
            #                             ],
            #                         ),
            #                         # dbc.CardImg(
            #                         #     src="static\images\TreeViewer_homepage.PNG",
            #                         #     top=True,
            #                         #     style={
            #                         #         # "height": "40vh",
            #                         #         # "width": "100%",
            #                         #         "padding-top": "10px",
            #                         #         "padding-left": "10px",
            #                         #         "padding-right": "10px",
            #                         #     }
            #                         # ),
            #                     ],
            #                     color="warning",
            #                     outline=True,
            #                 ),
            #                 # P-Distance Card
            #                 dbc.Card(
            #                     children=[
            #                         dbc.CardBody(
            #                             [
            #                                 html.Div(
            #                                     children=[
            #                                         html.H5(
            #                                             "p-Distance Tracer: ",
            #                                             className="card-title",
            #                                             style={
            #                                                 "text-decoration": "underline",
            #                                                 'margin-right': '10px'
            #                                             },
            #                                         ),
            #                                         dbc.CardLink("Go!", href="/apps/p_distance_viewer"),
            #                                     ],
            #                                     style={'display': 'flex'}
            #                                 ),
            #                                 html.P(
            #                                     "Prior to using the P-Distance graphing tool, run your multi-alignment file through the P-Distance Window Calculator."
            #                                 ),
                                            
            #                             ]
            #                         ),
            #                         # dbc.CardImg(
            #                         #     src="static\images\pDistViewer_homepage.PNG",
            #                         #     top=True,
            #                         #     style={
            #                         #         # "height": "40vh",
            #                         #         # "width": "100%",
            #                         #         "padding-top": "10px",
            #                         #         "padding-left": "10px",
            #                         #         "padding-right": "10px",
            #                         #     }
            #                         # ),
            #                     ],
            #                     color="warning",
            #                     outline=True,
            #                 ),
            #                 # Time Tree Card
            #                 # dbc.Card(
            #                 #     children=[
            #                 #         dbc.CardImg(
            #                 #             src="/static/images/coming_soon.png",
            #                 #             top=True,
            #                 #             style={
            #                 #                 "padding-top": "10px",
            #                 #                 "padding-left": "10px",
            #                 #                 "padding-right": "10px",
            #                 #             }
            #                 #         ),
            #                 #         dbc.CardBody(
            #                 #             [
            #                 #                 html.H5(
            #                 #                     "Time Tree", 
            #                 #                     className="card-title",
            #                 #                     style={
            #                 #                         "text-decoration": "underline"
            #                 #                     },
            #                 #                 ),
            #                 #                 html.P(
            #                 #                     ""
            #                 #                 ),
            #                 #                 dbc.CardLink("Go!", href="/apps/data_prep"),
            #                 #             ]
            #                 #         ),
            #                 #     ],
            #                 #     color="warning",
            #                 #     outline=True,
            #                 #     style={
            #                 #         "height": "750px",
            #                 #         "width": "95vw",
            #                 #         # "margin-left": "15px",
            #                 #         # "margin-right": "15px",
            #                 #     },
            #                 # ),
                                                     
            #                 # Coverage Graphing Card
            #                 # dbc.Card(
            #                 #     children=[
            #                 #         dbc.CardImg(
            #                 #             src="/static/images/coming_soon.png", 
            #                 #             top=True,
            #                 #             style={
            #                 #                 "padding-top": "10px",
            #                 #                 "padding-left": "10px",
            #                 #                 "padding-right": "10px",
            #                 #             }
            #                 #         ),
            #                 #         dbc.CardBody(
            #                 #             [
            #                 #                 html.H5(
            #                 #                     "Coverage Graphing Tool", 
            #                 #                     className="card-title",
            #                 #                     style={
            #                 #                         "text-decoration": "underline"
            #                 #                     },
            #                 #                 ),
            #                 #                 html.P(
            #                 #                     ""
            #                 #                 ),
            #                 #                 dbc.CardLink("Go!", href="/apps/coverage_graphing"),
            #                 #             ]
            #                 #         ),
            #                 #     ],
            #                 #     color="warning",
            #                 #     outline=True,
            #                 #     style={
            #                 #         "height": "750px",
            #                 #         "width": "95vw",
            #                 #         # "margin-left": "15px",
            #                 #         # "margin-right": "15px",
            #                 #     },
            #                 # ),
            #                  # Sequence Viewer Card
            #                 # dbc.Card(
            #                 #     children=[
            #                 #         dbc.CardImg(
            #                 #             src="/static/images/coming_soon.png", 
            #                 #             top=True,
            #                 #             style={
            #                 #                 "padding-top": "10px",
            #                 #                 "padding-left": "10px",
            #                 #                 "padding-right": "10px",
            #                 #             }
            #                 #         ),
            #                 #         dbc.CardBody(
            #                 #             [
            #                 #                 html.H5(
            #                 #                     "Sequence Viewer", 
            #                 #                     className="card-title",
            #                 #                     style={
            #                 #                         "text-decoration": "underline"
            #                 #                     },
            #                 #                 ),
            #                 #                 html.P(
            #                 #                     ""
            #                 #                 ),
            #                 #                 dbc.CardLink("Go!", href="/apps/sequence_viewer"),
            #                 #             ]
            #                 #         ),
            #                 #     ],
            #                 #     color="warning",
            #                 #     outline=True,
            #                 #     style={
            #                 #         "height": "750px",
            #                 #         "width": "95vw",
            #                 #     },
            #                 # ),
            #                 # --- Sandbox ---
            #                 # dbc.Card(
            #                 #     children=[                                  
            #                 #         dbc.CardBody(
            #                 #             [
            #                 #                 html.H5(
            #                 #                     "SandBox", 
            #                 #                     className="card-title", 
            #                 #                     style={
            #                 #                         "text-decoration": "underline"
            #                 #                     },
            #                 #                 ),
            #                 #                 html.P(
            #                 #                     "Prior to using the P-Distance graphing tool, run your multi-alignment file through the P-Distance Window Calculator."
            #                 #                 ),
            #                 #                 dbc.CardLink("Go!", href="/apps/sandbox"),
            #                 #             ]
            #                 #         ),
            #                 #     ],
            #                 #     color="warning",
            #                 #     outline=True,
            #                 #     style={
            #                 #         "height": "750px",
            #                 #         "width": "95vw",
            #                 #     },
            #                 # ), 
                            
            #                 # Data Preparation Card
            #                 # dbc.Card(
            #                 #     children=[
            #                 #         dbc.CardImg(
            #                 #             src="/static/images/coming_soon.png", 
            #                 #             top=True,
            #                 #             style={
            #                 #                 "padding-top": "10px",
            #                 #                 "padding-left": "10px",
            #                 #                 "padding-right": "10px",
            #                 #             }
            #                 #         ),
            #                 #         dbc.CardBody(
            #                 #             [
            #                 #                 html.H5(
            #                 #                     "Data Preparation", 
            #                 #                     className="card-title",
            #                 #                     style={
            #                 #                         "text-decoration": "underline"
            #                 #                     },
            #                 #                 ),
            #                 #                 html.P(
            #                 #                     ""
            #                 #                 ),
            #                 #                 dbc.CardLink("Go!", href="/apps/data_prep"),
            #                 #             ]
            #                 #         ),
            #                 #     ],
            #                 #     color="warning",
            #                 #     outline=True,
            #                 #     style={
            #                 #         "height": "750px",
            #                 #         "width": "95vw",
            #                 #     },
            #                 # ),                            
            #             ],
            #             style={
            #                 "padding-left": "20px",
            #                 "padding-right": "20px",
            #                 "margin": "10px",
            #             },
            #             # className="wd-12"
            #         )
            #     ],
            #     style={
            #         # "height": "30vh",
            #         "border":"2px #F39C12 solid",
            #         "border-radius": "5px",
            #         "margin-top": "10px",
            #         "margin-bottom": "10px",
            #         "background": "primary",
            #     },
            #     justify="center",
            #     key='tools-row',
            # ),
        ],
    fluid=True,
    key='home_container',
    )

layout = html.Div([
            nav,
            body
        ])
