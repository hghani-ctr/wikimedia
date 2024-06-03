import re
import math
from math import ceil, floor, log10
import pandas as pd
from dateutil.relativedelta import relativedelta
import shapely


def simple_num_format(value, round_sigfigs=False, sig=2, perc=False, sign=False):
    """Formats number for labels. Handles rounding, percentage formatting, and prefixes for large numbers."""
    if round_sigfigs:
        value = round(value, sig - int(floor(log10(abs(value)))) - 1)
        
    if perc:
        label = "{:.0%}".format(value)
        return label
    
    if value == 0:
        order = 1
    else:
        order = math.floor(math.log10(abs(value)))
    if order >= 3:
        formatting = '{:1.2f}'
    else:
        formatting = '{:1.0f}'
    
    # Get the order label
    if order >= 12:
        multiplier = float('1e-12')
        formatting = formatting + 'T'
    elif order >= 9:
        multiplier = float('1e-9')
        formatting = formatting + 'B'
    elif order >= 6:
        multiplier = float('1e-6')
        formatting = formatting + 'M'
    elif order >= 3:
        multiplier = float('1e-3')
        formatting = formatting + 'K'
    else:
        multiplier = 1
        
    formatted_value = formatting.format(value * multiplier)
    tail_dot_rgx = re.compile(r'(?:(\.)|(\.\d*?[1-9]\d*?))0+(?=\b|[^0-9])')
    label = tail_dot_rgx.sub(r'\2', formatted_value)
    if sign and value > 0:
        label = "+" + label
    return label

def split_df_by_col(df, index_column_name = "month", cols_per_df = 4):
    """Splits a DataFrame into multiple DataFrames, each with up to four columns plus an index column for use in plotting."""
    num_charts = len(df.columns) - 1
    num_figures = ceil(num_charts / cols_per_df)
    df = df.set_index('month')
    dfs = []
    for f in range(num_figures):
        col_start = f * cols_per_df
        col_end = min(col_start + cols_per_df, num_charts + 1)
        cols = list(range(col_start, col_end))
        cols = list(set(list(cols)))
        new_df = df.iloc[:, cols]
        dfs.append(new_df)
    return dfs

def format_perc(x, sig=2, sign=True):
    """Formats a number as a percentage with optional sign prefix."""
    if sign:
        rounded = "{0:+.2g}".format(round(x, sig-int(floor(log10(abs(x))))-1))
        return rounded + "%"
    else:
        rounded = "{0:.2g}".format(round(x, sig-int(floor(log10(abs(x))))-1))
        return rounded + "%"

def gen_keys(dfs, key_colors, index_column_name = "month"):
    """Generates a list of DataFrames, each representing a key for a subplot with column labels and colors."""
    keys = []
    num_colors = len(key_colors)
    c = 0
    for subdf in dfs:
        variables = list(subdf.columns)
        variables.remove("month")
        new_key_values = []
        for col in variables:
            if c == 0:
                new_key_values.append([col, key_colors[c]])
            else:
                new_key_values.append([col, key_colors[(c % num_colors)]])
            c += 1
        new_key = pd.DataFrame(new_key_values, index=variables, columns=['labelname','color'])
        keys.append(new_key)
    return keys

def closestdivisible(n, m):
    """Finds the number closest to 'n' that is divisible by 'm'."""
    q = int(n / m)
    n1 = m * q
    if((n * m) > 0) :
        n2 = (m * (q + 1))
    else :
        n2 = (m * (q - 1))
    if (abs(n - n1) < abs(n - n2)) :
        return n1
    return n2

def roll(df, rolling_months = 3, index_column_name = "month"):
    """Returns a DataFrame with a rolling average calculation over the specified number of months."""
    rolled = df.set_index(index_column_name).rolling(rolling_months).mean().reset_index().dropna()
    return rolled

def round_to_nearest(x, base=1000):
    """Rounds to the nearest 1000."""
    return base * round(x / base)

def change_over_time(var, change_var_name, data_df, region_table_local, days_delta=0, months_delta=0, years_delta=0):
    """Calculates the change over time for a given variable."""
    # Get data for the most recent month
    current_df = data_df.loc[data_df['month'] == data_df.iloc[-1]['month']]
    # Get data for time delta
    prev_time = data_df.iloc[-1]['month'].replace(day=1) - relativedelta(years=years_delta, months=months_delta, days=days_delta)
    prev_df = data_df.loc[data_df['month'] == prev_time]
    # Names and labels
    var_x = var + "_x"
    var_y = var + "_y"
    growth_var_label = change_var_name + "_label"
    # Comparison df
    growth_df = current_df.merge(prev_df, how='left',left_on="region", right_on="region")
    growth_df = growth_df.rename(columns={var_x:"current",var_y:"prev"})
    growth_df = growth_df.drop(columns=['month_x','month_y'])
    growth_df[change_var_name] = (growth_df["current"] - growth_df["prev"]) / growth_df["prev"]
    growth_df[growth_var_label] = (growth_df[change_var_name] * 100).map(format_perc)
    region_table_local = region_table_local.merge(growth_df.drop(columns=["current", "prev"]), how='left', on="region")
    
    return region_table_local


def adjust_label_position(region, region_table, x=0, y=0):
    """Adjusts label positions on a map chart for a given region."""
    current = region_table.at[region, 'centroid']
    region_table.at[region, 'centroid'] = shapely.Point(current.x + x, current.y + y)