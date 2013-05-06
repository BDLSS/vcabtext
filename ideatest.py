# This file is used to test ideas.

from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles

def get_styles():
    # Grab all the possible styles
    # The idea of this came from a website, link lost.
    styles = list(get_all_styles())
    
    print("\nAll built in styles for Pygments: ")
    for style in styles:
        print('- ' + style)
    
    # Enter name of style from the above list.
    pick_style = raw_input('\nEnter name of chosen style: ')
    
    # Check user input is a valid style
    while pick_style not in styles:
        print('A Style with that name does not exist. Please try again.')
        pick_style = raw_input('\nEnter name of chosen style: ')       
    else:
        # If valid then create the CSS file
        
        style = HtmlFormatter(style=pick_style).get_style_defs('.highlight')
        print style
        
        print('Style successfully generated.')
        
        
get_styles()