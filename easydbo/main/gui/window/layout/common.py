import PySimpleGUI as sg

class Attribution:
    base_button = {'font': ('', 12)}
    base_checkbox = {'font': ('', 12)}
    base_inputtext = {'font': ('', 12)}
    base_text = {'font': ('', 12)}

    color_safe = '#3d3dd4'
    color_warning = '#b0ac2e'
    color_danger = '#e83838'

    text_table = {'font': ('', 13), 'text_color': '#ffffff',
                  'background_color': '#85b005', 'border_width': 5,
                  'relief': sg.RELIEF_RAISED, 'justification': 'center'}
