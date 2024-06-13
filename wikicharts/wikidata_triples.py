from datetime import date, datetime, timedelta
from .wikicharts import Wikichart
from .config import wmf_colors
import pandas as pd

def main():
    print("Generating Triples Growth chart...")

    #---PARAMETERS---
    outfile_name = "wikidata_triples_growth.png"
    yoy_note = " "
    #display or note
    display_flag = True
    
    home_dir = ''

    #---CLEAN DATA--
    #Data Columns: "month", "total.content", "timeRange.start", "timeRange.end"
    df = pd.read_csv(home_dir + 'wikicharts/resources/data/triples_growth.csv', sep=',')
  
    #note start and end dates may be different depending on chart_type
    start_date = "2022-06-01"
    end_date = datetime.today()
    
    df['month'] = pd.to_datetime(df['month'])
    
    #---PREPARE TO PLOT

    #---PLOT---
    chart = Wikichart(start_date,end_date,df)
    chart.init_plot(width=12)
    chart.plot_line('month','total_triples',col = wmf_colors['brightblue'], linewidth=4)
    chart.format(title = f'Monthly Growth of Wikidata Triples',
        radjust=0.75,
        data_source="Wikidata")
    chart.annotate(x='month', 
                   y='total_triples', 
                   num_annotation=chart.calc_finalcount(y='total_triples'))
    chart.finalize_plot('triples_growth_chart.png',display=display_flag)

if __name__ == "__main__":
    main()
    
    