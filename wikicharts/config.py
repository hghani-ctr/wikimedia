from matplotlib import font_manager


# Font setup
font_dirs = ["wikicharts/resources/fonts/"]
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
for font_file in font_files:
    font_manager.fontManager.addfont(font_file)


wmf_colors = {
    'black75': '#404040',
    'black50': '#7F7F7F',
    'black25': '#BFBFBF',
    'base80': '#eaecf0',
    'orange': '#EE8019',
    'base70': '#c8ccd1',
    'red': '#970302',
    'pink': '#E679A6',
    'green50': '#00af89',
    'purple': '#5748B5',
    'blue': '#0E65C0',
    'brightblue': '#049DFF',
    'brightbluelight': '#C0E6FF',
    'yellow': '#F0BC00',
    'green': '#308557',
    'brightgreen': '#71D1B3'
}

style_parameters = {
    'font': 'Montserrat',
    'title_font_size': 24,
    'text_font_size': 14
}


wmf_regions = [
    "Northern & Western Europe",
    "North America",
    "East, Southeast Asia, & Pacific",
    "Central & Eastern Europe & Central Asia",
    "Latin America & Caribbean",
    "Middle East & North Africa",
    "South Asia",
    "Sub-Saharan Africa"
]


key_colors = [
    wmf_colors['red'], 
    wmf_colors['orange'], 
    wmf_colors['yellow'], 
    wmf_colors['green'], 
    wmf_colors['purple'], 
    wmf_colors['blue'], 
    wmf_colors['pink'], 
    wmf_colors['black50'], 
    wmf_colors['brightblue'],
    wmf_colors['red']
]
