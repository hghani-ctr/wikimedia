from .wikicharts import Wikichart
import matplotlib.pyplot as plt
import pandas as pd
from .config import wmf_colors
from datetime import datetime

def main():
    print("Generating Pageview Referrals chart...")

    #---PARAMETERS---
    save_file_name = "Pageviews_Referral.png"
    display_flag = True

    #---CLEAN DATA--
    df = pd.read_csv('wikicharts/resources/data/referral_source.tsv', 
                     sep='\t')
    df.rename(columns={
    'corrected_pv_internal': 'internal',
    'corrected_pv_none': 'none',
    'corrected_pv_external (search engine)': 'external'
    }, inplace=True)
    
    df['month'] = pd.to_datetime(df['month'])
    df.sort_values(by='month')
        
    start_date = "2021-07-01"
    end_date = datetime.today()
    
    df = df[['month', 'internal', 'none', 'external']]
    
    df['internal'] = df['internal'].replace(',', '', regex=True).astype(float).fillna(0).astype(int)
    df['none'] = df['none'].replace(',', '', regex=True).astype(float).fillna(0).astype(int)
    df['external'] = df['external'].replace(',', '', regex=True).astype(float).fillna(0).astype(int)
 
    df = df[df["month"].isin(pd.date_range(start_date, end_date))]

    #---PREPARE TO PLOT
    key = pd.DataFrame([['External (search engine)',wmf_colors['purple']],
        ['Internal',wmf_colors['green']],
        ['None',wmf_colors['orange']]],
        index=['external','internal','none'],
        columns=['labelname','color'])
 
    #---MAKE CHART---
    chart = Wikichart(start_date,
                      end_date,
                      df,
                      time_col='month')
    
    chart.init_plot(width=15,
                    height=7)
    
    plt.plot(df.month, 
             df.external, 
             label='_nolegend_', 
             color=key.loc['external','color'],
             linewidth=2,
             zorder=8)
    
    plt.plot(df.month, 
             df.internal, 
             label='_nolegend_', 
             color=key.loc['internal','color'],
             linewidth=2,
             zorder=8)
    
    plt.plot(df.month, 
             df.none, 
             label='_nolegend_', 
             color=key.loc['none','color'],
             linewidth=2,
             zorder=8)
   
    chart.format(title = 'Pageviews by Referral Source',
        data_source="https://docs.google.com/spreadsheets/d/1Aw5kjj47cEi-PSX0eApCUp3Ww9_XNyARxcdoL9QnHp4",
        ybuffer=True,
        format_x_yearly=True,
        badjust=0.275, ladjust=0.1, radjust=0.85,
        titlepad=20)
    
    plt.xlabel("Year",
               font='Montserrat', 
               fontsize=18, 
               labelpad=10) 
    
    plt.ylabel("Pageviews",
               font='Montserrat', 
               fontsize=18,
               labelpad=10)
    
    chart.multi_yoy_annotate(['external','internal','none'],key,chart.calc_yoy, xpad=0)
    
    chart.plot_monthlyscatter('month','external',
                              key.loc['external','color'])
    
    chart.plot_monthlyscatter('month','internal',
                              key.loc['internal','color'])
    
    chart.plot_monthlyscatter('month','none',
                              key.loc['none','color'])
    
    plt.figtext(0.5, 0.09, "Data between July 2021 and January 2022 corrected for data loss.", 
                fontsize=14, 
                family='Montserrat',
                color= wmf_colors['black25'],
                horizontalalignment='center')
    
    chart.finalize_plot(save_file_name,display=display_flag)

if __name__ == "__main__":
    main()