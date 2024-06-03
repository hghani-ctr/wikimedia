from .wikicharts import Wikichart
import pandas as pd
from .config import wmf_colors
from datetime import datetime
import matplotlib.pyplot as plt
from .parameters import editing_data_path


def main():
    print("Generating Active Editors chart...")

    #---PARAMETERS---
    save_file_name = "Active_Editors.png"
    yoy_note = " "
    display_flag = True

    #---CLEAN DATA--
    df = pd.read_csv(editing_data_path, sep='\t')


    start_date = "2019-01-01"
    end_date = datetime.today()
    df['month'] = pd.to_datetime(df['month'])
    df = df[df["month"].isin(pd.date_range(start_date, end_date))]

    #---MAKE CHART---
    chart = Wikichart(start_date,end_date,df)
    chart.init_plot()
    
    chart.plot_line('month','active_editors',wmf_colors['blue'])
    chart.plot_monthlyscatter('month','active_editors',wmf_colors['blue'])
    chart.plot_yoy_highlight('month','active_editors')
    
    chart.format(title = 'Active Editors',
        data_source="https://github.com/wikimedia-research/Editing-movement-metrics")
    
    chart.annotate(x='month',
        y='active_editors',
        num_annotation=chart.calc_yoy(y='active_editors',
                                      yoy_note=yoy_note))
    
    chart.finalize_plot(save_file_name,display=display_flag)

if __name__ == "__main__":
    main()
