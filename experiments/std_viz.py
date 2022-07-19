import numpy as np
import pandas as pd

# Bokeh libraries
from bokeh.io import output_file, output_notebook
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from bokeh.layouts import row, column, gridplot
from bokeh.models.widgets import Tabs, Panel

def make_dim_plot(dimension: pd.core.series.Series, nb=False) :
    '''
    Builds a figure object showing the distribution of subjects of a population for
    a specific dimension
    '''
    if nb: output_notebook()

    dimension = dimension[np.isfinite(dimension)]
    hist, edges = np.histogram(dimension, density=True, bins=20)

    p = figure(title=dimension.name, tools="", background_fill_color="#fafafa")

    p.quad(
        top=hist,
        bottom=0,
        left=edges[:-1],
        right=edges[1:],
        fill_color="navy",
        line_color="white",
        alpha=0.5,
        legend_label=dimension.name,
    )

    p.y_range.start = 0
    p.legend.location = "center_right"
    p.legend.background_fill_color = "#fefefe"
    p.xaxis.axis_label = "x"
    p.yaxis.axis_label = "Pr(x)"
    p.grid.grid_line_color = "white"

    return p