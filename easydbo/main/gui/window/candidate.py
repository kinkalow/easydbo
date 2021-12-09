import re
import PySimpleGUI as sg
from .base import BaseWindow
from .layout.common import Attribution as attr

class CandidateWindow(BaseWindow):
    def __init__(self, data, util, parent_element, location):
        super().__init__(util.winmgr)

        self.data = sorted(set([str(d) for d in data]))
        self.data = [[d] for d in sorted(set([str(d) for d in data]))]
        self.parent_element = parent_element
        self.num_buttons = min([30, len(self.data)])

        prefkey = util.make_timestamp_prefix('candidate')
        self.key_input = f'{prefkey}input'
        self.key_numbercandidate = f'{prefkey}numbercandidate'
        self.key_cancel = f'{prefkey}cancel'
        self.key_table = f'{prefkey}table'
        #
        self.key_input_return = f'{self.key_input}.return'  # bind

        table_attr = attr.base_table.copy()
        table_attr.pop('font')
        layout = [
            [
                sg.InputText('', **attr.base_inputtext_with_size, key=self.key_input, enable_events=True),
                sg.Text(f'{len(self.data)} / {len(self.data)}', **attr.base_text_with_size, key=self.key_numbercandidate),
                sg.Button('Cancel', **attr.base_button_with_color_safety, key=self.key_cancel),
            ]
        ] + [
            [
                sg.Table(self.data, **table_attr, font=('', 14), key=self.key_table, headings=[''], enable_click_events=True, expand_x=True, expand_y=True, justification='left', num_rows=self.num_buttons, header_background_color=sg.DEFAULT_BACKGROUND_COLOR)
            ]
        ]

        self.window = sg.Window(
            'EasyDBO Candidate',
            layout,
            size=(1300, 800),
            resizable=True,
            finalize=True,
            no_titlebar=True,
            location=location,
        )

        self.window[self.key_input].bind('<Return>', f'.{self.key_input_return.split(".")[-1]}')

    def handle(self, event, values):
        if event == self.key_input:
            self.find_candidate(values[self.key_input])
        elif (isinstance(event, tuple) and event[0:2] == (self.key_table, '+CICKED+')):  # On table
            row = event[2][0]
            if row is None or row == -1:  # Header line
                return
            self.notify(row)
        elif event == self.key_input_return:
            self.notify(0)
        elif event == self.key_cancel:
            self.close()

    def find_candidate(self, pattern=''):
        candidates = [[d[0]] for d in self.data if re.search(pattern, d[0])] if pattern else self.data
        self.window[self.key_table].update(candidates)
        num_candidates = len(candidates)
        self.window[self.key_numbercandidate].update(f'{num_candidates} / {len(self.data)}')

    def notify(self, row):
        candidate = self.window[self.key_table].get()[row][0]
        self.parent_element.update(candidate)
        self.close()
