import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc

import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def single_chrom_expanded(
    chosen_samples,
    chromosome,
    file_value,
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
):

    if type(chosen_samples) == str:
        chosen_samples = [chosen_samples]

    graphs = []

    """ Filter out current chromosome and set x- and y-max"""
    curr_chrom_data = read_csv[read_csv["Chromosome"] == chromosome]

    x_max = curr_chrom_data["Stop"].max() * 1.1  # increase 10% above max
    y_max = float(curr_chrom_data["p_distance"].max() * 1.1)  # increase 10% above max
    

    """Dynamically set height of graphs based on # of samples being shown"""
    if len(chosen_samples) >= 4:
        base_graph_height = 150
    elif len(chosen_samples) == 3:
        base_graph_height = 200
    elif len(chosen_samples) == 2:
        base_graph_height = 300
    else:
        base_graph_height = 500

    fig = make_subplots(
        rows=len(chosen_samples),
        cols=1,
        x_title="Position",
        y_title="p-distance",
        row_titles=chosen_samples,
        # subplot_titles=chosen_samples,
        row_heights=[base_graph_height] * len(chosen_samples)
    )
    for row, sample_name in enumerate(chosen_samples, 1):
        filt_2 = (curr_chrom_data["Sample"] == sample_name)
        curr_sample_data = curr_chrom_data[filt_2]

        x_data = [i for i in curr_sample_data["Stop"]]
        y_data = [i for i in curr_sample_data["p_distance"]]

        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=y_data,
                legendgroup=str(sample_name),
                name=sample_name,
                line=dict(
                    color=colors[row], 
                    width=float(line_width),
                ),
                showlegend=True,
                # colorscale="Viridis"
            ),
            row=row,
            col=1,
        )
        continue
    fig.update_layout(
        height=base_graph_height*len(chosen_samples),
        margin=dict(
            l=60,
            r=50,
            b=60,
            t=30,
            pad=2.5
        ),
        template=chosen_template,
        showlegend=False,
        dragmode='pan',
        font=dict(
                family="Arial, monospace",
                size=font_size,
            ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )
    fig.update_yaxes(
        range=[0, y_max],
        fixedrange=True,
    )
    fig.update_xaxes(
        # range=[rangeslider_lowlim, rangeslider_highlim],
        fixedrange=True,
    )
    graphs.append(
        dbc.Col(
            dcc.Graph(
                id=sample_name,
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
            ),
            width=12,
            style={
                "height": "{}px".format(base_graph_height*len(chosen_samples))
            },
        )
    )
    return graphs


def single_chrom_condensed(
    chosen_samples,
    chromosome,
    file_value,
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
):
    # If you only want to look at one sample, the sample name will need to be put into a list.
    # If more than one selected, it automatically places it into a list.
    if type(chosen_samples) == str:
        chosen_samples = [chosen_samples]

    graphs = []

    """ Override base_graph_height"""

    base_graph_height = 500


    """ Filter out current chromosome and set x- and y-max"""
    curr_chrom_data = read_csv[read_csv["Chromosome"] == chromosome]

    x_max = curr_chrom_data["Stop"].max() * 1.1  # increase 10% above max
    y_max = float(curr_chrom_data["p_distance"].max() * 1.1)  # increase 10% above max

    fig = go.Figure()

    for row, sample_name in enumerate(samples, 1):
        filt_2 = (curr_chrom_data["Sample"] == sample_name)
        curr_sample_data = curr_chrom_data[filt_2]

        x_data = [i for i in curr_sample_data["Stop"]]
        y_data = [i for i in curr_sample_data["p_distance"]]

        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=y_data,
                legendgroup=str(sample_name),
                name=sample_name,
                line=dict(
                    color=colors[row], 
                    width=float(line_width),
                ),
                showlegend=True,
                # colorscale="Viridis"
            ),
        )
        continue
    fig.update_layout(
        height=base_graph_height*len(chosen_samples),
        margin=dict(
            l=60,
            r=50,
            b=60,
            t=30,
            pad=2.5
        ),
        template=chosen_template,
        showlegend=True,
        dragmode='pan',
        newshape=dict(
            line_color='red',
            line_width=1.5,
        ),
        font=dict(
                family="Arial, monospace",
                size=font_size,
            ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            itemsizing='trace',
        ),       
    )
    fig.update_yaxes(
        title="p-distance",
        range=[0, y_max],
        fixedrange=True,
    )
    fig.update_xaxes(
        title="Position",
        tick0=0,
        )
    graphs.append(
        dbc.Col(
            dcc.Graph(
                id=chromosome,
                figure=fig,
                config=dict(
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
            ),
            width=12,
            style={
                "height": "{}px".format(base_graph_height)
            },
        )
    )
    return graphs

