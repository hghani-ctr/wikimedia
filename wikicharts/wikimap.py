import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Polygon
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import os
from shapely.geometry import Polygon
import calendar
from datetime import date, datetime
from math import ceil, floor, log10
import warnings

from config import wmf_colors, wmf_regions, style_parameters
from data_utils import simple_num_format, split_df_by_col, format_perc, gen_keys, closestdivisible

from parameters import (
    author, 
    editing_data_path,
    readers_data_path,
    unique_devices_data_path,
    save_directory,
    content_gap_data_path
)
import warnings


class Wikimap():
    """A class for creating and managing map-based visualizations."""
    def __init__(
        self,
        dataset,
        width=10,
        height=6,
        fignum=0,
        title="",
        author=author,
        data_source="N/A",
        titlepad=0,
        month=False,
        display_month=True
    ):
        """Initializes the map with specified dimensions and data."""
        self.df = dataset
        self.fig, self.ax = plt.subplots(1, 1, num=fignum)
        self.fig.set_figwidth(width)
        self.fig.set_figheight(height)
        self.cax = None
        self.cbar = None
        self.vmin = None
        self.vmax = None
        if display_month == True:
            month_num = month.month
            month_name = f"({calendar.month_name[month_num]})"
        else:
            month_name = ""
        custom_title = f'{title} {month_name}'
        plt.title(custom_title, font=style_parameters['font'], fontsize=style_parameters['title_font_size'], weight='bold', loc='left', wrap=True, pad=titlepad)
        today = date.today()
        plt.figtext(0.1, 0.025, "Graph Notes: Created by " + str(author) + " " + str(today) + " using data from " + str(data_source), family=style_parameters['font'], fontsize=8, color=wmf_colors['black25'])

    def plot_wcolorbar(self, col="pop_est", custom_cmap="plasma_r", plot_alpha=0.6, setlimits=False, custom_vmin=-25, custom_vmax=50):
        """Creates a map chart with a color scale legend."""
        if setlimits == True:
            self.vmin = custom_vmin
            self.vmax = custom_vmax
        else:
            self.vmin = self.df[col].min()
            self.vmax = self.df[col].max()
        sm = plt.cm.ScalarMappable(cmap=custom_cmap, norm=plt.Normalize(vmin=self.vmin, vmax=self.vmax))
        sm.set_array([])
        divider = make_axes_locatable(self.ax)
        self.cax = divider.append_axes("right", size="3%", pad=0.05)
        self.cbar = plt.colorbar(sm, cax=self.cax, alpha=plot_alpha)
        self.df.plot(column=col, cmap=custom_cmap, vmin=self.vmin, vmax=self.vmax, linewidth=0.1, ax=self.ax, edgecolor='black', alpha=plot_alpha)

    def plot_regions(self, region_table, label_col, fontsize=12):
        """Plots region outlines and applies labels based on a given column."""
        for region in wmf_regions:
            region_geo = region_table.loc[region, 'geometry']
            region_boundary = region_geo.boundary
            region_boundary.plot(ax=self.ax, lw=1.5, color='black', alpha=1)
        for region in wmf_regions:
            centroid = region_table.loc[region, 'centroid']
            self.ax.annotate(text=region_table.loc[region, label_col], xy=(centroid.x, centroid.y), xycoords='data', ha='center', va='center', fontsize=fontsize, font=style_parameters['font'], fontweight='bold', zorder=15, bbox=dict(facecolor=(1, 1, 1, 0.85), edgecolor='black', pad=3))

    def format_map(self, radjust=0.9, ladjust=0.1, tadjust=0.9, badjust=0.1, format_colobar=True, cbar_perc=False):
        """Applies formatting to the map, adjusting margins and color bar settings."""
        for pos in ['right', 'top', 'bottom', 'left']:
            plt.gca().spines[pos].set_visible(False)
        self.ax.axis('off')
        plt.tight_layout(pad=3)
        if format_colobar == True:
            self.cbar.outline.set_visible(False)
            current_ylabels = self.cax.get_yticklabels()
            y_ticks = list(self.cax.get_yticks())
            new_ylabels = []
            for y_label in current_ylabels:
                y_value = float(y_label.get_position()[1])
                new_label = simple_num_format(y_value, perc=cbar_perc)
                new_ylabels.append(new_label)
            self.cax.set_yticklabels(new_ylabels, fontsize=10, font=style_parameters['font'])

    def finalize_plot(self, save_file_name, display=True):
        """Finalizes the map visualization by saving to file and optionally displaying it."""
        save_path = save_directory + save_file_name
        plt.savefig(save_path, dpi=300)
        if display:
            plt.show()