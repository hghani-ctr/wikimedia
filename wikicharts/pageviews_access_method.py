from .wikicharts import Wikichart
import matplotlib.pyplot as plt
import pandas as pd
from .config import wmf_colors
from datetime import datetime


from .parameters import readers_data_path

def main():
    print("Generating Pageviews Access Method chart...")
    print("Note that even if annotation looks incorrect or cut off in jupyter notebook, the image saved in the charts folder may still be correct")

    #---PARAMETERS---
    save_file_name = "Pageviews_Access_Method.png"

    #---CLEAN DATA--
    df = pd.read_csv(readers_data_path, sep='\t')
    
    df = df[['month','desktop', 'mobileweb']]
    df = df.rename(columns={'mobileweb':'mobile_web', 'month':'timestamp'})
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    start_date = "2022-02-01"
    end_date = datetime.today()
    
    df.sort_values(by='timestamp')
    df = df[df["timestamp"].isin(pd.date_range(start_date, end_date))]
    

    #---PLOT---
    
    chart = Wikichart(start_date,end_date,df,time_col='timestamp')
    chart.init_plot()
    
    plt.plot(df.timestamp, 
             df.desktop,label='_nolegend_',
             color=wmf_colors['brightgreen'])
    
    plt.plot(df.timestamp, 
             df.mobile_web,
             label='_nolegend_',
             color=wmf_colors['pink'])
    
    plt.scatter(df.timestamp, 
                df.desktop,
                label='_nolegend_',
                color=wmf_colors['brightgreen'])
    
    plt.scatter(df.timestamp, 
                df.mobile_web,
                label='_nolegend_',
                color=wmf_colors['pink'])
    
    chart.format(title = f'Pageviews by Access Method',
        radjust=0.85,
        badjust=0.2,
        ladjust=0.1,
        data_source="https://docs.google.com/spreadsheets/d/1Aw5kjj47cEi-PSX0eApCUp3Ww9_XNyARxcdoL9QnHp4")
    
    plt.xlabel("",font='Montserrat', fontsize=18, labelpad=10)
    plt.ylabel("Pageviews",font='Montserrat', fontsize=18,labelpad=10)
    
    chart.annotate(x='timestamp',
        y='desktop',
        legend_label="Desktop",
        num_color=wmf_colors['brightgreen'],
        num_annotation=chart.calc_finalcount(y='desktop',
                                             yoy_note=''))
    
    chart.annotate(x='timestamp',
        y='mobile_web',
        legend_label="Mobile",
        num_color=wmf_colors['pink'],
        num_annotation=chart.calc_finalcount(y='mobile_web',
                                             yoy_note=''))
    
    chart.finalize_plot(save_file_name,
                        display=True)

if __name__ == "__main__":
    main()