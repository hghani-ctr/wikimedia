from .wikicharts import Wikichart
import pandas as pd
from .config import wmf_colors
from datetime import datetime
import matplotlib.pyplot as plt

from .parameters import content_gap_data_path


def main():
    print("Generating region chart..")
    
    #---PARAMETERS---
    save_file_name = "Underrepresented Region Growth.png"
    
    #---CLEAN DATA--
    df = pd.read_csv(content_gap_data_path, sep='\t')
    
    start_date = '2022-01'
    end_date = datetime.today()
    df['month'] = pd.to_datetime(df['month'])
    df = df[df["month"].isin(pd.date_range(start_date, end_date))]

    #---MAKE CHART---
    df['timestamp'] = pd.to_datetime(df['month'], format='%Y-%m')
    chart = Wikichart(start_date, end_date, df, time_col='month')
    chart.init_plot()
    chart.plot_line('month', '%_of_new_articles_about_underrepresented_regions', 
                    wmf_colors['blue'])
    
    plt.scatter(df['month'], df['%_of_new_articles_about_underrepresented_regions'], 
                color=wmf_colors['blue'], zorder=5)
  
    chart.format(title='Articles about underrepresented regions', 
                 data_source="the Knowledge Gap Index",
                 titlepad=15,
                perc=True)
    
    chart.annotate(x='month',
            y='%_of_new_articles_about_underrepresented_regions',
            use_last_y=True,
            perc = True)
    chart.finalize_plot(save_file_name)

if __name__ == "__main__":
    main()






