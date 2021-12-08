import PySimpleGUI as sg

class Attribution:
    color_safety = '#22348c'
    color_warning = '#b0ac2e'
    color_danger = '#e83838'

    base_button = {'font': ('', 12)}
    base_checkbox = {'font': ('', 12)}
    base_inputtext = {'font': ('', 12)}
    base_multiline = {'font': ('', 12)}
    base_text = {'font': ('', 12)}
    base_table = {'font': ('', 12), 'selected_row_colors': 'red on yellow',
                  'justification': 'right', 'auto_size_columns': False}

    base_button_with_color_safety = {**base_button, 'button_color': color_safety}
    base_button_with_color_warning = {**base_button, 'button_color': color_warning}
    base_button_with_color_danger = {**base_button, 'button_color': color_danger}

    base_text_with_size = {**base_text, 'size': (20, 1)}
    base_inputtext_with_size = {**base_text, 'size': (20, 1)}

    text_table = {'font': ('', 13), 'text_color': '#ffffff',
                  'background_color': '#85b005', 'border_width': 5,
                  'relief': sg.RELIEF_RAISED, 'justification': 'center'}
