from .wikicharts import Wikichart
import pandas as pd
from .config import wmf_colors, key_colors
from datetime import datetime
import numpy as np
import warnings
from math import ceil
from .data_utils import gen_keys, round_to_nearest
import os

def main():
    print("Generating Regional Active Editors chart...")

    warnings.filterwarnings("ignore")

    save_file_name_base = "Regional_Active_Editors"
    
    # Get the absolute path to the current module file (module.py)
    
    module_dir = os.path.abspath(os.path.dirname(__file__))
    tsv_file_path = os.path.join(module_dir, 'resources/data/regional_editor_metrics.tsv')

    #---CLEAN DATA--
    df = pd.read_csv(
        tsv_file_path,
        sep='\t',
        parse_dates=["month"],
        index_col="month"
    )
    
    
    start_date = df.index.min()
    end_date = df.index.max()
    col_order = df.iloc[-1].sort_values(ascending=False).index
    
    # gen_keys expects a list of data frames, with no index
    df = df[col_order]
    dfs = [df.reset_index()]

    #---MAKE CHARTS---
    max_charts_per_figure = 8
    fig_counter = 0
    
    
    keys = gen_keys(dfs, key_colors)
    total_num_charts = len(df.columns)
    num_figures = ceil(total_num_charts / max_charts_per_figure)
    figures = [None] * num_figures
    maxranges = [None] * num_figures
    num_ticks = [None] * num_figures
    
   
    for f in range(num_figures):
        fig_counter += 1
        charts_in_figure = len(dfs[f].columns) - 1
        figures[f] = Wikichart(start_date, end_date, dfs[f])
        figures[f].init_plot(width=12, subplotsx=2, subplotsy=4, fignum=f)
        figures[f].plot_subplots_lines('month', keys[f], num_charts=charts_in_figure, subplot_title_size=9)
        figures[f].plot_multi_trendlines('month', keys[f], num_charts=charts_in_figure)

        # Set individual y-axis limits and labels for each subplot
        for i, ax in enumerate(figures[f].ax.flat):
            if i < charts_in_figure:
                region_label = keys[f].iloc[i]['labelname']
                region_data = dfs[f][region_label].dropna()
                ymin = max(0, round_to_nearest(region_data.min()) - 1000)  
                ymax = round_to_nearest(region_data.max()) + 1000  
                ax.set_ylim(ymin, ymax)
                
                ax.set_xlim(start_date, end_date)

                y_ticks = np.arange(ymin, ymax + 1000, 1000)
                y_labels = [f'{int(tick/1000)}k' if tick != 0 else '0' for tick in y_ticks]
                ax.set_yticks(y_ticks)
                ax.set_yticklabels(y_labels)

        figures[f].format_subplots(title='Regional Active Editors',
                                   key=keys[f],
                                   data_source="https://docs.google.com/spreadsheets/d/13XrrnCaz9qsKs5Gu_lUs2jtsK9VrSiGlilCleDgR6KM",
                                   num_charts=charts_in_figure,
                                   tickfontsize=8)
        figures[f].clean_ylabels_subplots(tickfontsize=8)
        save_file_name = save_file_name_base + "_" + 'All' + ".png"
        figures[f].finalize_plot(save_file_name, display=False)
        
    #---GENERATE INDIVIDUAL CHARTS---
    df.reset_index(inplace=True)

    df['month'] = pd.to_datetime(df['month'])

    individual_charts = []
    columns = list(df.columns)

    for current_col in columns:
        if current_col != 'month':  
            current_df = df[['month', current_col]].dropna()
            current_savefile = save_file_name_base + "_" + f'{current_col}' + ".png"
            
            current_df = current_df.sort_values(by='month').drop_duplicates(subset='month', keep='last')
            
            chart = Wikichart(start_date, end_date, current_df)
            chart.init_plot(fignum=len(individual_charts) + 1)
            current_color = key_colors[(columns.index(current_col) % len(key_colors))]
            
            chart.plot_line('month', current_col, col=current_color)
            chart.plot_monthlyscatter('month', current_col, col=current_color)
            chart.plot_yoy_highlight('month', current_col, highlight_radius = 700)
            
            chart.format(
                title=f'Active Editors: {current_col}',
                ybuffer=False,
                data_source="https://docs.google.com/spreadsheets/d/13XrrnCaz9qsKs5Gu_lUs2jtsK9VrSiGlilCleDgR6KM",
                tadjust=0.825, badjust=0.125,
                titlepad=25
            )
            
            chart.annotate(
                x='month',
                y=current_col,
                num_annotation=chart.calc_yoy(y=current_col, yoy_note="")
            )
            
            chart.finalize_plot(current_savefile, display=False)
            individual_charts.append(chart)



if __name__ == "__main__":
    main()

