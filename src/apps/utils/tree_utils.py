from pathlib import Path
from io import StringIO

from Bio import Phylo
from ete3 import Tree
import math
import numpy as np
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy

from apps.utils import data_utils

class DrawTree():
    def __init__(self, newicktree):
        self.newicktree = Phylo.read(newicktree, "newick")

    def create_square_tree(self):

        def get_x_coordinates(tree):
            """Associates to each clade an x-coord.
            returns dict {clade: x-coord}
            """
            xcoords = tree.depths()
            xcoord_dict = dict(xcoords)

            first_node = [k for k in xcoords][0]
            xcoords[first_node] = -0.01

            # tree.depth() maps tree clades to depths (by branch length).
            # returns a dict {clade: depth} where clade runs over all Clade instances of the tree, and depth is the distance from root to clade

            #  If there are no branch lengths, assign unit branch lengths
            if not max(xcoords.values()):
                xcoords = tree.depths(unit_branch_lengths=True)
            return xcoords

        def get_y_coordinates(tree, dist=1.3):
            """
            returns  dict {clade: y-coord}
            The y-coordinates are  (float) multiple of integers (i*dist below)
            dist depends on the number of tree leafs
            """
            maxheight = tree.count_terminals()  # Counts the number of tree leafs.
            # Rows are defined by the tips/leafs
            ycoords = dict(
                (leaf, maxheight - i * dist)
                for i, leaf in enumerate(reversed(tree.get_terminals()))
            )

            def calc_row(clade):
                for subclade in clade:
                    if subclade not in ycoords:
                        calc_row(subclade)
                ycoords[clade] = (ycoords[clade.clades[0]] +
                                  ycoords[clade.clades[-1]]) / 2

            if tree.root.clades:
                calc_row(tree.root)
            return ycoords

        def get_clade_lines(
            orientation="horizontal",
            y_curr=0,
            x_start=0,
            x_curr=0,
            y_bot=0,
            y_top=0,
            line_color="rgb(25,25,25)",
            line_width=0.5,
            root_clade = False
        ):
            """define a shape of type 'line', for branch
            """
            branch_line = dict(
                type="line", layer="below", line=dict(color=line_color, width=line_width)
            )

            if root_clade:
                branch_line.update(x0=-0.01, y0=y_curr, x1=-0.01, y1=y_curr)
                return branch_line
            elif orientation == "horizontal":
                branch_line.update(x0=x_start, y0=y_curr, x1=x_curr, y1=y_curr)
            elif orientation == "vertical":
                branch_line.update(x0=x_curr, y0=y_bot, x1=x_curr, y1=y_top)
            else:
                raise ValueError("Line type can be 'horizontal' or 'vertical'")

            return branch_line

        def draw_clade(
            clade,
            x_start,
            line_shapes,
            line_color="rgb(15,15,15)",
            line_width=1,
            x_coords=0,
            y_coords=0,
            init_clade=False,
        ):
            """Recursively draw the tree branches, down from the given clade"""

            x_curr = x_coords[clade]
            y_curr = y_coords[clade]

            # Draw a horizontal line from start to here
            if init_clade:
                branch_line = get_clade_lines(
                    orientation="horizontal",
                    y_curr=y_curr,
                    x_start=x_start,
                    x_curr=x_curr,
                    line_color=line_color,
                    line_width=line_width,
                    root_clade=True,
                )
            else:
                branch_line = get_clade_lines(
                    orientation="horizontal",
                    y_curr=y_curr,
                    x_start=x_start,
                    x_curr=x_curr,
                    line_color=line_color,
                    line_width=line_width,
                    root_clade=False,
                )

            line_shapes.append(branch_line)

            if clade.clades:
                # Draw a vertical line connecting all children
                y_top = y_coords[clade.clades[0]]
                y_bot = y_coords[clade.clades[-1]]

                line_shapes.append(
                    get_clade_lines(
                        orientation="vertical",
                        x_curr=x_curr,
                        y_bot=y_bot,
                        y_top=y_top,
                        line_color=line_color,
                        line_width=line_width,
                    )
                )

                # Draw descendants
                for child in clade:
                    draw_clade(child, x_curr, line_shapes,
                               x_coords=x_coords, y_coords=y_coords)

        tree = self.newicktree
        tree.ladderize()

        x_coords = get_x_coordinates(tree)
        y_coords = get_y_coordinates(tree)
        line_shapes = []
        draw_clade(
            tree.root,
            0,
            line_shapes,
            line_color="rgb(25,25,25)",
            line_width=1,
            x_coords=x_coords,
            y_coords=y_coords,
            init_clade=True,
        )
        my_tree_clades = x_coords.keys()
        X = []
        Y = []
        text = []

        for cl in my_tree_clades:
            X.append(x_coords[cl])
            Y.append(y_coords[cl])
            # Add confidence values if internal node
            if not cl.name:
                text.append(cl.confidence)
            else:
                text.append(cl.name)

        axis = dict(
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title="",  # y title
        )

        label_legend = ["Tree_1"]
        nodes = []

        for elt in label_legend:
            node = dict(
                type="scatter",
                x=X,
                y=Y,
                mode="markers+text",
                # marker=dict(color=color, size=5),
                text=text,  # vignet information of each node
                textposition='right',
                showlegend=False,
                name=elt,
            )
            nodes.append(node)

        layout = dict(
            height=800,
            dragmode="select",
            autosize=True,
            showlegend=True,
            xaxis=dict(
                showline=True,
                zeroline=False,
                showgrid=False,  # To visualize the vertical lines
                ticklen=4,
                showticklabels=True,
                title="Branch Length",
                range=[-0.02, max(X)*1.25],
            ),
            yaxis=axis,
            hovermode="closest",
            shapes=line_shapes,
            legend={"x": 0, "y": 1},
            font=dict(family="Open Sans"),
            template='plotly_dark',
        )

        fig = dict(data=nodes, layout=layout)
        return fig

    def create_angular_tree(self):

        def get_x_coordinates(tree):
            """Associates to each clade an x-coord.
            returns dict {clade: x-coord}
            """
            xcoords = tree.depths()
            # tree.depth() maps tree clades to depths (by branch length).
            # returns a dict {clade: depth} where clade runs over all Clade instances of the tree, and depth
            # is the distance from root to clade

            #  If there are no branch lengths, assign unit branch lengths
            if not max(xcoords.values()):
                xcoords = tree.depths(unit_branch_lengths=True)

            return xcoords

        def get_y_coordinates(tree, dist=1):
            """
            returns  dict {clade: y-coord}
            The y-coordinates are  (float) multiple of integers (i*dist below)
            dist depends on the number of tree leafs
            """
            maxheight = tree.count_terminals()  # Counts the number of tree leafs.
            # Rows are defined by the tips/leafs
            ycoords = dict(
                (leaf, maxheight - i / dist) for i, leaf in enumerate(reversed(tree.get_terminals()))
            )

            def calc_row(clade):
                for subclade in clade:
                    if subclade not in ycoords:
                        calc_row(subclade)
                ycoords[clade] = (ycoords[clade.clades[0]] +
                                  ycoords[clade.clades[-1]]) / 2

            if tree.root.clades:
                calc_row(tree.root)
            return ycoords

        def get_clade_lines(
            orientation="horizontal",
            y_curr=0,
            last_y_curr=0,
            x_start=0,
            x_curr=0,
            y_bot=0,
            y_top=0,
            line_color="rgb(25,25,25)",
            line_width=0.5,
            init_flag=False,
        ):
            """define a shape of type 'line', for branch
            """
            branch_line = dict(
                type="line", layer="below", line=dict(color=line_color, width=line_width)
            )
            if orientation == "horizontal":
                if init_flag:
                    branch_line.update(x0=x_start, y0=y_curr,
                                       x1=x_curr, y1=y_curr)
                else:
                    branch_line.update(
                        x0=x_start, y0=last_y_curr, x1=x_curr, y1=y_curr)
            elif orientation == "vertical":
                branch_line.update(x0=x_curr, y0=y_bot, x1=x_curr, y1=y_top)
            else:
                raise ValueError("Line type can be 'horizontal' or 'vertical'")
            return branch_line

        def draw_clade(
            clade,
            x_start,
            line_shapes,
            line_color="rgb(15,15,15)",
            line_width=1,
            x_coords=0,
            y_coords=0,
            last_clade_y_coord=0,
            init_flag=True
        ):
            """Recursively draw the tree branches, down from the given clade"""
            x_curr = x_coords[clade]
            y_curr = y_coords[clade]

            # Draw a horizontal line from start to here
            branch_line = get_clade_lines(
                orientation="horizontal",
                y_curr=y_curr,
                last_y_curr=last_clade_y_coord,
                x_start=x_start,
                x_curr=x_curr,
                line_color=line_color,
                line_width=line_width,
                init_flag=init_flag,
            )

            line_shapes.append(branch_line)

            if clade.clades:
                # Draw descendants
                for child in clade:
                    draw_clade(child, x_curr, line_shapes, x_coords=x_coords,
                               y_coords=y_coords, last_clade_y_coord=y_coords[clade], init_flag=False)

        # Load in Tree object and ladderize
        tree = self.newicktree
        tree.ladderize()

        # Get coordinates + put into dictionary
        # dict(keys=clade_names, values=)
        x_coords = get_x_coordinates(tree)
        y_coords = get_y_coordinates(tree)
        line_shapes = []
        draw_clade(
            tree.root,
            0,
            line_shapes,
            line_color="rgb(25,25,25)",
            line_width=1,
            x_coords=x_coords,
            y_coords=y_coords,
        )
        #
        my_tree_clades = x_coords.keys()
        X = []
        Y = []
        text = []

        for cl in my_tree_clades:
            X.append(x_coords[cl])
            Y.append(y_coords[cl])
            # Add confidence values if internal node
            if not cl.name:
                text.append(cl.confidence)
            else:
                text.append(cl.name)

        axis = dict(
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title="",  # y title
        )

        label_legend = ["Tree_1"]
        nodes = []

        for elt in label_legend:
            node = dict(
                type="scatter",
                x=X,
                y=Y,
                mode="markers+text",
                # marker=dict(color=color, size=5),
                text=text,  # vignet information of each node
                textposition='right',
                hoverinfo='',
                showlegend=False,
                name=elt,
            )
            nodes.append(node)

        layout = dict(
            height=800,
            # title=graph_title,
            dragmode="select",
            autosize=True,
            showlegend=True,
            xaxis=dict(
                showline=True,
                zeroline=False,
                showgrid=False,
                ticklen=4,
                showticklabels=True,
                title="Branch Length",
            ),
            yaxis=axis,
            hovermode="closest",
            shapes=line_shapes,
            legend={"x": 0, "y": 1},
            font=dict(family="Open Sans"),
            template='plotly_dark',
        )

        fig = dict(data=nodes, layout=layout)
        return fig


class RFDistance():

    def __init__(self, t1, t2):
        self.t1 = Tree(t1)
        self.t2 = Tree(t2)
        self.compare = self.t1.compare(self.t2)

    def NormRF(self):
        return self.compare['norm_rf']

    def RF(self):
        return self.compare['rf']

    def MaxRF(self):
        return self.compare['max_rf']


# -------------------------------------------------------------------------------------
# ----------------------------- Figure creating functions -----------------------------

def make_combined_topology_figure(
    dataframe,
    max_window_size,
    window_size,
    chromosome_length_info,
    template,
    num_of_graphs_to_plot,
    color_mapping,
):
    df_cols = dataframe.columns.to_list()
    # Set chromosome info variables
    # NOTE: Strip is used in case there are commas in the number
    chrom_start = chromosome_length_info["Start"][0]
    chrom_stop = chromosome_length_info["Stop"][0]

    clean_start, clean_stop = data_utils.fix_bed_file_chroms(
        chrom_start, chrom_stop)
    # Set dtick value based on chromosome length
    if clean_stop > 10000000:
        dtick_val = 10000000
        tick_val = 0
    elif 1000000 < clean_stop < 10000000:  # Between 1 million and 10 million
        dtick_val = None
        tick_val = None
    elif 100000 < clean_stop < 1000000:  # Between 100,000 and 1 million
        dtick_val = None
        tick_val = None
    elif 1000 < clean_stop < 100000:  # Between 1000 and 100,000
        dtick_val = None
        tick_val = None
    elif 100 < clean_stop < 1000:
        dtick_val = None
        tick_val = None
    elif 10 < clean_stop < 100:
        dtick_val = None
        tick_val = None
    else:
        dtick_val = None
        tick_val = None


    # get number of unqiue windows for y-values of plotting
    unique_windows = dataframe["Window"]

    # set ranges
    x_range = [clean_start, clean_stop]

    # Build graph  
    fig = px.histogram(
        dataframe,
        x="Window",
        y=[1]*len(unique_windows),
        nbins=int(clean_stop / window_size),
        # nbins=len(unique_windows),
        color="TopologyID",
        color_discrete_map=color_mapping,
        hover_data=['Chromosome', 'Window'],
        barmode='relative',
        marginal="rug",
        range_x=x_range,
    )

    # Update layout
    fig.update_layout(
        template=template,
        legend_title_text='Topology',
        xaxis_title_text='Position',
        margin=dict(
            l=60,
            r=50,
            b=40,
            t=40,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
    )
    fig.update_xaxes(
        # matches="x",
        rangemode="tozero",
        linewidth=2,
    )
    fig.update_yaxes(
        nticks=1,
        title="",
        showline=True,
        linewidth=2,
        showticklabels=False,
    )
    return fig


def make_rug_plot_figure(
    dataframe,
    max_window_size,
    window_size,
    chromosome_length_info,
    template,
    num_of_graphs_to_plot,
    color_mapping,
):
    """
    NOTE: max_window_size is currently unused. It has been replaced by a bed f with chromosome length info.
    """
    # Set chromosome info variables
    # NOTE: Strip is used in case there are commas in the number
    chrom_start = chromosome_length_info["Start"][0]
    chrom_stop = chromosome_length_info["Stop"][0]

    clean_start, clean_stop = data_utils.fix_bed_file_chroms(
        chrom_start, chrom_stop)
    # Set dtick value based on chromosome length
    if clean_stop > 10000000:
        dtick_val = 10000000
        tick_val = 0
    elif 1000000 < clean_stop < 10000000:  # Between 1 million and 10 million
        dtick_val = None
        tick_val = None
    elif 100000 < clean_stop < 1000000:  # Between 100,000 and 1 million
        dtick_val = None
        tick_val = None
    elif 1000 < clean_stop < 100000:  # Between 1000 and 100,000
        dtick_val = None
        tick_val = None
    elif 100 < clean_stop < 1000:
        dtick_val = None
        tick_val = None
    elif 10 < clean_stop < 100:
        dtick_val = None
        tick_val = None
    else:
        dtick_val = None
        tick_val = None

    x_range = [clean_start, clean_stop]

    fig = px.histogram(
        dataframe,
        x="Window",
        y=[1]*len(dataframe["Window"]),
        nbins=int(clean_stop / window_size),
        color="TopologyID",
        facet_row="TopologyID",
        color_discrete_map=color_mapping,
        histfunc="count",
        barmode='overlay',
        range_x=x_range,
    )
    fig.update_layout(
        template=template,
        legend_title_text='Topology',
        xaxis_title_text='Position',
        margin=dict(
            l=60,
            r=1,
            t=40,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
    )
    fig.update_xaxes(
        matches="x",
        rangemode="tozero",
        tick0=tick_val,
        dtick=dtick_val,
    )
    fig.update_yaxes(
        nticks=1,
        title="",
        showline=True,
        linewidth=2,
        showticklabels=False,
    )
    fig.for_each_annotation(lambda a: a.update(text=""))
    return fig


def make_alt_data_int_figure(
    alt_data_to_graph,
    dataframe,
    chromosome_length_info,
    template,
    num_of_graphs_to_plot,
    chromosome,
):
    # sort dataframe
    dataframe.sort_values(by=["Window"], inplace=True)
    y_range_max = max(dataframe[alt_data_to_graph])

    # Set chromosome info variables
    chrom_cols = [col for col in chromosome_length_info.columns]
    chromosome_length_info_clean = chromosome_length_info[chromosome_length_info[chrom_cols[0]] == chromosome]
    chromosome_length_info_clean.reset_index(drop=True, inplace=True)
    chrom_start = chromosome_length_info_clean[chrom_cols[1]][0]
    chrom_stop = chromosome_length_info_clean[chrom_cols[2]][0]
    clean_start, clean_stop = data_utils.fix_bed_file_chroms(
        chrom_start, chrom_stop)

    # Set dtick value based on chromosome length
    if clean_stop > 10000000:
        dtick_val = 10000000
        tick_val = 0
    else:
        dtick_val = None
        tick_val = None

    # set graph height based on number of graphs to plot
    graph_height = (500 // num_of_graphs_to_plot)

    # set ranges
    x_range = [clean_start, clean_stop]
    y_range = [0, y_range_max * 1.1]

    # Build graph
    fig = px.line(
        dataframe,
        x="Window",
        y=alt_data_to_graph,
    )
    # Update layout
    fig.update_layout(
        template=template,
        margin=dict(
            l=60,
            r=50,
            b=40,
            t=40,
        ),
        title={
            'text': str(alt_data_to_graph),
            'y':0.95,
            'x':0.501,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    fig.update_xaxes(
        title="Position",
        tick0=tick_val,
        # dtick=dtick_val,
    )
    fig.update_yaxes(
        title="Percent (%)",
        range=y_range,
        nticks=1,
        dtick=10,
        showline=True,
        linewidth=2,
    )
    return fig


def make_alt_data_str_figure(
    alt_data_to_graph,
    dataframe,
    chromosome_length_info,
    template,
    num_of_graphs_to_plot,
    chromosome,
):
    # sort dataframe
    dataframe.sort_values(by=["Window"], inplace=True)
    dataframe.dropna(inplace=True)

    # Set chromosome info variables
    chrom_cols = [col for col in chromosome_length_info.columns]
    chromosome_length_info_clean = chromosome_length_info[chromosome_length_info[chrom_cols[0]] == chromosome]
    chromosome_length_info_clean.reset_index(drop=True, inplace=True)
    chrom_start = chromosome_length_info_clean[chrom_cols[1]][0]
    chrom_stop = chromosome_length_info_clean[chrom_cols[2]][0]
    clean_start, clean_stop = data_utils.fix_bed_file_chroms(
        chrom_start, chrom_stop)

    # Set dtick value based on chromosome length
    if clean_stop > 10000000:
        dtick_val = 10000000
        tick_val = 0
    else:
        dtick_val = None
        tick_val = None

    # set ranges
    x_range = [clean_start, clean_stop]
    # Build graph
    fig = px.histogram(
        dataframe,
        x="Window",
        y=[1]*len(dataframe),
        color=alt_data_to_graph,
    )
    # Update layout
    fig.update_layout(
        template=template,
        margin=dict(
            l=60,
            r=50,
            b=40,
            t=40,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        title={
            'text': str(alt_data_to_graph),
            'y':0.95,
            'x':0.501,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    fig.update_xaxes(
        title="Position",
        range=x_range,
        linewidth=2,
        tick0=tick_val,
        showline=True,
        # dtick=dtick_val,
    )
    fig.update_yaxes(
        title="y-axis",
        range=[0, 1],
        nticks=1,
        dtick=10,
        showline=True,
        linewidth=2,
    )
    return fig


def make_RF_heatmap(rfdist_df, template, color_mapping):
    fig = px.bar(
        rfdist_df,
        x='index',
        y='NormRF',
        color='TopologyID',
        color_discrete_map=color_mapping,
        text='NormRF',
        range_y=[0, 1.2],
    )

    fig.update_traces(
        textposition='outside', 
        texttemplate='%{text:.2f}',
    )
    
    fig.update_xaxes(
        dtick=1,
        title='Window',
        # NOTE: Replace index labels with Window values
        tickmode = 'array',
        tickvals = rfdist_df['index'],
        ticktext = [str(s) for s in rfdist_df['Window']],
        )
    fig.update_layout(
        # margin=dict(r=1, t=60, b=10),
        # autosize=True,
        title={
            'text': "Normalized RF-Distance",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        template=template,
    )
    return fig

# ---------------------------------------------------------------------------------
# ----------------------------- Build graph functions -----------------------------
def build_combined_topology_graph(
    topology_df,
    chromosome_length_data,
    chromosome,
    template,
    topology,
    num_of_graphs_to_plot,
    color_mapping,
):
    # --- Set up topology data ---
    # Clean up dataframes and sort
    topology_df.sort_values(by=["Chromosome", "Window"], inplace=True)
    topology_df.reset_index(drop=True, inplace=True)

    # Collect needed dataframe metadata before grouping out data
    topology_max_window_value = max(topology_df["Window"])
    topology_window_size = abs(topology_df["Window"][1] - topology_df["Window"][0])

    # Filter by chromosome
    topology_df = topology_df[topology_df["Chromosome"] == chromosome]

    # Clean up dataframes and sort after filter
    topology_df.sort_values(by=["Chromosome", "Window"], inplace=True)
    topology_df.reset_index(drop=True, inplace=True)

    # --- Set up chromosome length metadata ---
    chrom_length_df = pd.read_json(chromosome_length_data)
    chrom_length_df = chrom_length_df[chrom_length_df["Chromosome"] == chromosome]
    chrom_length_df.reset_index(drop=True, inplace=True)

    # Group wanted data
    if (type(topology) == str) or (type(topology) == int):
        wanted_rows = topology_df[topology_df["TopologyID"] == topology]
    elif type(topology) == list:
        wanted_rows = topology_df[topology_df["TopologyID"].isin(topology)]

    # Create tree graph
    topology_graph_data = make_combined_topology_figure(
        wanted_rows,
        topology_max_window_value,
        topology_window_size,
        chrom_length_df,
        template,
        num_of_graphs_to_plot,
        color_mapping,
    )
    return topology_graph_data


def build_singular_topology_graph(
    topology_df,
    chromosome_length_data,
    chromosome,
    template,
    topology,
    num_of_graphs_to_plot,
    color_mapping,
):

    # Clean up dataframes and sort
    topology_df.sort_values(by=["Chromosome", "Window"], inplace=True)
    topology_df.reset_index(drop=True, inplace=True)

    # Collect needed dataframe metadata before grouping out data
    # multiply by 1.1 to give a 10% cushion to the end of the graph
    topology_max_window_value = max(topology_df["Window"])
    topology_window_size = abs(topology_df["Window"][1] - topology_df["Window"][0])

    # Filter by chromosome
    topology_df = topology_df[topology_df["Chromosome"] == chromosome]

    # Clean up dataframes and sort after filter
    topology_df.sort_values(by=["Chromosome", "Window"], inplace=True)
    topology_df.reset_index(drop=True, inplace=True)

    # --- Set up chromosome length metadata ---
    chrom_length_df = pd.read_json(chromosome_length_data)
    chrom_length_df = chrom_length_df[chrom_length_df["Chromosome"] == chromosome]
    chrom_length_df.reset_index(drop=True, inplace=True)

    # Group wanted data
    if (type(topology) == str) or (type(topology) == int):
        wanted_rows = topology_df[topology_df["TopologyID"] == topology]
    elif type(topology) == list:
        wanted_rows = topology_df[topology_df["TopologyID"].isin(topology)]

    # Create tree graph
    heatmap_graph = make_rug_plot_figure(
        wanted_rows,
        topology_max_window_value,
        topology_window_size,
        chrom_length_df,
        template,
        num_of_graphs_to_plot,
        color_mapping,
    )
    return heatmap_graph


def build_alt_data_graph(
    alt_data_to_graph,
    tv_input_df,
    chromosome_length_data,
    chromosome,
    template,
    topology,
    num_of_graphs_to_plot,
):
    # Load in DataFrames
    chrom_length_df = pd.read_json(chromosome_length_data)

    # Filter by chromosome
    tv_input_df = tv_input_df[tv_input_df["Chromosome"] == chromosome]

    # Clean up dataframes and sort after filter
    tv_input_df.sort_values(by=["Chromosome", "Window", "TopologyID"], inplace=True)
    tv_input_df.reset_index(drop=True, inplace=True)

    # Check input type and grapha accordingly
    input_type = type(tv_input_df[alt_data_to_graph].dropna().to_list()[0])

    if input_type == str:
        alt_data_graph_data = make_alt_data_str_figure(
            alt_data_to_graph,
            tv_input_df,
            chrom_length_df,
            template,
            num_of_graphs_to_plot,
            chromosome,
        )
    else:
        alt_data_graph_data = make_alt_data_int_figure(
            alt_data_to_graph,
            tv_input_df,
            chrom_length_df,
            template,
            num_of_graphs_to_plot,
            chromosome,
        )
    return alt_data_graph_data


def build_RF_heatmap(
    rfdist_df,
    template,
    color_mapping,
):
    # Reset index and use to get proper window placement
    rfdist_df.reset_index(inplace=True)
    # Create figure + return figure
    heatmap = make_RF_heatmap(rfdist_df, template, color_mapping)
    return heatmap


def no_data_graph(template):
    """This function returns a blank figure with a "NO DATA" watermark"""
    fig = go.Figure()
    fig.update_layout(
        template=template,
        annotations=[
            dict(
                name="draft watermark",
                text="NO DATA",
                textangle=0,
                opacity=0.1,
                font=dict(color="white", size=50),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ]
    )
    return fig


def init_data_graph(template):
    """
    This function returns a blank figure with a "NO DATA" watermark.
    """
    fig = go.Figure()
    fig.update_layout(
        template=template,
        annotations=[
            dict(
                name="draft watermark",
                text="GATHERING DATA...",
                textangle=0,
                opacity=0.9,
                font=dict(color="white", size=100),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ],
    )
    fig.update_xaxes(showgrid=False, range=[0.2, 1], zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, range=[0.2, 1], zeroline=False, visible=False)
    return fig


def init_RF_graph(template):
    """
    This function returns a blank figure with a "NO DATA" watermark.
    """
    fig = go.Figure()
    fig.update_layout(
        template=template,
        annotations=[
            dict(
                name="draft watermark",
                text="Hover Over Data to Activate",
                textangle=0,
                opacity=0.9,
                font=dict(color="white", size=100),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ],
    )
    fig.update_xaxes(showgrid=False, range=[0.2, 1], zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, range=[0.2, 1], zeroline=False, visible=False)
    return fig


# ---------------------------------------------------------------------------------
# ------------------------- Graph customization functions -------------------------

def set_topology_colors(f, color):
    df = data_utils.build_file_dataframe(f)  
    # Set colors to topologies
    sorted_topologies = df.assign(freq=df.groupby('TopologyID')['TopologyID'].transform('count')).sort_values(by=['freq','TopologyID'],ascending=[False,True]).loc[:,['TopologyID']]
    unique_topos = sorted_topologies["TopologyID"].unique()
    color_list = color * ((len(unique_topos) // len(color)))
    color_list = color_list + color[:len(unique_topos) % len(color)]
    output_dict = dict()
    for s, c in zip(unique_topos, color_list):
        output_dict[s] = c
    return output_dict


def get_RFxpos(hoverdata, window_size):
    hoverdata = hoverdata['points'][0]
    if 'customdata' in hoverdata.keys():
        x_pos = hoverdata['customdata'][1]  # Window position
        return int(x_pos)
    else:
        x_pos = int(hoverdata['x']) - (window_size/2) + 1
        return int(x_pos)