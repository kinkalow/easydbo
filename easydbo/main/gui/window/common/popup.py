import PySimpleGUI as sg
from easydbo.exception import EASYDBO_GOTO_LOOP

def popup(message, location):
    sg.Window('', layout=[[sg.Text(message, background_color='red', text_color='black')]], default_element_size=None,
              default_button_element_size=(None, None),
              auto_size_text=None, auto_size_buttons=None, location=location, relative_location=(None, None), size=(None, None),
              element_padding=None, margins=(0, 0), button_color=None, font=12,
              progress_bar_color=(None, None), background_color='red', border_depth=0, auto_close=True,
              auto_close_duration=1, icon=None, force_toplevel=False,
              alpha_channel=1, return_keyboard_events=False, use_default_focus=False, text_justification=None,
              no_titlebar=True, grab_anywhere=False, grab_anywhere_using_control=True, keep_on_top=True, resizable=True, disable_close=False,
              disable_minimize=False, right_click_menu=None, transparent_color=None, debugger_enabled=True,
              right_click_menu_background_color=None, right_click_menu_text_color=None, right_click_menu_disabled_text_color=None,
              right_click_menu_selected_colors=(None, None),
              right_click_menu_font=None, right_click_menu_tearoff=False,
              finalize=False, element_justification='left', ttk_theme=None, use_ttk_buttons=None, modal=False, enable_close_attempted_event=False,
              titlebar_background_color=None, titlebar_text_color=None, titlebar_font=None, titlebar_icon=None,
              use_custom_titlebar=None, scaling=None, metadata=None) \
    .read(timeout=0)

def popup_error(message, location):
    popup(f'[Error] {message}', location)
    raise EASYDBO_GOTO_LOOP('')
