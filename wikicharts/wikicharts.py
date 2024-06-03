import os
import re
import calendar
from datetime import date, datetime
from math import ceil, floor, log10

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.dates as dates
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle
from matplotlib import font_manager
import warnings
import math
from math import ceil, floor, log10

from .data_utils import simple_num_format, split_df_by_col, format_perc, gen_keys, closestdivisible
from .parameters import (
    author, 
    editing_data_path,
    readers_data_path,
    unique_devices_data_path,
    save_directory,
    content_gap_data_path
)

from .config import wmf_colors, style_parameters, wmf_regions


class Wikichart():
    """A class for creating and managing plots specifically designed for Wikipedia-style visualizations."""
    def __init__(self, start_date, end_date, dataset, set_month_interest=True, time_col='month', yoy_highlight=None):
        """Initializes the chart with dates and data, setting the month of interest for highlighting specific data points."""
        self.start_date = start_date
        self.end_date = end_date
        self.df = dataset
        # Sets month_interest to the last month in the dataset, or to the current month
        if set_month_interest:
            self.month_interest = self.df.iloc[-1][time_col].month
            self.month_name = calendar.month_name[self.month_interest]
        else:
            self.month_interest = date.today().month
            self.month_name = calendar.month_name[self.month_interest]
        self.fig = None
        self.ax = None
        self.yranges = []
        self.ynumticks = []

    def init_plot(self, width=10, height=6, subplotsx=1, subplotsy=1, fignum=0):
        """Initializes the plotting area with specified dimensions and number of subplots."""
        self.fig, self.ax = plt.subplots(subplotsx, subplotsy, num=fignum)
        self.fig.set_figwidth(width)
        self.fig.set_figheight(height)

    def plot_line(self, x, y, col, legend_label='_nolegend_', linewidth=2):
        """Plots a basic line chart."""
        plt.plot(self.df[str(x)], self.df[str(y)],
                 label=legend_label,
                 color=col,
                 zorder=3,
                 linewidth=linewidth)
        
    def plot_bar(self, x, y, col = wmf_colors['blue'], legend_label='_nolegend_', width=10):
        """Plots a basic bar chart."""
        plt.bar(self.df[str(x)], self.df[str(y)], 
                color=col, 
                label=legend_label, 
                width=width)
    

    def plot_monthlyscatter(self, x, y, col, legend_label='_nolegend_'):
        """Plots scatter points for a specific month across multiple years."""
        monthly_df = self.df[self.df[str(x)].dt.month == self.month_interest]
        plt.scatter(monthly_df[str(x)], monthly_df[str(y)],
                    label=legend_label,
                    color=col,
                    zorder=4)
        # Note: due to a bug in matplotlib, the grid's zorder is fixed at 2.5 so everything plotted must be above 2.5
        

    def plot_yoy_highlight(self, x, y, highlight_radius=1000, col=wmf_colors['yellow'], legend_label='_nolegend_'):
        """Highlights year-over-year changes with a circular marker."""
        yoy_highlight = pd.concat([self.df.iloc[-13, :], self.df.iloc[-1, :]], axis=1).T
        plt.scatter(yoy_highlight[str(x)], yoy_highlight[str(y)],
                    label=legend_label,
                    s=highlight_radius,
                    facecolors='none',
                    edgecolors=col,
                    zorder=5)
        # Note: due to a bug in matplotlib, the grid's zorder is fixed at 2.5 so everything plotted must be above 2.5
        

    def plot_data_loss(self, x, y1, y2, data_loss_df, col=wmf_colors['base80'], legend_label='_nolegend_'):
        """Fills an area to indicate data loss or data exclusion."""
        plt.fill_between(data_loss_df[str(x)], data_loss_df[str(y1)], data_loss_df[str(y2)],
                         label=legend_label,
                         color=col,
                         edgecolor=col,
                         zorder=3)

    def block_off(self, blockstart, blockend, rectangle_text="", xbuffer=7):
        """Blocks off a range of dates with a rectangular overlay, optionally adding text."""
        xstart = mdates.date2num(blockstart)
        xend = mdates.date2num(blockend)
        block_width = xend - xstart
        ymin, ymax = plt.gca().get_ylim()
        block_height = ymax - ymin
        
        rect = Rectangle((xstart - xbuffer, ymin), block_width + 2 * xbuffer, block_height,
                         linewidth=0,  
                         fill='white',
                         edgecolor=wmf_colors['black75'], 
                         facecolor='white',  
                         zorder=5)
        plt.gca().add_patch(rect)
        
        annotation_x = xstart + (block_width / 2)
        ytick_values = plt.gca().get_yticks()
        ystart = ytick_values[0]
        annotation_y = ystart + (block_height / 2)
        rectangle_textbox = plt.gca().text(annotation_x, annotation_y, rectangle_text,
                                           ha='center',
                                           va='center',
                                           color=wmf_colors['black25'],
                                           family='Montserrat',
                                           fontsize=14,
                                           wrap=True,
                                           bbox=dict(pad=100, boxstyle='square', fc='none', ec='none'),
                                           zorder=8)
        rectangle_textbox._get_wrap_line_width = lambda: 300.

    def format(self, title, author=author, data_source="N/A", ybuffer=True, format_x_yearly=True, format_x_monthly=False, radjust=0.85, ladjust=0.1, tadjust=0.9, badjust=0.1, titlepad=0, perc=False):
        """Applies basic formatting to the chart, including title setup, axis labels, and grid lines."""
        for pos in ['right', 'top', 'bottom', 'left']:
            plt.gca().spines[pos].set_visible(False)
        # Add gridlines    
        plt.grid(axis='y', zorder=-1, color=wmf_colors['black25'], linewidth=0.25, clip_on=False)
        # Format title
        custom_title = f'{title} ({calendar.month_name[self.month_interest]})'
        plt.title(custom_title, font=style_parameters['font'], 
                  fontsize=style_parameters['title_font_size'], 
                  weight='bold', 
                  loc='left', 
                  wrap=True, 
                  pad=titlepad)
        # Expand bottom margin to make romo for author and data source info.
        plt.subplots_adjust(bottom=badjust, right=radjust, left=ladjust, top=tadjust)
        # Format x-axis labels — yearly x-axis labels on January
        if format_x_yearly == True:
            plt.xticks(fontname=style_parameters['font'], fontsize=style_parameters['text_font_size'])
            date_labels = []
            date_labels_raw = pd.date_range(self.start_date, self.end_date, freq='AS-JAN')
            for dl in date_labels_raw:
                date_labels.append(datetime.strftime(dl, '%Y'))
            plt.xticks(ticks=date_labels_raw, labels=date_labels)
         # Format x-axis labels — monthly labels
        if format_x_monthly == True:
            date_labels = []
            for dl in self.df['timestamp']:
                date_labels.append(datetime.strftime(dl, '%b'))
            plt.xticks(ticks=self.df['timestamp'], labels=date_labels, fontsize=14, fontname='Montserrat')
            
        # Buffer y-axis range to be 2/3rds of the total y axis range
        # Note: gca = get current axis
        if ybuffer == True:
            ax = plt.gca()
            current_ymin, current_ymax = ax.get_ylim()
            current_yrange = current_ymax - current_ymin
            new_ymin = current_ymin - current_yrange / 4
            if current_ymin > 0:
                # If the new ymin is positive, increase the ymax to have 2/3 buffer
                if new_ymin >= 0:
                    new_ymax = new_ymin + current_yrange * 1.5
                else:
                    new_ymin = 0
                    new_ymax = current_ymin + current_ymax
                ax.set_ylim([new_ymin, new_ymax])
                # Prevent any gridline clipping, but may make the graph seem overcluttered
                current_values = plt.gca().get_yticks()
                ax.set_ylim([current_values[0], new_ymax])
                
        # Format y-axis labels         
        warnings.filterwarnings("ignore")
        current_values = plt.gca().get_yticks()
        new_labels = []
        for y_value in current_values:
            new_label = simple_num_format(y_value, perc=perc)
            new_labels.append(new_label)
        plt.gca().set_yticklabels(new_labels)
        plt.yticks(fontname=style_parameters['font'], fontsize=style_parameters['text_font_size'])
        # Bottom annotation
        plt.figtext(
            0.1, 0.025,
            f"Graph Notes: Created by {author} on {date.today()} using data from {data_source}",
            family=style_parameters['font'],
            fontsize=8,
            color=wmf_colors['black25']
        )
        
    def annotate(self, x, y, num_annotation=None, legend_label="", label_color='black', num_color='black', xpad=0, ypad=0, zorder=10, use_last_y=False, perc=False, dynamic_spacing = 10):
        """Annotates the plot with text labels and numerical annotations at specified coordinates."""
        
        # Extract the last values for x and y to place the annotations
        last_x = self.df[str(x)].iat[-1]
        last_y = self.df[str(y)].iat[-1]

        if use_last_y:
            # If the perc flag is true, format the number as a percentage
            if perc:
                num_annotation = f"{last_y * 100:.1f}%"
            else:
                num_annotation = f"{last_y:.2f}"
    
        if legend_label:
            dynamic_spacing = (len(legend_label)* 10) + 1
        else:
            dynamic_spacing = 10
            
        # Calculate space between annotation calculation and annotation label
        legend_label_x_offset = 20 + xpad
        num_annotation_x_offset = legend_label_x_offset + dynamic_spacing

        if legend_label:
            plt.annotate(legend_label,
                            xy=(last_x, last_y),
                            xytext=(legend_label_x_offset, -5 + ypad),
                            textcoords='offset points',
                            color=label_color,
                            fontsize=style_parameters['text_font_size'],
                            weight='bold',
                            family=style_parameters['font'],
                            bbox=dict(pad=5, facecolor="white", edgecolor="none", alpha=0.7),
                            zorder=zorder)

    
        plt.annotate(num_annotation,
                     xy=(last_x, last_y),
                     xytext=(num_annotation_x_offset, -5 + ypad),
                     textcoords='offset points',
                     color=num_color,
                     fontsize=style_parameters['text_font_size'],
                     weight='bold',
                     family=style_parameters['font'],
                     zorder=zorder)

    def annotate_mean(self, x, y, line_color='red', line_width=2, line_style='-', alpha=0.5, text_color='darkred', text_xoffset=85, alignment_adjustment=0.005, zorder=10, show_median=False):
        """Calculates and annotates the mean and optionally the median for a data series."""
        mean_value = self.df[y].mean()
        median_value = self.df[y].median()
        
        last_x_position = self.df[x].iloc[-1]
        last_y_value = self.df[y].iloc[-1]
        
        # Calculate the percentage difference between the last y value and the mean
        percent_diff = abs((last_y_value - mean_value) / mean_value)
        percentage_mean_value = round(mean_value * 100, 1)
        percentage_median_value = round(median_value * 100, 1)
        
        # Determine label positioning
        if percent_diff < 0.01:
            label_x_position = last_x_position + pd.DateOffset(days=text_xoffset)
            label_y_position = last_y_value
            ha = 'left'
            va = 'center'
        else:
            label_x_position = last_x_position + pd.DateOffset(days=text_xoffset)
            label_y_position = mean_value + (mean_value * alignment_adjustment)
            ha = 'center'
            va = 'center'
            
        # Place text for the mean and median values in percentage format rounded to 1 decimal space
        plt.text(
            x=label_x_position,
            y=label_y_position,
            s=f'Mean: {percentage_mean_value:.1f}% / Median: {percentage_median_value:.1f}%' if show_median else f'Mean: {percentage_mean_value:.1f}%',
            color=text_color,
            ha=ha,
            va=va,
            fontsize=style_parameters['text_font_size'],
            weight='bold',
            family=style_parameters['font']
        )

    def calc_yoy(self, y, yoy_note=""):
        """Calculates the year-over-year percentage change for a specified column."""
        yoy_highlight = pd.concat([self.df.iloc[-13, :], self.df.iloc[-1, :]], axis=1).T
        yoy_change_percent = ((yoy_highlight[str(y)].iat[-1] - yoy_highlight[str(y)].iat[0]) / yoy_highlight[str(y)].iat[0]) * 100
        
        if math.isnan(yoy_change_percent):
            yoy_annotation = "YoY N/A"
        elif yoy_change_percent > 0:
            yoy_annotation = f" +{yoy_change_percent:.1f}% YoY" + " " + yoy_note
        else:
            yoy_annotation = f" {yoy_change_percent:.1f}% YoY" + " " + yoy_note
        return yoy_annotation

    def calc_finalcount(self, y, yoy_note=""):
        """Calculates the final count of a specified column for annotations."""
        final_count = self.df[str(y)].iat[-1]
        count_annotation = simple_num_format(value=final_count)
        return count_annotation

    def calc_yspacing(self, ys):
        """Calculates vertical spacing for annotations to avoid overlap."""
        lastys = self.df[ys].iloc[-1]
        lastys = lastys.to_frame('lasty')
        lastys = lastys.sort_values(by=['lasty'], ascending=True)
        lastys['ypad'] = 0
    
        padmultiplier = 1
        # Set remaining two paddings
        for i in range(1, len(ys)):
            valuedistance = lastys.iloc[i]['lasty'] - lastys.iloc[i - 1]['lasty']
            # Add padding if values are too close
            if valuedistance < 250000:
                lastys.at[lastys.iloc[i].name, 'ypad'] = 15 * padmultiplier
                padmultiplier += 1
            else:
                padmultiplier = 1
        return lastys

    def multi_yoy_annotate(self, ys, key, annotation_fxn, x='month', xpad=0, dynamic_spacing = 10):
        """Annotates multiple series in a plot with year-over-year changes or final counts."""
        lastys = self.calc_yspacing(ys)
        for i in range(len(ys)):
            y = lastys.iloc[i].name
            self.annotate(x=x,
                          y=y,
                          num_annotation=annotation_fxn(y=y),
                          legend_label=key.loc[y, 'labelname'],
                          label_color=key.loc[y, 'color'],
                          xpad=xpad,
                          ypad=lastys.iloc[i].ypad,
                          dynamic_spacing=dynamic_spacing)

    def top_annotation(self, x=0.05, y=0.87, annotation_text=""):
        """Adds a custom annotation at the top of the chart under the title."""
        plt.figtext(x, y, annotation_text, family=style_parameters['font'], fontsize=10, color=wmf_colors['black75'])

    def add_legend(self, legend_fontsize=14):
        """Adds a legend to the plot with custom formatting."""
        matplotlib.rcParams['legend.fontsize'] = legend_fontsize
        plt.legend(frameon=False,
                   loc="upper center",
                   bbox_to_anchor=(0.5, -0.15,),
                   fancybox=False,
                   shadow=False,
                   ncol=4,
                   prop={"family": style_parameters['font']})

    def add_block_legend(self):
        """Adds a blocked out area to the legend."""
        self.fig.patches.extend([plt.Rectangle((0.05, 0.868), 0.01, 0.02,
                                               linewidth=0.1,  
                                               hatch='//////',
                                               edgecolor='black', 
                                               facecolor='white',  
                                               zorder=100,
                                               transform=self.fig.transFigure,
                                               figure=self.fig)])

    def finalize_plot(self, save_file_name, display=True):
        """Saves plot to a file according to specified parameters and displays it"""
        save_path = save_directory + save_file_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        if display:
            plt.show()

    def plot_subplots_lines(self, x, key, linewidth=2, num_charts=4, subplot_title_size=12):
        """Plots lines on multiple subplots within the figure."""
        i = 0
        for row in self.ax:
            for axis in row:
                if i < num_charts:
                    region_label = key.iloc[i]['labelname']
                    region_color = key.iloc[i]['color']
                    axis.plot(self.df['month'],
                              self.df[region_label],
                              label='_no_legend_,',
                              color=region_color,
                              zorder=3,
                              linewidth=linewidth)
                    axis.set_title(region_label, fontfamily=style_parameters['font'], fontsize=subplot_title_size)
                i += 1

    def plot_multi_trendlines(self, x, key, linewidth=1, num_charts=4):
        """Plots trend lines on multiple subplots within the figure."""
        x_num = dates.date2num(self.df[x])
        i = 0
        for row in self.ax:
            for axis in row:
                if i < num_charts:
                    y_label = key.iloc[i]['labelname']
                    z = np.polyfit(x_num, self.df[y_label], 1)
                    p = np.poly1d(z)
                    axis.plot(x_num,
                              p(x_num),
                              label='_no_legend_,',
                              color='black',
                              zorder=4,
                              linewidth=linewidth)
                i += 1

    def block_off_multi(self, blockstart, blockend, xbuffer=6):
        """Blocks off a set of dates on multiple subplots within the figure."""
        for row in self.ax:
            for axis in row:
                # Convert dates to x axis coordinates
                xstart = mdates.date2num(blockstart)
                xend = mdates.date2num(blockend)
                block_width = xend - xstart
                ymin, ymax = axis.get_ylim()
                block_height = ymax - ymin
                rect = Rectangle((xstart - xbuffer, ymin), block_width + 2 * xbuffer, block_height,
                                 linewidth=0, 
                                 hatch='////',
                                 edgecolor=wmf_colors['black75'], 
                                 facecolor='white', 
                                 zorder=10)
                axis.add_patch(rect)

    def get_maxyrange(self):
        """Returns the maximum y-range and number of ticks from the subplots."""
        for row in self.ax:
            for axis in row:
                # Note that the axis limits are not necessarily the range displayed by the min and max ticks
                # the axis limits might slightly wider than the min-max tick range — we use the min max tick range to ensure congruity between charts
                 
                # Gets the tick range    
                ticks = axis.get_yticklabels()
                tick_range = ticks[-1].get_position()[1] - ticks[0].get_position()[1]
                self.yranges.append(tick_range)
                self.ynumticks.append(len(ticks))
        maxrange = max(self.yranges)
        maxrange_index = self.yranges.index(maxrange)
        maxrange_numticks = self.ynumticks[maxrange_index]
        return maxrange, maxrange_numticks

    def format_subplots(self, title, key, author=author, data_source="N/A", radjust=0.85, ladjust=0.1, tadjust=0.85, badjust=0.1, num_charts=4, tickfontsize=12, mo_in_title=True):
        """Applies formatting across multiple subplots within the figure."""
        plt.subplots_adjust(bottom=badjust, right=radjust, left=ladjust, top=tadjust, wspace=0.2, hspace=0.4)
        i = 0
        for row in self.ax:
            for axis in row:
                if i < num_charts:
                    axis.set_frame_on(False)
                    axis.grid(axis='y', 
                              zorder=-1, 
                              color=wmf_colors['black25'], 
                              linewidth=0.25)
                    axis.set_xticklabels(axis.get_xticklabels(), 
                                         fontfamily=style_parameters['font'], 
                                         fontsize=tickfontsize)
                    
                    # Format x axis labels to show year only.
                    axis.xaxis.set_major_locator(mdates.YearLocator(month=1))
                    xaxisFormatter = mdates.DateFormatter('%Y')
                    axis.xaxis.set_major_formatter(xaxisFormatter)
                    current_values = axis.get_yticklabels()
                    new_labels = []
                    
                    # Format y labels in abbreviated notation.
                    for y_label in current_values:
                        y_value = float(y_label.get_position()[1])
                        new_label = simple_num_format(y_value)
                        new_labels.append(new_label)
                    axis.set_yticklabels(new_labels, fontfamily=style_parameters['font'], fontsize=tickfontsize)
                else:
                    axis.set_visible(False)
                i += 1
                
        # Add title and axis labels
        if mo_in_title:
            figure_title = f'{title} ({calendar.month_name[self.month_interest]})'
        else:
            figure_title = f'{title}'
            
        self.fig.suptitle(figure_title, ha='left', 
                          x=0.05,
                          y=0.97, 
                          fontsize=style_parameters['title_font_size'], 
                          fontproperties={'family': style_parameters['font'], 
                                          'weight': 'bold'})
        plt.figtext(
            0.05, 0.01,
            f"Graph Notes: Created by {author} on {date.today()} using data from {data_source}",
            fontsize=8, va="bottom", ha="left",
            color=wmf_colors['black25'],
            fontproperties={'family': style_parameters['font']}
        )
        
    def clean_ylabels_subplots(self, tickfontsize=12):
        """Cleans up the y-labels on multiple subplots, showing only the top and bottom labels in bold."""
        i = 0
        for row in self.ax:
            for axis in row:
                current_labels = axis.get_yticklabels()
                new_labels = [''] * len(current_labels)
                new_labels[0] = current_labels[0]
                new_labels[-1] = current_labels[-1]
                axis.set_yticklabels(new_labels, fontfamily=style_parameters['font'], fontsize=tickfontsize, weight='bold')
                i += 1

    def standardize_subplotyaxis(self, ymin, ymax, num_charts=4):
        """Sets the same y-axis limits for all subplots within the figure."""
        i = 0
        for row in self.ax:
            for axis in row:
                if i < num_charts:
                    axis.set_ylim([ymin, ymax])
                i += 1

    def standardize_yrange(self, yrange, num_ticks, std_cutoff=15):
        """Sets the y-axis range for a single plot based on the standard number of ticks and a cutoff for very small ranges."""
        std_yinterval = yrange / (num_ticks - 1)
        ax = plt.gca()
        current_ymin, current_ymax = ax.get_ylim()
        current_yrange = current_ymax - current_ymin
        if current_yrange > (yrange / std_cutoff):
            current_ymedian = current_ymin + ((current_ymax - current_ymin) / 2)
            if (num_ticks % 2) == 0:
                new_ymedian = closestdivisible(current_ymedian, std_yinterval)
                if new_ymedian < current_ymedian:
                    new_ymin = new_ymedian - (std_yinterval * (num_ticks / 2 - 1))
                else:
                    new_ymin = new_ymedian - (std_yinterval * (num_ticks / 2))
            else:
                new_ymedian = closestdivisible(current_ymedian, std_yinterval)
                new_ymin = new_ymedian - (yrange / 2)
            new_ymin = max(0, new_ymin)
            new_ymax = new_ymin + yrange
            ax.set_ylim(new_ymin, new_ymax)

    def standardize_subplotyrange(self, yrange, num_ticks, num_charts=4, std_cutoff=15):
        """Standardizes the y-axis range across multiple subplots within the figure based on a standard number of ticks and a cutoff for very small ranges."""
        std_yinterval = yrange / (num_ticks - 1)
        i = 0
        for row in self.ax:
            for axis in row:
                if i < num_charts:
                    current_ymin, current_ymax = axis.get_ylim()
                    current_yrange = current_ymax - current_ymin
                    if current_yrange > (yrange / std_cutoff):
                        current_ymedian = current_ymin + ((current_ymax - current_ymin) / 2)
                        if (num_ticks % 2) == 0:
                            new_ymedian = closestdivisible(current_ymedian, std_yinterval)
                            if new_ymedian < current_ymedian:
                                new_ymin = new_ymedian - (std_yinterval * (num_ticks / 2 - 1))
                            else:
                                new_ymin = new_ymedian - (std_yinterval * (num_ticks / 2))
                        else:
                            new_ymedian = closestdivisible(current_ymedian, std_yinterval)
                            new_ymin = new_ymedian - (yrange / 2)
                        new_ymin = max(0, new_ymin)
                        new_ymax = new_ymin + yrange
                        axis.set_ylim(new_ymin, new_ymax)
                i += 1

    def get_ytickrange(self):
        """Returns the range of y-ticks for the current axis."""
        ticks = self.ax.get_yticklabels()
        tick_range = ticks[-1].get_position()[1] - ticks[0].get_position()[1]
        return tick_range
