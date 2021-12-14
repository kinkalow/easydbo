class EASYDBO_GOTO_LOOP(Exception):
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        if not self.value:
            return ''
        return f'[ERROR] {self.value}'
