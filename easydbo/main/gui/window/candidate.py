import PySimpleGUI as sg
from .base import BaseWindow
from .layout.common import Attribution as attr
import re

class CandidateWindow(BaseWindow):
    def __init__(self, data, util, parent_element, parent_loc):
        self.data = sorted(set([str(d) for d in data]))
        self.parent_element = parent_element
        self.num_buttons = min([30, len(self.data)])

        prefkey = util.make_timestamp_prefix('candidate')
        self.key_input = f'{prefkey}input'
        self.key_numbercandidate = f'{prefkey}'
        self.key_candidate_buttons = [f'{prefkey}button.{i}' for i in range(self.num_buttons)]
        #
        self.key_input_return = f'{self.key_input}.return'  # bind

        layout = [
            [
                sg.InputText('', **attr.base_inputtext_with_size, key=self.key_input, enable_events=True),
                sg.Text(f'{len(self.data)} / {len(self.data)}', **attr.base_text_with_size, key=self.key_numbercandidate),
            ]
        ] + [
            [sg.Button(d, **attr.base_button_with_color_safety, key=k, expand_x=True)]
            for d, k in zip(self.data, self.key_candidate_buttons)
        ]
        #self.key_candidates = f'{prefkey}candidates'
        #[sg.Multiline(self.find_candidates(), **attr.base_multiline, key=self.key_candidates, expand_x=True, expand_y=True)],

        self.window = sg.Window(
            'EasyDBO Candidate',
            layout,
            size=(1200, 500),
            resizable=True,
            finalize=True,
            #no_titlebar=True,
        )
        self.window.move(parent_loc[0], parent_loc[1] + 30)

        self.window[self.key_input].bind('<Return>', f'.{self.key_input_return.split(".")[-1]}')

    def handle(self, event, values):
        if event == self.key_input:
            self.candidate(values[self.key_input])
        elif event in self.key_candidate_buttons:
            candidate = self.window[event].get_text()
            self.notify(candidate)
        elif event == self.key_input_return:
            candidate = values[self.key_input]
            self.notify(candidate)

    #def find_candidates(self, pattern=''):
    #    if pattern:
    #        candidate = ''
    #        for d in self.data:
    #            if re.search(pattern, d):
    #                candidate += f'{d} '
    #        return candidate.rstrip()
    #    else:
    #        return ' '.join(self.data)
    def find_candidates(self, pattern=''):
        if pattern:
            return [d for d in self.data if re.search(pattern, d)]
        else:
            return self.data

    def candidate(self, pattern):
        candidates = self.find_candidates(pattern)
        num_candidates = len(candidates)
        if len(candidates) < self.num_buttons:
            candidates += ['' for _ in range(self.num_buttons - len(candidates))]
        for c, k in zip(candidates, self.key_candidate_buttons):
            self.window[k].update(c)
        self.window[self.key_numbercandidate].update(f'{num_candidates} / {len(self.data)}')

    def notify(self, value):
        self.parent_element.update(value)
        self.close()
