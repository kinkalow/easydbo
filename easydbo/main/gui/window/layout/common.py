import PySimpleGUI as sg

class Attribution:
    color_safety = '#22348c'
    color_warning = '#b0ac2e'
    color_danger = '#e83838'

    base_button = {'font': ('', 12)}
    base_checkbox = {'font': ('', 12)}
    base_inputtext = {'font': ('', 12)}
    base_text = {'font': ('', 12)}
    base_table = {'font': ('', 12)}

    base_button_with_color_safety = {**base_button, 'button_color': color_safety}
    base_button_with_color_warning = {**base_button, 'button_color': color_warning}
    base_button_with_color_danger = {**base_button, 'button_color': color_danger}

    text_table = {'font': ('', 13), 'text_color': '#ffffff',
                  'background_color': '#85b005', 'border_width': 5,
                  'relief': sg.RELIEF_RAISED, 'justification': 'center'}
