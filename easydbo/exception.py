class EASYDBO_GOTO_LOOP(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        if not self.message:
            return ''
        if isinstance(self.message, str):
            ms = self.message.split('\n')
        ms[0] = f'[ERROR] {ms[0]}'
        for i in range(1, len(ms)):
            ms[i] = ' ' * 8 + ms[i]
        return '\n'.join(ms)

class EASYDBO_USER_ERROR(Exception):
    pass
